#!/usr/bin/env python
#
# MimeTypes.py
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
from .MimeType import MimeType
from .Plugin import Plugin

log = logging.getLogger("Thug")


class MimeTypes(dict):
    def __init__(self):
        super().__init__()

        if not log.ThugVulnModules.acropdf_disabled:
            self["application/pdf"] = MimeType(
                {
                    "description": "Adobe Acrobat Plug-In",
                    "suffixes": "pdf",
                    "filename": "npctrl.dll",
                    "type": "application/pdf",
                    "enabledPlugin": Plugin(
                        {
                            "name": "Adobe Acrobat",
                            "version": f"{log.ThugVulnModules.acropdf_pdf}",
                            "description": "Adobe Acrobat Plug-In",
                        }
                    ),
                    "enabled": True,
                }
            )

        if not log.ThugVulnModules.shockwave_flash_disabled:
            self["application/x-shockwave-flash"] = MimeType(
                {
                    "description": "Shockwave Flash",
                    "suffixes": "swf",
                    "filename": f"Flash32_"
                    f"{'_'.join(log.ThugVulnModules.shockwave_flash.split('.'))}.ocx",
                    "type": "application/x-shockwave-flash",
                    "enabledPlugin": Plugin(
                        {
                            "name": f"Shockwave Flash "
                            f"{log.ThugVulnModules.shockwave_flash}",
                            "version": f"{log.ThugVulnModules.shockwave_flash}",
                            "description": f"Shockwave Flash "
                            f"{log.ThugVulnModules.shockwave_flash}",
                        }
                    ),
                    "enabled": True,
                }
            )

        if not log.ThugVulnModules.javaplugin_disabled:
            self["application/x-java-applet"] = MimeType(
                {
                    "description": "Java Applet",
                    "suffixes": "jar",
                    "filename": "npjp2.dll",
                    "type": f"application/x-java-applet;jpi-version="
                    f"{log.ThugVulnModules._javaplugin}",
                    "enabledPlugin": Plugin(
                        {
                            "name": f"Java {log.ThugVulnModules._javaplugin}",
                            "version": f"{log.ThugVulnModules._javaplugin}",
                            "description": "Java",
                        }
                    ),
                    "enabled": True,
                }
            )

        if log.ThugOpts.Personality.isWindows():
            self["application/x-ms-wmz"] = MimeType(
                {
                    "description": "Windows Media Player",
                    "suffixes": "wmz",
                    "filename": "npdsplay.dll",
                    "type": "application/x-ms-wmz",
                    "enabledPlugin": Plugin(
                        {
                            "name": "Windows Media Player 7",
                            "version": "7",
                            "description": "Windows Media Player 7",
                        }
                    ),
                    "enabled": True,
                }
            )

    def __getitem__(self, key):
        try:
            key = int(key)
            return self.item(key)
        except ValueError:
            return dict.__getitem__(self, key) if key in self else MimeType()

    @property
    def length(self):
        return len(self)

    def item(self, index):
        if index >= self.length:
            return MimeType()

        return list(self.values())[index]

    def namedItem(self, key):
        return dict.__getitem__(self, key) if key in self else MimeType()
