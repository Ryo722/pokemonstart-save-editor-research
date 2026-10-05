"""Narrow host evidence gate for M4 Windows delivery."""
from __future__ import annotations

import sys


# The actual Windows run was Windows 11 build 26200.9457. A changed build is
# intentionally unvalidated until its bounded delivery path is checked again.
VALIDATED_WINDOWS_BUILD = 26200
VALIDATED_WINDOWS_UBR = 9457


def validated_windows_host() -> bool:
    if sys.platform != "win32" or not hasattr(sys, "getwindowsversion"):
        return False
    try:
        import winreg
        version = sys.getwindowsversion()
        if (version.major, version.minor, version.build) != (10, 0, VALIDATED_WINDOWS_BUILD):
            return False
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                            r"SOFTWARE\Microsoft\Windows NT\CurrentVersion") as key:
            revision, _ = winreg.QueryValueEx(key, "UBR")
        return revision == VALIDATED_WINDOWS_UBR
    except (OSError, ValueError, AttributeError):
        return False
