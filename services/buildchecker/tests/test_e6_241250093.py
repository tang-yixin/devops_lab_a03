"""E6 student test (241250093): reads outside the project root never enter the
actual dependency graph and therefore cannot produce findings.

Covers execution_graph()'s project-root path filtering (fullcheck.project_path):
a successful read-open whose resolved absolute path is not strictly under the
project root is dropped before it can become a dependency or a MISSING finding.
This is the mechanism behind the E6 teaching conclusion that only project-local
reads count toward MD/RD.
"""
import tempfile
import unittest
from pathlib import Path

from buildchecker.fullcheck import analyze, execution_graph


class TestProjectRootFiltering(unittest.TestCase):
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

    def build_trace(self, reader_extra=""):
        # Process tree: make(t.10) -> cc(t.11) -> cc1(t.12 reads) + as(t.13 writes).
        self.write("t.10", 'execve("/usr/bin/make", ["make", "app"], []) = 0\n'
                   'clone(child_stack=NULL, flags=SIGCHLD) = 11\n')
        self.write("t.11", 'execve("/usr/bin/cc", ["cc", "-c", "module.c", "-o", "module.o"], []) = 0\n'
                   'clone(child_stack=NULL, flags=SIGCHLD) = 12\n'
                   'clone(child_stack=NULL, flags=SIGCHLD) = 13\n')
        self.write("t.12", 'execve("/usr/libexec/cc1", ["cc1", "module.c"], []) = 0\n'
                   'openat(AT_FDCWD, "module.c", O_RDONLY) = 3\n'
                   'openat(AT_FDCWD, "local.h", O_RDONLY) = 4\n' + reader_extra)
        self.write("t.13", 'execve("/usr/bin/as", ["as", "-o", "module.o"], []) = 0\n'
                   'openat(AT_FDCWD, "module.o", O_RDWR|O_CREAT|O_TRUNC, 0666) = 3\n')

    def test_outside_root_absolute_read_is_filtered(self):
        # /usr/include/stdio.h and /course/other/secret.h lie outside /course/project.
        self.build_trace(
            'openat(AT_FDCWD, "/usr/include/stdio.h", O_RDONLY) = 5\n'
            'openat(AT_FDCWD, "/course/other/secret.h", O_RDONLY) = 6\n')
        targets, _ = execution_graph(self.folder, self.root)
        # Only project-local reads survive into the actual graph.
        self.assertEqual(set(targets["module.o"]["dependencies"]),
                         {"module.c", "local.h"})
        # The outside-root reads must be absent entirely.
        self.assertNotIn("/usr/include/stdio.h", targets["module.o"]["dependencies"])
        self.assertNotIn("course/other/secret.h", targets["module.o"]["dependencies"])

    def test_outside_root_read_produces_no_finding(self):
        # The compiler also reads /usr/include/stdio.h (outside root, undeclared),
        # but it is filtered before analysis, so it cannot become a MISSING finding.
        self.build_trace(
            'openat(AT_FDCWD, "/usr/include/stdio.h", O_RDONLY) = 5\n')
        database = self.write("db.txt",
                              '# Files\nmodule.o: module.c local.h\n# files hash-table stats:\n')
        result = analyze(self.folder, database, self.root)
        self.assertEqual(result["findings"], [])
        self.assertEqual(result["observed_targets"], ["module.o"])


if __name__ == "__main__":
    unittest.main()
