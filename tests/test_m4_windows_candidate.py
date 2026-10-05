import hashlib
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pokemonstart_m4_publication as candidate


@unittest.skipUnless(sys.platform == "win32", "actual Windows NTFS candidate")
class WindowsCandidateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        candidate._local_ntfs(self.root)
        self.source = self.root / "source.sav"
        self.destination = self.root / "output.sav"
        self.source.write_bytes(b"source")

    def publish(self, audit=lambda raw: None):
        return candidate.publish_new(self.source, self.destination,
                                     hashlib.sha256(b"source").hexdigest(), b"complete", audit)

    def assert_clean(self):
        self.assertFalse(self.destination.exists())
        self.assertEqual(list(self.root.glob(".pokemonstart-stage-*")), [])

    def test_complete_and_no_clobber(self):
        self.assertEqual(self.publish(), hashlib.sha256(b"complete").hexdigest())
        self.assertEqual(self.destination.read_bytes(), b"complete")
        self.assertEqual(self.source.read_bytes(), b"source")
        self.assertEqual(list(self.root.glob(".pokemonstart-stage-*")), [])
        with self.assertRaisesRegex(candidate.PublicationError, "exists"):
            self.publish()
        self.assertEqual(self.destination.read_bytes(), b"complete")

    def test_aliases_and_repository(self):
        with self.assertRaises(candidate.PublicationError):
            candidate.publish_new(self.source, self.source, hashlib.sha256(b"source").hexdigest(),
                                  b"complete", lambda raw: None)
        os.link(self.source, self.destination)
        with self.assertRaises(candidate.PublicationError):
            self.publish()
        self.assertEqual(self.source.read_bytes(), b"source")
        self.destination.unlink()
        with self.assertRaisesRegex(candidate.PublicationError, "repository"):
            candidate.publish_new(self.source, Path(candidate.__file__).parent / "forbidden.sav",
                                  hashlib.sha256(b"source").hexdigest(), b"complete", lambda raw: None)

    def test_race_and_faults(self):
        real_link = os.link

        def race(src, dst):
            Path(dst).write_bytes(b"rival")
            return real_link(src, dst)

        with patch.object(candidate.os, "link", side_effect=race):
            with self.assertRaises(FileExistsError):
                self.publish()
        self.assertEqual(self.destination.read_bytes(), b"rival")
        self.destination.unlink()

        with patch.object(candidate.os, "link", side_effect=OSError("link failed")):
            with self.assertRaisesRegex(OSError, "link failed"):
                self.publish()
        self.assert_clean()

        with self.assertRaisesRegex(ValueError, "audit"):
            self.publish(lambda raw: (_ for _ in ()).throw(ValueError("audit")))
        self.assert_clean()

        def mutate(raw):
            self.source.write_bytes(b"mutated")
        with self.assertRaisesRegex(candidate.PublicationError, "source changed"):
            self.publish(mutate)
        self.assert_clean()

    def test_short_write_leaves_no_final(self):
        real_fdopen = os.fdopen
        class ShortWriter:
            def __init__(self, inner): self.inner = inner
            def __enter__(self): self.inner.__enter__(); return self
            def __exit__(self, *args): return self.inner.__exit__(*args)
            def write(self, data): return self.inner.write(data[:2])
            def flush(self): self.inner.flush()
            def fileno(self): return self.inner.fileno()
        with patch.object(candidate.os, "fdopen",
                          side_effect=lambda fd, mode: ShortWriter(real_fdopen(fd, mode))):
            with self.assertRaisesRegex(candidate.PublicationError, "short"):
                self.publish()
        self.assert_clean()

    def test_reparse_destination_and_parent(self):
        try:
            self.destination.symlink_to(self.source)
        except OSError:
            pass  # Standard Windows accounts often lack symlink privilege.
        else:
            with self.assertRaises(candidate.PublicationError):
                self.publish()
            self.destination.unlink()
        alias = self.root / "parent_alias"
        created = subprocess.run(["cmd", "/c", "mklink", "/J", str(alias), str(self.root)],
                                 capture_output=True)
        if created.returncode:
            self.skipTest("junction creation unavailable")
        with self.assertRaisesRegex(candidate.PublicationError, "reparse"):
            candidate.publish_new(self.source, alias / "output.sav",
                                  hashlib.sha256(b"source").hexdigest(), b"complete",
                                  lambda raw: None)
        alias.rmdir()

    def test_network_removable_and_non_ntfs_fail_before_source_io(self):
        for drive_type, filesystem, reason in ((4, "NTFS", "network/removable"),
                                               (2, "NTFS", "network/removable"),
                                               (3, "ReFS", "only local NTFS")):
            with self.subTest(drive_type=drive_type, filesystem=filesystem), \
                 patch.object(candidate, "_windows_volume",
                              return_value=(drive_type, filesystem)):
                with self.assertRaisesRegex(candidate.PublicationError, reason):
                    candidate.publish_new(self.root / "missing.sav", self.destination,
                                          "0" * 64, b"complete", lambda raw: None)
                self.assert_clean()

    def test_unvalidated_windows_build_fails_before_source_io(self):
        with patch.object(candidate.host, "validated_windows_host", return_value=False):
            with self.assertRaisesRegex(candidate.PublicationError, "unvalidated"):
                candidate.publish_new(self.root / "missing.sav", self.destination,
                                      "0" * 64, b"complete", lambda raw: None)
        self.assert_clean()

    def test_postpublication_rejection_removes_owned_link(self):
        calls = 0
        def audit(raw):
            nonlocal calls
            calls += 1
            if calls == 3:
                raise ValueError("final audit failed")
        with self.assertRaisesRegex(ValueError, "final audit failed"):
            self.publish(audit)
        self.assertEqual(calls, 3)
        self.assert_clean()

    def test_postpublication_replacement_is_preserved(self):
        calls = 0
        def audit(raw):
            nonlocal calls
            calls += 1
            if calls == 3:
                self.destination.unlink()
                self.destination.write_bytes(b"rival")
                raise ValueError("final audit failed")
        with self.assertRaisesRegex(ValueError, "final audit failed"):
            self.publish(audit)
        self.assertEqual(self.destination.read_bytes(), b"rival")
        self.assertEqual(self.source.read_bytes(), b"source")
        self.assertEqual(list(self.root.glob(".pokemonstart-stage-*")), [])

    def test_process_exit_boundaries(self):
        script = ("import os,sys,hashlib; import pokemonstart_m4_publication as c; "
                  "c.os.link=lambda *args: os._exit(31); "
                  "c.publish_new(sys.argv[1],sys.argv[2],hashlib.sha256(b'source').hexdigest(),"
                  "b'complete',lambda raw: None)")
        run = subprocess.run([sys.executable, "-c", script, str(self.source), str(self.destination)])
        self.assertEqual(run.returncode, 31)
        self.assertFalse(self.destination.exists())
        stages = list(self.root.glob(".pokemonstart-stage-*"))
        self.assertEqual(len(stages), 1)
        self.assertEqual(stages[0].read_bytes(), b"complete")
        stages[0].unlink()

        script = ("import os,sys,hashlib; import pokemonstart_m4_publication as c; "
                  "real=c.os.link; "
                  "c.os.link=lambda a,b: (real(a,b),os._exit(32)); "
                  "c.publish_new(sys.argv[1],sys.argv[2],hashlib.sha256(b'source').hexdigest(),"
                  "b'complete',lambda raw: None)")
        run = subprocess.run([sys.executable, "-c", script, str(self.source), str(self.destination)])
        self.assertEqual(run.returncode, 32)
        self.assertEqual(self.destination.read_bytes(), b"complete")
        self.assertEqual(self.source.read_bytes(), b"source")


if __name__ == "__main__":
    unittest.main()
