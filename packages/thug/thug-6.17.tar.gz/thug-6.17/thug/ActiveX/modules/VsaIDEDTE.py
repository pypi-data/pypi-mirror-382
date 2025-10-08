import logging

log = logging.getLogger("Thug")


def CreateObject(self, _object, param=""):  # pylint:disable=unused-argument
    from thug import ActiveX

    log.ThugLogging.add_behavior_warn(f"[VsaIDE.DTE ActiveX] CreateObject ({_object})")
    log.ThugLogging.log_exploit_event(
        self._window.url,
        "VsaIDE.DTE ActiveX",
        "CreateObject",
        data={"object": _object},
        forward=False,
    )

    return ActiveX.ActiveX._ActiveXObject(self._window, _object)
