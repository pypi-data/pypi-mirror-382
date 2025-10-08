#!/usr/bin/env python
#
# BaseLogging.py
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

import os
import errno
import hashlib
import logging
import datetime
import tempfile

log = logging.getLogger("Thug")


class BaseLogging:
    def __init__(self):
        self.baseDir = None

    @staticmethod
    def check_module(module, config):
        if not getattr(log.ThugOpts, f"{module}_logging", True):
            return False

        return config.getboolean(module, "enable")

    def set_basedir(self, url):
        if self.baseDir:
            return

        t = datetime.datetime.now()
        m = hashlib.md5()  # nosec
        m.update(url.encode("utf8"))

        cwd = os.getcwd()

        base = os.getenv(
            "THUG_LOGBASE",
            cwd if os.access(cwd, os.W_OK) else tempfile.mkdtemp(),
        )

        self.baseDir = os.path.join(
            base, "thug-logs", m.hexdigest(), t.strftime("%Y%m%d%H%M%S")
        )

        if not log.ThugOpts.file_logging:
            return

        try:
            os.makedirs(self.baseDir)
        except OSError as e:
            if e.errno == errno.EEXIST:
                pass
            else:  # pragma: no cover
                raise

        thug_csv = os.path.join(base, "thug-logs", "thug.csv")
        csv_line = f"{m.hexdigest()},{url}\n"

        if os.path.exists(thug_csv):
            with open(thug_csv, encoding="utf-8", mode="r") as fd:
                for line in fd.readlines():
                    if line == csv_line:
                        return

        with open(thug_csv, encoding="utf-8", mode="at+") as fd:
            fd.write(csv_line)

    def set_absbasedir(self, basedir):
        self.baseDir = basedir

        if not log.ThugOpts.file_logging:
            return

        try:
            os.makedirs(self.baseDir)
        except OSError as e:
            if e.errno == errno.EEXIST:
                pass
            else:
                raise
