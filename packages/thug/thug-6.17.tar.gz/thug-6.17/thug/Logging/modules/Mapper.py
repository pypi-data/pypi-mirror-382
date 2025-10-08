#!/usr/bin/env python
#
# Mapper.py
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
#
# Author:   Thorsten Sick <thorsten.sick@avira.com> from Avira
#           (developed for the iTES Project http://ites-project.org)
#
# Changes:
#           - pydot support                 (Angelo Dell'Aera <angelo.dellaera@honeynet.org>)
#           - Replace pydot with pygraphviz (Angelo Dell'Aera <angelo.dellaera@honeynet.org>)

import os
import json

from urllib.parse import urlparse

try:
    import pygraphviz

    PYGRAPHVIZ_MODULE = True
except ImportError:  # pragma: no cover
    PYGRAPHVIZ_MODULE = False


class DictDiffer:
    """
    Calculate the difference between two dictionaries as:
    (1) items added
    (2) items removed
    (3) keys same in both but changed values
    (4) keys same in both and unchanged values
    """

    def __init__(self, current_dict, past_dict):
        self.current_dict = current_dict
        self.past_dict = past_dict
        self.set_current = set(current_dict.keys())
        self.set_past = set(past_dict.keys())
        self.intersect = self.set_current.intersection(self.set_past)

    def added(self):
        return self.set_current - self.intersect

    def removed(self):
        return self.set_past - self.intersect

    def changed(self):
        return set(
            o for o in self.intersect if self.past_dict[o] != self.current_dict[o]
        )

    def unchanged(self):
        return set(
            o for o in self.intersect if self.past_dict[o] == self.current_dict[o]
        )

    def anychange(self):
        return self.added() or self.removed() or self.changed()


class Mapper:
    """
    Map URL relationships
    """

    markup_types = (
        "text/html",
        "text/xml",
        "text/css",
    )

    image_types = ("image/",)

    exec_types = (
        "application/javascript",
        "text/javascript",
        "application/x-javascript",
    )

    def __init__(self, resdir, simplify=False):
        """
        @resdir     : Directory to store the result svg in
        @simplify   : Reduce the urls to server names
        """
        self.simplify = simplify

        self.data = {"locations": [], "connections": []}

        self.first_track = True  # flag indicating that we did not follow a track yet
        self.__init_graph(resdir)

    def __init_graph(self, resdir):
        if not PYGRAPHVIZ_MODULE:
            return  # pragma: no cover

        graphdir = os.path.abspath(os.path.join(resdir, os.pardir))
        self.svgfile = os.path.join(graphdir, "graph.svg")
        self.graph = pygraphviz.AGraph(strict=False, directed=True, rankdir="LR")

    @staticmethod
    def _check_content_type(loc, t):
        return loc["content-type"] and loc["content-type"].lower().startswith(t)

    def _check_types(self, loc, _types):
        for t in _types:
            if self._check_content_type(loc, t):
                return True

        return False

    def check_markup(self, loc):
        return self._check_types(loc, self.markup_types)

    def check_image(self, loc):
        return self._check_types(loc, self.image_types)

    def check_exec(self, loc):
        return self._check_types(loc, self.exec_types)

    def get_shape(self, loc):
        # Markup
        if self.check_markup(loc):
            return "box"

        # Images
        if self.check_image(loc):
            return "oval"

        # Executable stuff
        if self.check_exec(loc):
            return "hexagon"

        return None

    @staticmethod
    def get_fillcolor(loc):
        if "error" in loc["flags"]:
            return "orange"

        return None

    @staticmethod
    def get_color(con):
        if con["method"] in ("iframe",):
            return "orange"

        return None

    @staticmethod
    def normalize_url(url):
        if url.endswith("/"):
            return url[:-1]

        return url

    def dot_from_data(self):
        # Create dot from data
        if "locations" in self.data:
            for loc in self.data["locations"]:
                if loc["display"] is False:
                    continue

                url = self.normalize_url(loc["url"])

                self.graph.add_node(url)

                node = self.graph.get_node(url)

                shape = self.get_shape(loc)
                if shape:
                    node.attr["shape"] = shape  # pylint:disable=no-member

                fillcolor = self.get_fillcolor(loc)
                if fillcolor:
                    node.attr["style"] = "filled"  # pylint:disable=no-member
                    node.attr["fillcolor"] = fillcolor  # pylint:disable=no-member

        if "connections" in self.data:
            # Add edges
            count = 1

            for con in self.data["connections"]:
                if con["display"] is False:
                    continue

                _s = self.normalize_url(con["source"])
                source = self.graph.get_node(_s)
                if not source:  # pragma: no cover
                    source = _s

                _d = self.normalize_url(con["destination"])
                destination = self.graph.get_node(_d)
                if not destination:  # pragma: no cover
                    destination = _d

                self.graph.add_edge(source, destination)
                edge = self.graph.get_edge(source, destination)
                edge.attr["label"] = f"[{count}] {con['method']}"  # pylint:disable=no-member
                count += 1

                color = self.get_color(con)
                if color:
                    edge.attr["color"] = color  # pylint:disable=no-member

    def add_location(self, loc):
        """
        Add location information to location data
        """
        loc["display"] = True

        if self.simplify:
            url = urlparse(loc["url"]).netloc
            if url:
                loc["url"] = url

        for a in self.data["locations"]:
            d = DictDiffer(a, loc)
            if not d.anychange():
                return

        self.data["locations"].append(loc)

    def add_weak_location(self, url):
        """
        Generate a weak location for the given url.
        """

        for location in self.data["locations"]:
            if location["url"] == url:
                return

        loc = {
            "mimetype": "",
            "url": url,
            "size": 0,
            "flags": {},
            "sha256": None,
            "content-type": None,
            "display": True,
            "md5": None,
        }

        self.add_location(loc)

    def add_connection(self, con):
        """
        Add connection information to connection data
        """
        con["display"] = True

        if self.simplify:
            url = urlparse(con["source"]).netloc
            if url:
                con["source"] = url

            url = urlparse(con["destination"]).netloc
            if url:
                con["destination"] = url

        self.add_weak_location(con["source"])
        self.add_weak_location(con["destination"])

        for a in self.data["connections"]:
            d = DictDiffer(a, con)
            if not d.anychange():
                return

        self.data["connections"].append(con)

    def add_data(self, data):
        if not PYGRAPHVIZ_MODULE:
            return  # pragma: no cover

        # Add nodes
        if "locations" in data:
            for loc in data["locations"]:
                self.add_location(loc)

        if "connections" in data:
            for con in data["connections"]:
                self.add_connection(con)

    def add_file(self, filename):
        """
        Add data file
        """
        try:
            with open(filename, encoding="utf-8", mode="r") as fd:
                self.add_data(json.load(fd))
        except ValueError:
            pass

    def write_svg(self):
        """
        Create SVG file
        """
        if not PYGRAPHVIZ_MODULE:
            return  # pragma: no cover

        self.dot_from_data()

        try:
            self.graph.layout(prog="dot")
            self.graph.draw(self.svgfile, format="svg")
        except Exception:  # pragma: no cover,pylint:disable=broad-except
            pass

    def activate(self, conto):
        """
        Iterate through data and set display for hot connections
        """

        tofix = []

        for connection in self.data["connections"]:
            if connection["display"] is False and connection["destination"] == conto:
                connection["display"] = True
                tofix.append(connection["source"])

        for location in self.data["locations"]:
            if location["url"] == conto or location["url"] in tofix:
                location["display"] = True

        for elem in tofix:
            self.activate(elem)

    def follow_track(self, end):
        """
        Follow the track between entry point of the analysis and the exploit URL.
        Remove all non-relevant stuff

        @end: end url to track the connections to
        """

        if self.first_track:
            for con in self.data["connections"]:
                con["display"] = False

            for loc in self.data["locations"]:
                loc["display"] = False

        self.first_track = False
        self.activate(end)

    def write_text(self):
        """
        Return text representation
        """
        res = ""
        for con in self.data["connections"]:
            if con["display"]:
                res += f"{str(con['source'])} -- {str(con['method'])} --> {str(con['destination'])} {os.linesep}"

        return res
