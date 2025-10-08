# Microsoft XMLDOM

import logging
import base64
import binascii

log = logging.getLogger("Thug")


class Node:
    def __init__(self, xml, elementName):
        self._nodeTypedValue = None
        self._dataType = None
        self._xml = xml
        self._node = xml.createElement(elementName)
        self.text = ""

    def getNodeTypedValue(self):
        try:
            if self._dataType in ("bin.base64",):
                return base64.b64decode(self.text)
            if self._dataType in ("bin.hex",):
                return binascii.unhexlify(self.text)
        except Exception as e:  # pylint:disable=broad-except
            log.info("[ERROR][getNodeTypedValue] %s", str(e))

        return self.text

    def setNodeTypedValue(self, value):
        if self.dataType in ("bin.base64",):
            self.text = base64.b64encode(value.encode())
        elif self.dataType in ("bin.hex",):
            self.text = binascii.hexlify(value.encode())
        else:
            self.text = value

    nodeTypedValue = property(getNodeTypedValue, setNodeTypedValue)

    def getDataType(self):
        return self._dataType

    def setDataType(self, value):
        self._dataType = value

    dataType = property(getDataType, setDataType)


def loadXML(self, bstrXML):
    from thug.DOM.W3C import w3c
    from thug.OS.Windows import security_sys

    self.xml = w3c.parseString(bstrXML)

    if "res://" not in bstrXML:
        return

    for p in bstrXML.split('"'):
        if p.startswith("res://"):
            log.URLClassifier.classify(p)
            log.ThugLogging.add_behavior_warn(
                f"[Microsoft XMLDOM ActiveX] Attempting to load {p}"
            )
            log.ThugLogging.log_classifier(
                "exploit", log.ThugLogging.url, "CVE-2017-0022"
            )
            if any(sys.lower() in p.lower() for sys in security_sys):
                self.parseError._errorCode = 0


def createElement(self, bstrTagName):
    log.ThugLogging.add_behavior_warn(
        f"[Microsoft XMLDOM ActiveX] Creating element {bstrTagName}"
    )
    return Node(self.xml, bstrTagName)
