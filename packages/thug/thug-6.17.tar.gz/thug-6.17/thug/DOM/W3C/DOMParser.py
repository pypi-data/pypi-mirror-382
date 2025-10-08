#!/usr/bin/env python

import logging

log = logging.getLogger("Thug")


class DOMParser:
    def parseFromString(self, s, type_):
        parser = "lxml" if "xml" in type_ else "html.parser"
        return log.DOMImplementation(log.HTMLInspector.run(s, parser))
