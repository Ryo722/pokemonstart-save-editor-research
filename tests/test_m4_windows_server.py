"""Actual Windows loopback listener smoke, with no private inputs."""
import importlib.util
import socket
import subprocess
import sys
import time
import unittest
from pathlib import Path


@unittest.skipUnless(sys.platform == "win32", "actual Windows listener")
@unittest.skipUnless(importlib.util.find_spec("nicegui"), "NiceGUI optional dependency")
class WindowsServerTests(unittest.TestCase):
    def test_listener_is_loopback_only(self):
        import nicegui
        with socket.socket() as probe:
            probe.bind(("127.0.0.1", 0))
            port = probe.getsockname()[1]
        site = str(Path(nicegui.__file__).parent.parent)
        code = ("import sys; sys.path.insert(0,sys.argv[1]); "
                "import pokemonstart_m4_web as web; "
                "web.run_server('unused-journal','unused-rom','synthetic',int(sys.argv[2]))")
        process = subprocess.Popen([sys.executable, "-c", code, site, str(port)],
                                   stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
                                   creationflags=subprocess.CREATE_NO_WINDOW)
        try:
            for _ in range(50):
                if process.poll() is not None:
                    self.fail("NiceGUI exited before binding loopback")
                try:
                    with socket.create_connection(("127.0.0.1", port), timeout=0.1):
                        break
                except OSError:
                    time.sleep(0.1)
            else:
                self.fail("NiceGUI did not bind loopback")
            lines = subprocess.check_output(["netstat", "-ano", "-p", "tcp"], text=True).splitlines()
            listeners = [line for line in lines if f":{port} " in line and "LISTENING" in line]
            self.assertTrue(listeners, "listener missing from netstat")
            self.assertTrue(all(line.split()[1] == f"127.0.0.1:{port}"
                                for line in listeners), listeners)
        finally:
            process.terminate()
            process.communicate(timeout=10)
