#!/usr/bin/env python
#
# HTTPSession.py
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

import logging
import sys
import socket
import ssl
import urllib.parse

import requests
import urllib3

urllib3.disable_warnings(category=urllib3.exceptions.InsecureRequestWarning)

log = logging.getLogger("Thug")


class HTTPSession:
    def __init__(self, proxy=None):
        self.__init_download_prevention()

        if proxy is None:
            proxy = log.ThugOpts.proxy

        self.__init_session(proxy)
        self.filecount = 0

    def __check_proxy_alive(self, hostname, port):
        s = socket.create_connection(
            (hostname, port), timeout=log.ThugOpts.proxy_connect_timeout
        )
        s.close()

    def __do_init_proxy(self, proxy):
        url = urllib.parse.urlparse(proxy)
        if not url.scheme:
            return False

        if not url.scheme.lower().startswith(("http", "socks4", "socks5")):
            return False

        try:
            self.__check_proxy_alive(url.hostname, url.port)
        except Exception as e:  # pylint:disable=broad-except
            log.critical("[CRITICAL] Proxy not available. Aborting the analysis!")

            if log.ThugOpts.raise_for_proxy:
                raise ValueError("[CRITICAL] Proxy not available") from e

            sys.exit(0)  # pragma: no cover

        self.session.proxies = {"http": proxy, "https": proxy}

        return True

    def __init_proxy(self, proxy):
        if proxy is None:
            return

        if self.__do_init_proxy(proxy):
            return

        log.critical("[CRITICAL] Wrong proxy specified. Aborting the analysis!")
        sys.exit(0)

    def __init_session(self, proxy):
        self.session = requests.Session()
        self.__init_proxy(proxy)

    def __init_download_prevention(self):
        if not log.ThugOpts.download_prevent:
            self.download_prevented_mimetypes = tuple()
            return

        mimetypes = ["audio/", "video/"]

        if not log.ThugOpts.image_processing:
            mimetypes.append("image/")

        self.download_prevented_mimetypes = tuple(mimetypes)

    def _normalize_protocol_relative_url(self, window, url):
        if not url.startswith("//"):
            return url

        if window.url in ("about:blank",):
            return f"http:{url}"

        base_url = urllib.parse.urlparse(window.url)
        return f"{base_url.scheme}:{url}" if base_url.scheme else f"http:{url}"

    @staticmethod
    def _normalize_query_fragment_url(url):
        p_url = urllib.parse.urlparse(urllib.parse.urldefrag(url)[0])

        p_query = urllib.parse.parse_qs(p_url.query, keep_blank_values=True)
        e_query = urllib.parse.urlencode(p_query.fromkeys(p_query, ""))

        return p_url._replace(query=e_query).geturl()

    def _is_compatible(self, url, scheme):
        return url.startswith(f"{scheme}:/") and not url.startswith(f"{scheme}://")

    def _check_compatibility(self, url):
        for scheme in (
            "http",
            "https",
        ):
            if self._is_compatible(url, scheme):
                return f"{scheme}://{url.split(f'{scheme}:/')[1]}"

        return url

    def is_download_prevented(self, mimetype=None):
        if mimetype and mimetype.startswith(self.download_prevented_mimetypes):
            return True

        return False

    @staticmethod
    def is_data_uri(url):
        if url.lower().startswith("data:"):
            return True

        if url.startswith(("'", '"')) and url[1:].lower().startswith("data:"):
            return True  # pragma: no cover

        return False

    @staticmethod
    def is_blob_uri(url):
        if url.lower().startswith("blob:"):
            return True

        if url.startswith(("'", '"')) and url[1:].lower().startswith("blob:"):
            return True  # pragma: no cover

        return False

    def normalize_url(self, window, url):
        url = url.strip()

        # Do not normalize Data and Blob URI scheme
        if (
            url.lower().startswith("url=")
            or self.is_data_uri(url)
            or self.is_blob_uri(url)
        ):
            return url

        if url.startswith("#"):
            log.warning("[INFO] Ignoring anchor: %s", url)
            return None

        # Check the URL is not broken (i.e. http:/www.google.com) and
        # fix it if the broken URL option is enabled.
        if log.ThugOpts.broken_url:
            url = self._check_compatibility(url)

        url = self._normalize_protocol_relative_url(window, url)

        try:
            url = urllib.parse.quote(url, safe="%/:=&?~#+!$,;'@()*[]{}")
        except KeyError:  # pragma: no cover
            pass

        _url = urllib.parse.urlparse(url)

        base_url = None
        last_url = getattr(log, "last_url", None)

        for _base_url in (
            last_url,
            window.url,
        ):
            if not _base_url:
                continue

            base_url = _base_url
            p_base_url = urllib.parse.urlparse(base_url)
            if p_base_url.scheme:
                break

        # Check if a scheme handler is registered and calls the proper
        # handler in such case. This is how a real browser would handle
        # a specific scheme so if you want to add your own handler for
        # analyzing specific schemes the proper way to go is to define
        # a method named handle_<scheme> in the SchemeHandler and put
        # the logic within such method.
        handler = getattr(log.SchemeHandler, f"handle_{_url.scheme}", None)
        if handler:
            handler(window, url)
            return None

        if not _url.netloc and base_url:
            _url = urllib.parse.urljoin(base_url, url)
            log.warning("[Navigator URL Translation] %s --> %s", url, _url)
            return _url

        return url

    def check_equal_urls(self, url, last_url):
        return urllib.parse.unquote(url) in (urllib.parse.unquote(last_url),)

    def check_redirection_loop_url_params(self, url):
        p_url = urllib.parse.urlparse(url)

        qs = urllib.parse.parse_qs(p_url.query)
        # If the query string contains more than 10 parameters with the
        # same name we are reasonably experiencing a redirection loop
        return any(len(v) > 10 for v in qs.values())

    def build_http_headers(self, window, personality, headers):
        http_headers = {
            "Cache-Control": "no-cache",
            "Accept-Language": "en-US",
            "Accept": "*/*",
            "User-Agent": personality,
        }

        if window and window.url not in ("about:blank",):
            referer = (
                window.url if window.url.startswith("http") else f"http://{window.url}"
            )
            http_headers["Referer"] = referer

        # REVIEW ME!
        # if window and window.doc.cookie:
        #    http_headers['Cookie'] = window.doc.cookie

        for name, value in headers.items():
            http_headers[name] = value

        return http_headers

    def fetch_ssl_certificate(self, url):
        if not log.ThugOpts.cert_logging:
            return

        _url = urllib.parse.urlparse(url)
        if _url.scheme not in ("https",):
            return

        port = _url.port if _url.port else 443

        certificate = log.ThugLogging.ssl_certs.get((_url.netloc, port), None)
        if certificate:
            return

        try:
            certificate = ssl.get_server_certificate(
                (_url.netloc, port), ssl_version=ssl.PROTOCOL_TLS_CLIENT
            )
            log.ThugLogging.ssl_certs[(_url.netloc, port)] = certificate
            log.ThugLogging.log_certificate(url, certificate)
        except Exception as e:  # pragma: no cover,pylint:disable=broad-except
            log.warning("[SSL ERROR] %s", str(e))

    def fetch(
        self, url, method="GET", window=None, personality=None, headers=None, body=None
    ):
        if log.URLClassifier.filter(url):
            return None

        if self.is_data_uri(url):
            log.DFT._handle_data_uri(url)
            return None

        if self.is_blob_uri(url):
            log.DFT._handle_blob_uri(url)
            return None

        fetcher = getattr(self.session, method.lower(), None)
        if fetcher is None:  # pragma: no cover
            log.warning("Not supported method: %s", method)
            return None

        if headers is None:  # pragma: no cover
            headers = {}

        response = None

        try:
            async_prefetcher = getattr(log.DFT, "async_prefetcher", None)
        except Exception:  # pylint: disable=broad-except
            async_prefetcher = None

        if async_prefetcher:
            async_result = async_prefetcher.responses.get(url, None)
            if async_result:
                response = async_result.result()

        if response is None:
            _headers = self.build_http_headers(window, personality, headers)

            try:
                response = fetcher(
                    url,  # pylint:disable=not-callable
                    headers=_headers,
                    timeout=log.ThugOpts.connect_timeout,
                    data=body,
                    verify=log.ThugOpts.ssl_verify,
                    stream=True,
                )
            except requests.ConnectionError as e:
                log.warning("[HTTPSession] %s", str(e))
                raise

        if not response.ok:
            return None

        log.ThugLogging.retrieved_urls.add(url)

        self.filecount += 1

        if log.ThugOpts.web_tracking:
            log.WebTracking.inspect_response(response)

        return response

    def threshold_expired(self, url):
        if not log.ThugOpts.threshold:
            return False

        if self.filecount >= log.ThugOpts.threshold:
            log.ThugLogging.log_location(
                url, None, flags={"error": "Threshold Exceeded"}
            )
            return True

        return False

    @property
    def no_fetch(self):
        return log.ThugOpts.no_fetch

    def about_blank(self, url):
        return url.lower() in ("about:blank",)

    def get_cookies(self):
        return self.session.cookies

    def set_cookies(self, name, value):
        self.session.cookies.set(name, value)

    cookies = property(get_cookies, set_cookies)
