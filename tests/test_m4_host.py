import sys
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import pokemonstart_m4_host as host


class WindowsHostGateTests(unittest.TestCase):
    @unittest.skipUnless(sys.platform == "win32", "actual Windows host")
    def test_exact_observed_build_qualifies_and_changed_build_rejects(self):
        self.assertTrue(host.validated_windows_host())
        with patch.object(host.sys, "getwindowsversion",
                          return_value=SimpleNamespace(major=10, minor=0, build=26100)):
            self.assertFalse(host.validated_windows_host())
        with patch.object(host, "VALIDATED_WINDOWS_UBR", -1):
            self.assertFalse(host.validated_windows_host())

    def test_other_platform_rejects(self):
        with patch.object(host.sys, "platform", "linux"):
            self.assertFalse(host.validated_windows_host())
