#!/usr/bin/env python
#
# DFT.py
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA  02111-1307  USA

import types
import operator
import re
import base64
import logging

from urllib.parse import unquote
from urllib.parse import urljoin

import bs4

from bs4.element import NavigableString
from bs4.element import CData
from bs4.element import Script

from cssutils.parse import CSSParser

from thug.ActiveX.ActiveX import _ActiveXObject
from thug.DOM.W3C import w3c
from thug.DOM.AsyncPrefetcher import AsyncPrefetcher

log = logging.getLogger("Thug")


class DFT:
    javascript = ("javascript",)
    vbscript = ("vbs", "vbscript", "visualbasic")

    # Some event types are directed at the browser as a whole, rather than at
    # any particular document element. In JavaScript, handlers for these events
    # are registered on the Window object. In HTML, we place them on the <body>
    # tag, but the browser registers them on the Window. The following is the
    # complete list of such event handlers as defined by the draft HTML5
    # specification:
    #
    # onafterprint      onfocus         ononline        onresize
    # onbeforeprint     onhashchange    onpagehide      onstorage
    # onbeforeunload    onload          onpageshow      onundo
    # onblur            onmessage       onpopstate      onunload
    # onerror           onoffline       onredo
    window_events = (
        "abort",
        "afterprint",
        "beforeprint",
        "beforeunload",
        "blur",
        "error",
        "focus",
        "hashchange",
        "load",
        "message",
        "offline",
        "online",
        "pagehide",
        "pageshow",
        "popstate",
        "redo",
        "resize",
        "storage",
        "undo",
        "unload",
    )

    window_on_events = ["on" + e for e in window_events]

    window_storage_events = ("storage",)
    window_on_storage_events = ["on" + e for e in window_storage_events]
    _on_events = window_on_events + window_on_storage_events

    user_detection_events = (
        "mousemove",
        "scroll",
    )
    on_user_detection_events = ["on" + e for e in user_detection_events]

    async_prefetch_tags = ["script", "img"]

    def __init__(self, window, **kwds):
        self.window = window
        self.window.doc.DFT = self
        self.anchors = []
        self.forms = kwds["forms"] if "forms" in kwds else []
        self._context = None
        self.async_prefetcher = AsyncPrefetcher(window)
        log.DFT = self

        self._init_events()
        self._init_pyhooks()

    def _init_events(self):
        self.listeners = []

        # Events are handled in the same order they are inserted in this list
        self.handled_events = ["load", "mousemove"]

        for event in log.ThugOpts.events:
            self.handled_events.append(event)

        self.handled_on_events = ["on" + e for e in self.handled_events]
        self.dispatched_events = set()

    def _init_pyhooks(self):
        hooks = log.PyHooks.get("DFT", None)
        if hooks is None:
            return

        get_method_function = operator.attrgetter("__func__")
        get_method_self = operator.attrgetter("__self__")

        for label, hook in hooks.items():
            name = f"{label}_hook"
            _hook = get_method_function(hook) if get_method_self(hook) else hook
            method = types.MethodType(_hook, DFT)
            setattr(self, name, method)

    @property
    def context(self):
        if self._context is None:
            self._context = self.window.context

        return self._context

    def get_evtObject(self, elem, evtType):
        from thug.DOM.W3C.Events.Event import Event
        from thug.DOM.W3C.Events.MouseEvent import MouseEvent
        from thug.DOM.W3C.Events.HTMLEvent import HTMLEvent

        evtObject = None

        if evtType in MouseEvent.EventTypes:
            evtObject = MouseEvent()

        if evtType in HTMLEvent.EventTypes:
            evtObject = HTMLEvent()

        if evtObject is None:
            return None

        evtObject._target = elem
        evtObject.eventPhase = Event.AT_TARGET
        evtObject.currentTarget = elem
        return evtObject

    # Events handling
    def handle_element_event(self, evt):
        from thug.DOM.W3C.Events.Event import Event

        for elem, eventType, listener, capture in self.listeners:  # pylint:disable=unused-variable
            if getattr(elem, "name", None) is None:  # pragma: no cover
                continue

            if elem.name in ("body",):  # pragma: no cover
                continue

            evtObject = Event()
            evtObject._type = eventType

            if eventType in (evt,):
                if (elem._node, evt) in self.dispatched_events:
                    continue

                self.dispatched_events.add((elem._node, evt))
                elem._node.dispatchEvent(evtObject)

    def handle_window_storage_event(self, onevt, evtObject):
        if onevt in self.handled_on_events:
            handler = getattr(self.window, onevt, None)
            if handler:
                handler(evtObject)

    def run_event_handler(self, handler, evtObject):
        if (
            log.ThugOpts.Personality.isIE()
            and log.ThugOpts.Personality.browserMajorVersion < 9
        ):
            self.window.event = evtObject
            handler()
        else:
            handler.apply(evtObject.currentTarget)

    def handle_window_event(self, onevt):
        if onevt not in self.handled_on_events:
            return  # pragma: no cover

        if onevt not in self.window_on_events:
            return

        if onevt in self.window_on_storage_events:
            return

        handler = getattr(self.window, onevt, None)

        if handler:
            if (self.window, onevt[2:], handler) in self.dispatched_events:
                return

            self.dispatched_events.add((self.window, onevt[2:], handler))

            evtObject = self.get_evtObject(self.window, onevt[2:])
            self.run_event_handler(handler, evtObject)
            return

        with self.context as ctx:
            handler_type = ctx.eval(f"typeof window.{onevt}")
            if handler_type in ("function",):  # pragma: no cover
                handler = ctx.eval(f"window.{onevt}")

                if (self.window, onevt[2:], handler) in self.dispatched_events:
                    return

                handler.call()
                self.dispatched_events.add((self.window, onevt[2:], handler))

    def handle_document_event(self, onevt):
        if onevt not in self.handled_on_events:
            return  # pragma: no cover

        evtObject = self.get_evtObject(self.window.doc, onevt[2:])
        handler = getattr(self.window.doc, onevt, None)
        if handler:
            self.run_event_handler(handler, evtObject)

        if "_listeners" not in self.window.doc.tag.__dict__:
            return  # pragma: no cover

        for (
            eventType,
            listener,
            capture,
        ) in (
            self.window.doc.tag._listeners
        ):  # pragma: no cover,pylint:disable=unused-variable
            if eventType not in (onevt[2:],):
                continue

            if (self.window.doc, onevt[2:], handler) in self.dispatched_events:
                return

            self.dispatched_events.add((self.window.doc, onevt[2:], handler))

            evtObject = self.get_evtObject(self.window.doc, eventType)
            self.run_event_handler(listener, evtObject)

    def _build_event_handler(self, ctx, h):
        # When an event handler is registered by setting an HTML attribute
        # the browser converts the string of JavaScript code into a function.
        # Browsers other than IE construct a function with a single argument
        # named `event'. IE constructs a function that expects no argument.
        # If the identifier `event' is used in such a function, it refers to
        # `window.event'. In either case, HTML event handlers can refer to
        # the event object as `event'.
        if log.ThugOpts.Personality.isIE():
            return ctx.eval(
                f"(function() {{ with(document) {{ with(this.form || {{}}) {{ with(this) {{ event = window.event; {h} }} }} }} }}) "
            )

        return ctx.eval(
            f"(function(event) {{ with(document) {{ with(this.form || {{}}) {{ with(this) {{ {h} }} }} }} }}) "
        )

    def build_event_handler(self, ctx, h):
        try:
            return self._build_event_handler(ctx, h)
        except SyntaxError as e:  # pragma: no cover
            log.info("[SYNTAX ERROR][build_event_handler] %s", str(e))
            return None

    def get_event_handler(self, h):
        handler = None

        if isinstance(h, str):
            handler = self.build_event_handler(self.context, h)
        elif log.JSEngine.isJSFunction(h):
            handler = h
        else:  # pragma: no cover
            try:
                handler = getattr(self.context.locals, h, None)
            except Exception:  # pylint:disable=broad-except
                handler = None

        return handler

    def set_event_handler_attributes(self, elem):
        try:
            attrs = elem.attrs
        except Exception:  # pylint:disable=broad-except
            return

        if "language" in list(attrs.keys()) and attrs["language"].lower() not in (
            "javascript",
        ):
            return

        for evt, h in attrs.items():
            if evt not in self.handled_on_events:
                continue

            self.attach_event(elem, evt, h)

    def attach_event(self, elem, evt, h):
        handler = self.get_event_handler(h)
        if not handler:
            return  # pragma: no cover

        if (
            getattr(elem, "name", None)
            and elem.name in ("body",)
            and evt in self.window_on_events
        ):
            setattr(self.window, evt, handler)
            return

        if not getattr(elem, "_node", None):
            log.DOMImplementation.createHTMLElement(self.window.doc, elem)

        elem._node._attachEvent(evt, handler, True)

    def set_event_listeners(self, elem):
        p = getattr(elem, "_node", None)

        if p:
            for evt in self.handled_on_events:
                h = getattr(p, evt, None)
                if h:
                    self.attach_event(elem, evt, h)

        listeners = getattr(elem, "_listeners", None)
        if listeners:
            for eventType, listener, capture in listeners:
                if eventType in self.handled_events:
                    self.listeners.append((elem, eventType, listener, capture))

    def _handle_onerror(self, tag):
        from thug.DOM.W3C.Events.Event import Event

        if "onerror" not in tag.attrs:
            return

        if log.ThugOpts.Personality.isIE():
            evtObject = Event()
            evtObject._type = "onerror"
            self.window.event = evtObject

        try:
            handler = self.get_event_handler(tag.attrs["onerror"])
            handler.call()
        except Exception as e:  # pylint:disable=broad-except
            log.warning("[ERROR][_handle_onerror] %s", str(e))

    @property
    def javaUserAgent(self):
        javaplugin = log.ThugVulnModules._javaplugin.split(".")
        last = javaplugin.pop()
        version = f"{'.'.join(javaplugin)}_{last}"
        return log.ThugOpts.Personality.javaUserAgent % (version,)

    @property
    def javaWebStartUserAgent(self):
        javaplugin = log.ThugVulnModules._javaplugin.split(".")
        last = javaplugin.pop()
        version = f"{'.'.join(javaplugin)}_{last}"
        return f"JNLP/6.0 javaws/{version} (b04) Java/{version}"

    @property
    def shockwaveFlash(self):
        return ",".join(log.ThugVulnModules.shockwave_flash.split("."))

    def _check_jnlp_param(self, param):
        name = param.attrs["name"]
        value = param.attrs["value"]

        if name in ("__applet_ssv_validated",) and value.lower() in ("true",):
            log.ThugLogging.log_exploit_event(
                self.window.url,
                "Java WebStart",
                "Java Security Warning Bypass (CVE-2013-2423)",
                cve="CVE-2013-2423",
            )

            log.ThugLogging.log_classifier(
                "exploit", log.ThugLogging.url, "CVE-2013-2423"
            )

    def _handle_jnlp(self, data, headers, params):
        try:
            soup = bs4.BeautifulSoup(data, "lxml")
        except Exception as e:  # pragma: no cover,pylint:disable=broad-except
            log.info("[ERROR][_handle_jnlp] %s", str(e))
            return

        jnlp = soup.find("jnlp")
        if jnlp is None:
            return  # pragma: no cover

        codebase = jnlp.attrs["codebase"] if "codebase" in jnlp.attrs else ""

        log.ThugLogging.add_behavior_warn(
            description="[JNLP Detected]", method="Dynamic Analysis"
        )

        for param in soup.find_all("param"):
            log.ThugLogging.add_behavior_warn(
                description=f"[JNLP] {param}", method="Dynamic Analysis"
            )
            self._check_jnlp_param(param)

        jars = soup.find_all("jar")
        if not jars:
            return  # pragma: no cover

        headers["User-Agent"] = self.javaWebStartUserAgent

        for jar in jars:
            try:
                url = f"{codebase}{jar.attrs['href']}"
                self.window._navigator.fetch(
                    url, headers=headers, redirect_type="JNLP", params=params
                )
            except Exception as e:  # pragma: no cover,pylint:disable=broad-except
                log.info("[ERROR][_handle_jnlp] %s", str(e))

    def do_handle_params(self, _object):
        params = {}

        for child in _object.find_all():
            name = getattr(child, "name", None)
            if name is None:
                continue  # pragma: no cover

            if name.lower() in ("param",):
                if all(
                    p in child.attrs
                    for p in (
                        "name",
                        "value",
                    )
                ):
                    params[child.attrs["name"].lower()] = child.attrs["value"]

                    if "type" in child.attrs:
                        params["type"] = child.attrs["type"]

            if name.lower() in ("embed",):
                self.handle_embed(child)

        if not params:
            return params

        hook = getattr(self, "do_handle_params_hook", None)
        if hook:
            hook(params)  # pylint:disable=not-callable

        headers = {}
        headers["Connection"] = "keep-alive"

        if "type" in params:
            headers["Content-Type"] = params["type"]
        else:
            name = getattr(_object, "name", None)

            if name in ("applet",) or "archive" in params:
                headers["Content-Type"] = "application/x-java-archive"

            if "movie" in params:
                headers["x-flash-version"] = self.shockwaveFlash

        if (
            "Content-Type" in headers
            and "java" in headers["Content-Type"]
            and log.ThugOpts.Personality.javaUserAgent
        ):
            headers["User-Agent"] = self.javaUserAgent

        for key in (
            "filename",
            "movie",
        ):
            if key not in params:
                continue

            if log.ThugOpts.features_logging:
                log.ThugLogging.Features.increase_url_count()

            try:
                self.window._navigator.fetch(
                    params[key], headers=headers, redirect_type="params", params=params
                )
            except Exception as e:  # pylint:disable=broad-except
                log.info("[ERROR][do_handle_params] %s", str(e))

        for key, value in params.items():
            if key in (
                "filename",
                "movie",
                "archive",
                "code",
                "codebase",
                "source",
            ):
                continue

            if key.lower() not in ("jnlp_href",) and not value.startswith("http"):
                continue

            if log.ThugOpts.features_logging:
                log.ThugLogging.Features.increase_url_count()

            try:
                response = self.window._navigator.fetch(
                    value, headers=headers, redirect_type="params", params=params
                )

                if response:
                    self._handle_jnlp(response.content, headers, params)
            except Exception as e:  # pylint:disable=broad-except
                log.info("[ERROR][do_handle_params] %s", str(e))

        for p in ("source", "data", "archive"):
            handler = getattr(self, f"do_handle_params_{p}", None)
            if handler:
                handler(params, headers)  # pylint:disable=not-callable

        return params

    def do_params_fetch(self, url, headers, params):
        if log.ThugOpts.features_logging:
            log.ThugLogging.Features.increase_url_count()

        try:
            self.window._navigator.fetch(
                url, headers=headers, redirect_type="params", params=params
            )
        except Exception as e:  # pylint:disable=broad-except
            log.info("[ERROR][do_params_fetch] %s", str(e))

    def do_handle_params_source(self, params, headers):
        if "source" not in params:
            return

        self.do_params_fetch(params["source"], headers, params)

    def do_handle_params_data(self, params, headers):
        if "data" not in params:
            return

        self.do_params_fetch(params["data"], headers, params)

    def do_handle_params_archive(self, params, headers):
        if "archive" not in params:
            return

        if "codebase" in params:
            archive = urljoin(params["codebase"], params["archive"])
        else:
            archive = params["archive"]

        self.do_params_fetch(archive, headers, params)

    def handle_object(self, _object):
        log.warning(_object)

        if log.ThugOpts.features_logging:
            log.ThugLogging.Features.increase_object_count()

        self.check_small_element(_object, "object")

        params = self.do_handle_params(_object)

        classid = _object.get("classid", None)
        _id = _object.get("id", None)
        codebase = _object.get("codebase", None)
        data = _object.get("data", None)

        if codebase:
            if log.ThugOpts.features_logging:
                log.ThugLogging.Features.increase_url_count()

            try:
                self.window._navigator.fetch(
                    codebase, redirect_type="object codebase", params=params
                )
            except Exception as e:  # pragma: no cover,pylint:disable=broad-except
                log.info("[ERROR][handle_object] %s", str(e))

        if data and not log.HTTPSession.is_data_uri(data):
            if log.ThugOpts.features_logging:
                log.ThugLogging.Features.increase_url_count()

            try:
                self.window._navigator.fetch(
                    data, redirect_type="object data", params=params
                )
            except Exception as e:  # pylint:disable=broad-except
                log.info("[ERROR][handle_object] %s", str(e))

        if not log.ThugOpts.Personality.isIE():
            return

        if classid:
            try:
                axo = _ActiveXObject(self.window, classid, "id")
            except TypeError as e:  # pragma: no cover
                log.info("[ERROR][handle_object] %s", str(e))
                return

            if _id is None:
                return

            try:
                setattr(self.window, _id, axo)
                setattr(self.window.doc, _id, axo)
            except TypeError as e:  # pragma: no cover
                log.info("[ERROR][handle_object] %s", str(e))

    def _get_script_for_event_params(self, attr_event):
        result = []
        params = attr_event.split("(")

        if len(params) > 1:
            params = params[1].split(")")[0]
            result = [p for p in params.split(",") if p]

        return result

    def _handle_script_for_event(self, script):
        attr_for = script.get("for", None)
        attr_event = script.get("event", None)

        if not attr_for or not attr_event:
            return

        params = self._get_script_for_event_params(attr_event)

        if "playstatechange" in attr_event.lower() and params:
            with self.context as ctx:
                newState = params.pop()
                ctx.eval(f"{newState.strip()} = 0;")
                try:
                    oldState = params.pop()
                    ctx.eval(f"{oldState.strip()} = 3;")  # pragma: no cover
                except Exception as e:  # pylint:disable=broad-except
                    log.info("[ERROR][_handle_script_for_event] %s", str(e))

    def get_script_handler(self, script):
        language = script.get("language", None)
        if language is None:
            language = script.get("type", None)

        if language is None:
            return getattr(self, "handle_javascript")

        if language.lower() in (
            "jscript.compact",
            "jscript.encode",
        ):
            language = language.lower().replace(".", "_")

        try:
            _language = language.lower().split("/")[-1]
        except Exception:  # pragma: no cover,pylint:disable=broad-except
            log.warning("[SCRIPT] Unhandled script type: %s", language)
            return None

        if _language in ("script",):
            _language = "javascript"  # pragma: no cover

        return getattr(self, f"handle_{_language}", None)

    def handle_jscript_compact(self, script):
        log.ThugLogging.log_classifier(
            "jscript", log.ThugLogging.url, "JScript.Compact"
        )
        self.handle_jscript(script)

    def handle_jscript_encode(self, script):
        from .JScriptEncode import JScriptEncode

        log.ThugLogging.log_classifier("jscript", log.ThugLogging.url, "JScript.Encode")

        decoder = JScriptEncode()
        encoded = script.get_text(types=(NavigableString, CData, Script))
        js = decoder.decode(encoded)

        if not js:
            return

        if log.ThugOpts.code_logging:
            log.ThugLogging.add_code_snippet(js, "Javascript", "Contained_Inside")

        self.increase_script_chars_count("javascript", "inline", js)
        self.check_strings_in_script(js)
        self.window.evalScript(js, tag=script)

        log.ThugLogging.Shellcode.check_shellcodes()
        self.check_anchors()

    def handle_script(self, script):
        handler = self.get_script_handler(script)
        if not handler:
            return

        node = getattr(script, "_node", None)
        self.window.doc._currentScript = node

        if log.ThugOpts.Personality.isIE():
            self._handle_script_for_event(script)

        handler(script)
        self.handle_events(script._soup)

    def handle_external_javascript_text(self, s, response):
        # First attempt
        # Requests will automatically decode content from the server. Most
        # unicode charsets are seamlessly decoded. When you make a request,
        # Requests makes educated guesses about the encoding of the response
        # based on the HTTP headers.
        try:
            s.text = response.text
            return True
        except Exception:  # pragma: no cover,pylint:disable=broad-except
            return self.handle_external_javascript_text_last_attempt(s, response)

    def handle_external_javascript_text_last_attempt(
        self, s, response
    ):  # pragma: no cover
        # Last attempt
        # The encoding will be (hopefully) detected through the Encoding class.
        js = response.content

        enc = log.Encoding.detect(js)
        if enc["encoding"] is None:
            log.warning(
                "[ERROR][handle_external_javascript_text_last attempt] Encoding not detected"
            )
            return False

        try:
            s.text = js.decode(enc["encoding"])
        except Exception as e:  # pylint:disable=broad-except
            log.warning(
                "[ERROR][handle_external_javascript_text_last_attempt] %s", str(e)
            )
            return False

        return True

    def handle_data_javascript(self, script, src):
        data = self._handle_data_uri(src)
        if data is None:
            return  # pragma: no cover

        s = self.window.doc.createElement("script")

        for attr in script.attrs:
            if attr.lower() not in ("src",):
                s.setAttribute(attr, script.get(attr))

        s.text = data.decode() if isinstance(data, bytes) else data

    def handle_external_javascript(self, script):
        src = script.get("src", None)
        if src is None:
            return

        if log.ThugOpts.features_logging:
            log.ThugLogging.Features.increase_url_count()

        if log.HTTPSession.is_data_uri(src):
            self.handle_data_javascript(script, src)
            return

        try:
            response = self.window._navigator.fetch(src, redirect_type="script src")
        except Exception as e:  # pylint:disable=broad-except
            log.info("[ERROR][handle_external_javascript] %s", str(e))
            return

        if response is None or not response.ok or not response.content:
            return  # pragma: no cover

        if log.ThugOpts.code_logging:
            log.ThugLogging.add_code_snippet(response.content, "Javascript", "External")

        self.increase_script_chars_count("javascript", "external", response.text)

        try:
            s = self.window.doc.createElement("script")
        except TypeError:  # pragma: no cover
            self.window.evalScript(response.text, tag=script)
            return

        for attr in script.attrs:
            if attr.lower() not in ("src",) and getattr(s, "setAttribute", None):
                s.setAttribute(attr, script.get(attr))

        self.handle_external_javascript_text(s, response)

    def increase_javascript_count(self, provenance):
        if not log.ThugOpts.features_logging:
            return

        m = getattr(
            log.ThugLogging.Features, f"increase_{provenance}_javascript_count", None
        )
        if m:
            m()

    def increase_script_chars_count(self, type_, provenance, code):
        if not log.ThugOpts.features_logging:
            return

        m = getattr(
            log.ThugLogging.Features, f"add_{provenance}_{type_}_characters_count", None
        )
        if m:
            m(len(code))

        m = getattr(
            log.ThugLogging.Features,
            f"add_{provenance}_{type_}_whitespaces_count",
            None,
        )
        if m:
            m(len([a for a in code if a.isspace()]))

    def check_strings_in_script(self, code):
        if not log.ThugOpts.features_logging:
            return

        for s in ("iframe", "embed", "object", "frame", "form"):
            count = code.count(s)

            if not count:
                continue

            m = getattr(log.ThugLogging.Features, f"add_{s}_string_count", None)
            if m:
                m(count)

    def get_javascript_provenance(self, script):
        src = script.get("src", None)
        return "external" if src else "inline"

    def handle_javascript(self, script):
        log.info(script)

        provenance = self.get_javascript_provenance(script)
        self.handle_external_javascript(script)
        self.increase_javascript_count(provenance)

        js = script.get_text(types=(NavigableString, CData, Script))

        if js:
            if log.ThugOpts.code_logging:
                log.ThugLogging.add_code_snippet(js, "Javascript", "Contained_Inside")

            if provenance in ("inline",):
                self.increase_script_chars_count("javascript", provenance, js)

            self.check_strings_in_script(js)

            # According to HTML specifications "if the src has a URI value, user
            # agents must ignore the element's contents and retrieve the script
            # via the URI" [1]
            #
            # [1] https://www.w3.org/TR/REC-html40/interact/scripts.html#h-18.2.1
            if provenance in ("inline",):
                self.window.evalScript(js, tag=script)

        log.ThugLogging.Shellcode.check_shellcodes()
        self.check_anchors()

    def handle_jscript(self, script):
        self.handle_javascript(script)

    def handle_vbscript(self, script):
        log.info(script)

        if log.ThugOpts.features_logging:
            log.ThugLogging.Features.increase_inline_vbscript_count()

        text = script.get_text(types=(NavigableString, CData, Script))
        self.handle_vbscript_text(text)

    def handle_vbscript_text(self, text):
        log.warning("VBScript parsing not available")

        url = log.ThugLogging.url if log.ThugOpts.local else log.last_url
        self.increase_script_chars_count("vbscript", "inline", text)

        if log.ThugOpts.code_logging:
            log.ThugLogging.add_code_snippet(text, "VBScript", "Contained_Inside")

        try:
            log.ThugLogging.log_file(text, url, sampletype="VBS")
            log.VBSClassifier.classify(url, text)
        except Exception as e:  # pragma: no cover,pylint:disable=broad-except
            log.info("[ERROR][handle_vbscript_text] %s", str(e))

        hook = getattr(self, "do_handle_vbscript_text_hook", None)
        if hook and hook(text):  # pylint:disable=not-callable
            return  # pragma: no cover

        try:
            urls = re.findall(r"(?P<url>https?://[^\s'\"]+)", text)

            for url in urls:
                if log.ThugOpts.features_logging:
                    log.ThugLogging.Features.increase_url_count()

                self.window._navigator.fetch(url, redirect_type="VBS embedded URL")
        except Exception as e:  # pylint:disable=broad-except
            log.info("[ERROR][handle_vbscript_text] %s", str(e))

    def handle_vbs(self, script):
        self.handle_vbscript(script)

    def handle_visualbasic(self, script):
        self.handle_vbscript(script)

    def handle_noscript(self, script):  # pylint:disable=unused-argument
        if log.ThugOpts.features_logging:
            log.ThugLogging.Features.increase_noscript_count()

    def handle_html(self, html):  # pylint:disable=unused-argument
        if log.ThugOpts.features_logging:
            log.ThugLogging.Features.increase_html_count()

    def handle_head(self, head):  # pylint:disable=unused-argument
        if log.ThugOpts.features_logging:
            log.ThugLogging.Features.increase_head_count()

    def handle_title(self, title):  # pylint:disable=unused-argument
        if log.ThugOpts.features_logging:
            log.ThugLogging.Features.increase_title_count()

    def handle_body(self, body):  # pylint:disable=unused-argument
        if log.ThugOpts.features_logging:
            log.ThugLogging.Features.increase_body_count()

    def do_handle_form(self, form):
        log.info(form)

        action = form.get("action", None)
        if action in (
            None,
            "self",
        ):  # pragma: no cover
            last_url = getattr(log, "last_url", None)
            action = last_url if last_url else self.window.url

        if log.ThugOpts.features_logging:
            log.ThugLogging.Features.increase_url_count()

        _action = log.HTTPSession.normalize_url(self.window, action)
        if _action is None:
            return  # pragma: no cover

        if _action not in self.forms:
            self.forms.append(_action)

        method = form.get("method", "get")
        payload = None

        for child in form.find_all():
            name = getattr(child, "name", None)

            if name.lower() in ("input",):
                if payload is None:
                    payload = {}

                if all(
                    p in child.attrs
                    for p in (
                        "name",
                        "value",
                    )
                ):
                    payload[child.attrs["name"]] = child.attrs["value"]

        headers = {}
        headers["Content-Type"] = "application/x-www-form-urlencoded"

        try:
            response = self.window._navigator.fetch(
                action,
                headers=headers,
                method=method.upper(),
                body=payload,
                redirect_type="form",
            )
        except Exception as e:  # pragma: no cover,pylint:disable=broad-except
            log.info("[ERROR][do_handle_form] %s", str(e))
            return

        if response is None or not response.ok:
            return

        if getattr(response, "thug_mimehandler_hit", False):
            return  # pragma: no cover

        window = self.do_window_open(_action, response.content)
        self.run_dft(window, forms=self.forms)

    def handle_param(self, param):
        log.info(param)

    def handle_embed(self, embed):
        log.warning(embed)

        if log.ThugOpts.features_logging:
            log.ThugLogging.Features.increase_embed_count()

        src = embed.get("src", None)
        if src is None:
            src = embed.get("data", None)

        if src is None:
            return

        if log.ThugOpts.features_logging:
            log.ThugLogging.Features.increase_url_count()

        if self._handle_data_uri(src):
            return  # pragma: no cover

        headers = {}

        embed_type = embed.get("type", None)
        if embed_type:
            headers["Content-Type"] = embed_type

        if "Content-Type" in headers:
            if (
                "java" in headers["Content-Type"]
                and log.ThugOpts.Personality.javaUserAgent
            ):
                headers["User-Agent"] = self.javaUserAgent

            if "flash" in headers["Content-Type"]:
                headers["x-flash-version"] = self.shockwaveFlash

        try:
            self.window._navigator.fetch(src, headers=headers, redirect_type="embed")
        except Exception as e:  # pylint:disable=broad-except
            log.info("[ERROR][handle_embed] %s", str(e))

    def handle_applet(self, applet):
        log.warning(applet)

        params = self.do_handle_params(applet)

        archive = applet.get("archive", None)
        if not archive:
            return

        if log.ThugOpts.features_logging:
            log.ThugLogging.Features.increase_url_count()

        headers = {}
        headers["Connection"] = "keep-alive"
        headers["Content-type"] = "application/x-java-archive"

        if log.ThugOpts.Personality.javaUserAgent:
            headers["User-Agent"] = self.javaUserAgent

        try:
            self.window._navigator.fetch(
                archive, headers=headers, redirect_type="applet", params=params
            )
        except Exception as e:  # pragma: no cover,pylint:disable=broad-except
            log.info("[ERROR][handle_applet] %s", str(e))

    def handle_meta(self, meta):
        log.info(meta)

        name = meta.get("name", None)
        if name and name.lower() in ("generator",):
            content = meta.get("content", None)
            if content:
                log.ThugLogging.add_behavior_warn(f"[Meta] Generator: {content}")

        self.handle_meta_http_equiv(meta)

    def handle_meta_http_equiv(self, meta):
        http_equiv = meta.get("http-equiv", None)
        if http_equiv in (None, "http-equiv"):
            return

        content = meta.get("content", None)
        if content is None:
            return

        tag = http_equiv.lower().replace("-", "_")
        handler = getattr(self, f"handle_meta_{tag}", None)
        if handler:
            handler(http_equiv, content)  # pylint:disable=not-callable

    def handle_meta_x_ua_compatible(self, http_equiv, content):
        # Internet Explorer < 8.0 doesn't support the X-UA-Compatible header
        # and the webpage doesn't specify a <!DOCTYPE> directive.
        if (
            log.ThugOpts.Personality.isIE()
            and log.ThugOpts.Personality.browserMajorVersion >= 8
        ):
            if http_equiv.lower() in ("x-ua-compatible",):
                self.window.doc.compatible = content

                if "emulate" in content.lower():
                    log.ThugLogging.log_classifier(
                        "x-ua-compatible", log.ThugLogging.url, content
                    )

    def force_handle_meta_x_ua_compatible(self):
        for meta in self.window.doc.doc.find_all("meta"):
            http_equiv = meta.get("http-equiv", None)
            if http_equiv is None:
                continue

            if http_equiv.lower() not in ("x-ua-compatible",):
                continue

            content = meta.get("content", None)
            if content is None:
                continue

            self.handle_meta_x_ua_compatible(http_equiv, content)

    def handle_meta_refresh(self, http_equiv, content, delayed=False):
        if http_equiv.lower() not in ("refresh",) or "url" not in content.lower():
            return

        url = None
        timeout = 0
        data_uri = "data:" in content

        for s in content.split(";"):
            if data_uri is True and url is not None:
                url = f"{url};{s}"

            s = s.strip()
            if s.lower().startswith("url="):
                url = s[4:]
                continue

            try:
                timeout = int(s)
            except ValueError:
                pass

        if not url:
            return  # pragma: no cover

        if not delayed and timeout > 0:
            log.ThugLogging.meta_refresh.append((http_equiv, content))
            return

        if log.ThugOpts.features_logging:
            log.ThugLogging.Features.increase_meta_refresh_count()
            log.ThugLogging.Features.increase_url_count()

        if url.startswith("'") and url.endswith("'"):
            url = url[1:-1]

        if url.startswith("\\'") and url.endswith("\\'"):
            url = url[2:-2]

        n_url = log.HTTPSession._normalize_query_fragment_url(url)

        if n_url in log.ThugLogging.meta and log.ThugLogging.meta[n_url] >= 3:
            return  # pragma: no cover

        if data_uri:
            self._handle_data_uri(url)
            return

        try:
            response = self.window._navigator.fetch(url, redirect_type="meta")
        except Exception as e:  # pylint:disable=broad-except
            log.info("[ERROR][handle_meta_refresh] %s", str(e))
            return

        if response is None or not response.ok:
            return

        if n_url not in log.ThugLogging.meta:
            log.ThugLogging.meta[n_url] = 0

        log.ThugLogging.meta[n_url] += 1

        self.window_open(self.window.url, response.content)

    def do_handle_frame(self, frame, url, content):
        window = self.do_window_open(url, content)

        frame_id = frame.get("id", None)
        if frame_id:
            log.ThugLogging.windows[frame_id] = window

        self.run_dft(window)

    def handle_frame(self, frame, redirect_type="frame"):
        if redirect_type not in ("iframe",):
            log.warning(frame)

        src = frame.get("src", None)
        if not src:
            return

        if self._handle_data_uri(src):
            return

        if log.ThugOpts.features_logging:
            log.ThugLogging.Features.increase_url_count()

        try:
            response = self.window._navigator.fetch(src, redirect_type=redirect_type)
        except Exception as e:  # pylint:disable=broad-except
            log.info("[ERROR][handle_frame] %s", str(e))
            return

        if response is None or not response.ok:
            return  # pragma: no cover

        if (
            response.url in log.ThugLogging.frames
            and log.ThugLogging.frames[response.url] >= 3
        ):
            return  # pragma: no cover

        if response.url not in log.ThugLogging.frames:
            log.ThugLogging.frames[response.url] = 0

        log.ThugLogging.frames[response.url] += 1

        if getattr(response, "thug_mimehandler_hit", False):
            return  # pragma: no cover

        self.do_handle_frame(frame, response.url, response.content)

    def handle_iframe(self, iframe):
        log.warning(iframe)

        if log.ThugOpts.features_logging:
            log.ThugLogging.Features.increase_iframe_count()

        self.check_small_element(iframe, "iframe")

        srcdoc = iframe.get("srcdoc", None)
        if srcdoc:
            url = log.ThugLogging.url if log.ThugOpts.local else log.last_url
            self.do_handle_frame(iframe, url, srcdoc)
            return

        self.handle_frame(iframe, "iframe")

    def do_handle_font_face_rule(self, rule):
        for p in rule.style:
            if p.name.lower() not in ("src",):
                continue

            url = p.value
            if url.startswith("url(") and len(url) > 4:
                url = url.split("url(")[1].split(")")[0]

            if log.ThugOpts.features_logging:
                log.ThugLogging.Features.increase_url_count()

            if self._handle_data_uri(url):
                continue  # pragma: no cover

            try:
                self.window._navigator.fetch(url, redirect_type="font face")
            except Exception as e:  # pylint:disable=broad-except
                log.info("[ERROR][do_handle_font_face_rule] %s", str(e))
                return

    def handle_style(self, style):
        log.info(style)

        cssparser = CSSParser(loglevel=logging.CRITICAL, validate=False)

        try:
            sheet = cssparser.parseString(style.encode_contents())
        except Exception as e:  # pragma: no cover,pylint:disable=broad-except
            log.info("[ERROR][handle_style] %s", str(e))
            return

        for rule in sheet:
            if rule.type == rule.FONT_FACE_RULE:
                self.do_handle_font_face_rule(rule)

    def _check_decode_data_uri(self, data, opts):
        mimetypes = (
            "application/javascript",
            "application/x-javascript",
            "text/javascript",
        )

        if opts and opts[0].lower() in mimetypes:
            data.decode()

    def _handle_data_uri(self, uri):
        """
        Data URI Scheme
        data:[<MIME-type>][;charset=<encoding>][;base64],<data>

        The encoding is indicated by ;base64. If it is present the data is
        encoded as base64. Without it the data (as a sequence of octets) is
        represented using ASCII encoding for octets inside the range of safe
        URL characters and using the standard %xx hex encoding of URLs for
        octets outside that range. If <MIME-type> is omitted, it defaults to
        text/plain;charset=US-ASCII. (As a shorthand, the type can be omitted
        but the charset parameter supplied.)

        Some browsers (Chrome, Opera, Safari, Firefox) accept a non-standard
        ordering if both ;base64 and ;charset are supplied, while Internet
        Explorer requires that the charset's specification must precede the
        base64 token.
        """
        uri = uri if isinstance(uri, str) else str(uri)
        if not log.HTTPSession.is_data_uri(uri):
            return None

        if log.ThugOpts.features_logging:
            log.ThugLogging.Features.increase_data_uri_count()

        h = uri.split(",")
        if len(h) < 2 or not h[1]:
            return None  # pragma: no cover

        data = h[1]
        opts = h[0][len("data:") :].split(";")

        if "base64" in opts:
            try:
                data = base64.b64decode(h[1])
                self._check_decode_data_uri(data, opts)
            except Exception:  # pylint:disable=broad-except
                try:
                    data = base64.b64decode(unquote(h[1]).strip())
                    self._check_decode_data_uri(data, opts)
                except Exception:  # pragma: no cover,pylint:disable=broad-except
                    log.warning("[WARNING] Error while handling data URI: %s", data)
                    return None

            opts.remove("base64")

        if not opts or not opts[0]:
            opts = ["text/plain", "charset=US-ASCII"]

        mimetype = opts[0]

        handler = log.MIMEHandler.get_handler(mimetype)
        if handler:
            handler(self.window.url, data)
            return None

        if mimetype.startswith(("text/html",)):
            self.window_open(self.window.url, data)

        return data

    def _handle_blob_uri(self, uri):
        uri = uri if isinstance(uri, str) else str(uri)
        if not log.HTTPSession.is_blob_uri(uri):
            return  # pragma: no cover

        blob = log.UrlObjects.get(uri, None)
        if not blob:
            return  # pragma: no cover

        handler = log.MIMEHandler.get_handler(blob.type)
        if handler:
            handler(self.window.url, blob.blob)
            return

        log.ThugLogging.log_file(blob.blob, uri)  # pragma: no cover

    def handle_a(self, anchor):
        log.info(anchor)

        self.anchors.append(anchor)

        if not log.ThugOpts.extensive:
            return

        href = anchor.get("href", None)
        if not href:
            return  # pragma: no cover

        if self._handle_data_uri(href):
            return

        try:
            response = self.window._navigator.fetch(href, redirect_type="anchor")
        except Exception as e:  # pragma: no cover,pylint:disable=broad-except
            log.info("[ERROR][handle_a] %s", str(e))
            return

        if response is None or not response.ok:
            return  # pragma: no cover

        content_type = response.headers.get("content-type", None)
        if not content_type:
            return  # pragma: no cover

        if content_type.startswith(("text/html",)):
            self.window_open(self.window.url, response.content)

    def handle_link(self, link):
        log.info(link)

        # When a browser requests a resource from a third party server, that cross-origin’s
        # domain name must be resolved to an IP address before the browser can issue the
        # request. This process is known as DNS resolution. While DNS caching can help to
        # reduce this latency, DNS resolution can add significant latency to requests. For
        # websites that open connections to many third parties, this latency can significantly
        # reduce loading performance.
        #
        # dns-prefetch helps developers mask DNS resolution latency. The HTML <link> element
        # offers this functionality by way of a rel attribute value of dns-prefetch. The
        # cross-origin domain is then specified in the href attribute
        rel = link.get("rel", None)
        if rel and any(r in ("dns-prefetch",) for r in rel):
            return  # pragma: no cover

        href = link.get("href", None)
        if not href:
            return  # pragma: no cover

        if log.ThugOpts.features_logging:
            log.ThugLogging.Features.increase_url_count()

        if self._handle_data_uri(href):
            return  # pragma: no cover

        is_favicon = rel and any(r in ("icon",) for r in rel)

        try:
            response = self.window._navigator.fetch(
                href, redirect_type="link", disable_download_prevention=is_favicon
            )
        except Exception as e:  # pylint:disable=broad-except
            log.info("[ERROR][handle_link] %s", str(e))
            return

        if not response or not response.ok:
            return

        if is_favicon:
            log.ThugLogging.log_favicon(response.url, response.content)

    def handle_img(self, img):
        log.info(img)
        src = img.get("src", None)
        if not src:
            return  # pragma: no cover

        if self._handle_data_uri(src):
            return  # pragma: no cover

        cache = getattr(self, "img_cache", None)
        if not cache:
            self.img_cache = set()

        if src in self.img_cache:
            return  # pragma: no cover

        self.img_cache.add(src)

        try:
            self.window._navigator.fetch(src, redirect_type="img")
        except Exception as e:  # pragma: no cover,pylint:disable=broad-except
            log.info("[ERROR][handle_img] %s", str(e))
            self._handle_onerror(img)

    def check_anchors(self):
        clicked_anchors = [a for a in self.anchors if "_clicked" in a.attrs]
        if not clicked_anchors:
            return

        clicked_anchors.sort(key=lambda anchor: anchor["_clicked"])

        for anchor in clicked_anchors:
            del anchor["_clicked"]

            if "href" not in anchor.attrs:
                continue  # pragma: no cover

            href = anchor.attrs["href"]
            self.follow_href(href)

    def follow_href(self, href):
        window = self.do_window_open(self.window.url, "")
        window = window.open(href)

        if window:
            self.run_dft(window)

    def do_handle(self, child, soup, skip=True):
        name = getattr(child, "name", None)

        if name is None:
            return False

        if skip and name in (
            "object",
            "applet",
        ):
            return False

        handler = None

        try:
            handler = getattr(self, f"handle_{str(name.lower())}", None)
        except Exception as e:  # pragma: no cover,pylint:disable=broad-except
            log.warning("[ERROR][do_handle] %s", str(e))

        child._soup = soup

        if handler:
            handler(child)
            if name in ("script",):
                self.run_htmlclassifier(soup)

            return True

        return False

    def check_hidden_element(self, element):
        if not log.ThugOpts.features_logging:
            return

        attrs = getattr(element, "attrs", None)
        if attrs is None:
            return

        if "hidden" in attrs:
            log.ThugLogging.Features.increase_hidden_count()

    def check_small_element(self, element, tagname):
        if not log.ThugOpts.features_logging:
            return

        attrs = getattr(element, "attrs", None)
        if attrs is None:
            return  # pragma: no cover

        attrs_count = 0
        element_area = 1

        for key in ("width", "height"):
            if key not in attrs:
                continue

            try:
                value = int(attrs[key].split("px")[0])
            except Exception:  # pragma: no cover,pylint:disable=broad-except
                value = None

            if not value:
                continue

            if value <= 2:
                m = getattr(
                    log.ThugLogging.Features,
                    f"increase_{tagname}_small_{key}_count",
                    None,
                )
                if m:
                    m()

            attrs_count += 1
            element_area *= value

        if attrs_count > 1 and element_area < 30:
            m = getattr(
                log.ThugLogging.Features, f"increase_{tagname}_small_area_count", None
            )
            if m:
                m()

    def run_htmlclassifier(self, soup):
        try:
            log.HTMLClassifier.classify(
                log.ThugLogging.url if log.ThugOpts.local else self.window.url,
                str(soup),
            )
        except Exception as e:  # pragma: no cover,pylint:disable=broad-except
            log.info("[ERROR][run_htmlclassifier] %s", str(e))

    def do_window_open(self, url, content):
        doc = w3c.parseString(content)
        window = log.Window(url, doc, personality=log.ThugOpts.useragent)
        return window

    def run_dft(self, window, forms=None):
        if forms is None:
            forms = []

        dft = DFT(window, forms=forms)
        dft.run()

    def window_open(self, url, content):
        window = self.do_window_open(url, content)
        self.run_dft(window)

    def async_prefetch(self, soup):
        for tag in soup.find_all(self.async_prefetch_tags):
            src = tag.get("src", None)
            if src:
                self.async_prefetcher.fetch(src)

    def _run(self, soup=None):
        if soup is None:
            soup = self.window.doc.doc

        _soup = soup

        if log.ThugOpts.async_prefetch:
            self.async_prefetch(soup)

        # Dirty hack
        for p in soup.find_all("object"):
            self.check_hidden_element(p)
            self.handle_object(p)
            self.run_htmlclassifier(soup)

        for p in soup.find_all("applet"):
            self.check_hidden_element(p)
            self.handle_applet(p)

        for child in soup.descendants:
            if child is None:
                continue  # pragma: no cover

            self.check_hidden_element(child)

            parents = [p.name.lower() for p in child.parents]
            if "noscript" in parents:
                continue

            self.set_event_handler_attributes(child)
            if not self.do_handle(child, soup):
                continue

            analyzed = set()
            recur = True

            while recur:
                recur = False

                if tuple(soup.descendants) == tuple(_soup.descendants):
                    break

                for _child in set(soup.descendants) - set(
                    _soup.descendants
                ):  # pragma: no cover
                    if _child not in analyzed:
                        analyzed.add(_child)
                        recur = True

                        name = getattr(_child, "name", None)
                        if name:
                            self.do_handle(_child, soup, False)

            analyzed.clear()
            _soup = soup

        self.window.doc._readyState = "complete"

        for child in soup.descendants:
            self.set_event_listeners(child)

        self.handle_events(soup)

        while log.ThugLogging.meta_refresh:
            http_equiv, content = log.ThugLogging.meta_refresh.pop()
            self.handle_meta_refresh(http_equiv, content, True)

    def handle_events(self, soup):
        for evt in self.handled_on_events:
            try:
                self.handle_window_event(evt)
            except Exception:  # pragma: no cover,pylint:disable=broad-except
                log.warning("[handle_events] Event %s not properly handled", evt)

        for evt in self.handled_on_events:
            try:
                self.handle_document_event(evt)
            except Exception:  # pragma: no cover,pylint:disable=broad-except
                log.warning("[handle_events] Event %s not properly handled", evt)

        for evt in self.handled_events:
            try:
                self.handle_element_event(evt)
            except Exception:  # pragma: no cover,pylint:disable=broad-except
                log.warning("[handle_events] Event %s not properly handled", evt)

        self.run_htmlclassifier(soup)

    def run(self):
        with self.context:
            self._run()
            log.ThugLogging.Shellcode.check_shellcodes()
