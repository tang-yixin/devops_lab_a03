"""E6 student test (241250061): consistent declarations produce no findings.

Covers the analyze() pipeline end to end with a miniature trace: Make spawns
cc, whose cc1 child reads unit.c and base.h while as writes unit.o. The Make
database declares exactly those dependencies, so the actual graph equals the
declared graph and findings must be empty.
"""
import tempfile
import unittest
from pathlib import Path

from buildchecker.fullcheck import analyze


class TestConsistentDeclarations(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.folder = Path(self.temp.name)
        self.root = "/course/project"

    def tearDown(self):
        self.temp.cleanup()

    def write(self, name, text):
        path = self.folder / name
        path.write_text(text, encoding="utf-8")
        return path

    def test_no_findings_when_declared_matches_read(self):
        # Process tree: make(t.10) -> cc(t.11) -> cc1(t.12 reads) + as(t.13 writes).
        self.write("t.10", 'execve("/usr/bin/make", ["make", "app"], []) = 0\n'
                   'clone(child_stack=NULL, flags=SIGCHLD) = 11\n')
        self.write("t.11", 'execve("/usr/bin/cc", ["cc", "-c", "unit.c", "-o", "unit.o"], []) = 0\n'
                   'clone(child_stack=NULL, flags=SIGCHLD) = 12\n'
                   'clone(child_stack=NULL, flags=SIGCHLD) = 13\n')
        self.write("t.12", 'execve("/usr/libexec/cc1", ["cc1", "unit.c"], []) = 0\n'
                   'openat(AT_FDCWD, "unit.c", O_RDONLY) = 3\n'
                   'openat(AT_FDCWD, "base.h", O_RDONLY) = 4\n')
        self.write("t.13", 'execve("/usr/bin/as", ["as", "-o", "unit.o"], []) = 0\n'
                   'openat(AT_FDCWD, "unit.o", O_RDWR|O_CREAT|O_TRUNC, 0666) = 3\n')
        # Declaration matches the observed reads exactly.
        database = self.write("db.txt", '# Files\nunit.o: unit.c base.h\n# files hash-table stats:\n')
        result = analyze(self.folder, database, self.root)
        self.assertEqual(result["findings"], [])
        self.assertEqual(result["observed_targets"], ["unit.o"])
