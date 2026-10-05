import hashlib
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pokemonstart_m4_publication as p


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


class PublicationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.source = self.directory / "original.sav"
        self.source.write_bytes(b"original")
        self.destination = self.directory / "edited.sav"

    def publish(self, audit=lambda raw: None):
        return p.publish_new(self.source, self.destination, sha(b"original"), b"candidate", audit)

    def test_complete_new_file_and_source_unchanged(self):
        self.assertEqual(self.publish(), sha(b"candidate"))
        self.assertEqual(self.destination.read_bytes(), b"candidate")
        self.assertEqual(self.source.read_bytes(), b"original")
        self.assertEqual(list(self.directory.glob(".pokemonstart-stage-*")), [])

    def test_existing_destination_and_aliases(self):
        self.destination.write_bytes(b"existing")
        with self.assertRaisesRegex(p.PublicationError, "exists"):
            self.publish()
        self.assertEqual(self.destination.read_bytes(), b"existing")
        self.destination.unlink()
        with self.assertRaisesRegex(p.PublicationError, "alias"):
            p.publish_new(self.source, self.source, sha(b"original"), b"candidate", lambda raw: None)
        self.destination.symlink_to(self.source)
        with self.assertRaisesRegex(p.PublicationError, "alias"):
            self.publish()

    def test_prepublication_audit_failure_leaves_no_final(self):
        def reject(raw):
            raise p.PublicationError("audit failed")
        with self.assertRaisesRegex(p.PublicationError, "audit failed"):
            self.publish(reject)
        self.assertFalse(self.destination.exists())
        self.assertEqual(self.source.read_bytes(), b"original")

    def test_short_write_failure_leaves_no_final(self):
        real_fdopen = os.fdopen
        class ShortWriter:
            def __init__(self, inner):
                self.inner = inner
            def __enter__(self):
                self.inner.__enter__()
                return self
            def __exit__(self, *args):
                return self.inner.__exit__(*args)
            def write(self, data):
                return self.inner.write(data[:2])
            def flush(self):
                self.inner.flush()
            def fileno(self):
                return self.inner.fileno()
        with patch.object(p.os, "fdopen", side_effect=lambda fd, mode: ShortWriter(real_fdopen(fd, mode))):
            with self.assertRaisesRegex(p.PublicationError, "short"):
                self.publish()
        self.assertFalse(self.destination.exists())
        self.assertEqual(list(self.directory.glob(".pokemonstart-stage-*")), [])

    def test_link_failure_leaves_no_final(self):
        with patch.object(p.os, "link", side_effect=OSError("link failed")):
            with self.assertRaisesRegex(OSError, "link failed"):
                self.publish()
        self.assertFalse(self.destination.exists())
        self.assertEqual(list(self.directory.glob(".pokemonstart-stage-*")), [])

    def test_source_change_during_stage_rejected(self):
        def audit(raw):
            self.source.write_bytes(b"changed")
        with self.assertRaisesRegex(p.PublicationError, "source changed"):
            self.publish(audit)
        self.assertFalse(self.destination.exists())

    def test_process_crash_at_publication_boundaries(self):
        after_link = (
            "import os,sys,hashlib; import pokemonstart_m4_publication as p; "
            "p._fsync_directory=lambda directory: os._exit(37); "
            "p.publish_new(sys.argv[1],sys.argv[2],hashlib.sha256(b'original').hexdigest(),"
            "b'candidate',lambda raw: None)"
        )
        result = subprocess.run([sys.executable, "-c", after_link,
                                 str(self.source), str(self.destination)], check=False)
        self.assertEqual(result.returncode, 37)
        self.assertEqual(self.destination.read_bytes(), b"candidate")
        self.assertEqual(self.source.read_bytes(), b"original")
        self.destination.unlink()
        for staged in self.directory.glob(".pokemonstart-stage-*"):
            staged.unlink()
        before_link = (
            "import os,sys,hashlib; import pokemonstart_m4_publication as p; "
            "p.os.link=lambda *args: os._exit(38); "
            "p.publish_new(sys.argv[1],sys.argv[2],hashlib.sha256(b'original').hexdigest(),"
            "b'candidate',lambda raw: None)"
        )
        result = subprocess.run([sys.executable, "-c", before_link,
                                 str(self.source), str(self.destination)], check=False)
        self.assertEqual(result.returncode, 38)
        self.assertFalse(self.destination.exists())
        self.assertEqual(self.source.read_bytes(), b"original")


if __name__ == "__main__":
    unittest.main()
