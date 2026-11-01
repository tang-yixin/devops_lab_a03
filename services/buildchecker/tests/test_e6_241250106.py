"""E6 student test (241250106): failed syscalls never become dependencies.

Targets the ``ret < 0: continue`` guard at the top of the per-event loop in
``execution_graph``. The miniature transcript below contains three failed
calls that a naive implementation would happily record:

* a missing header (``ENOENT``) - must not become a read dependency,
* an unreadable header (``EACCES``) - must not become a read dependency,
* a temporary output that cannot be created (``ENOSPC``) - must not become a
  second final output of the recipe job.

They are paired with positive controls: the same header opened again later and
succeeding *is* recorded (at the line of the successful call), and a declared
dependency whose only open failed stays ``REDUNDANT`` instead of being
silently satisfied.
"""
import tempfile
import unittest
from pathlib import Path

from buildchecker.fullcheck import analyze, execution_graph


class TestFailedCallsAreNotDependencies(unittest.TestCase):
    ROOT = "/course/project"

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.folder = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def write(self, name, text):
        path = self.folder / name
        path.write_text(text, encoding="utf-8")
        return path

    def traces(self, reader_extra="", writer_extra=""):
        """make(t.20) -> cc(t.21) -> cc1(t.22 reads) + as(t.23 writes prog.o)."""
        self.write("t.20", 'execve("/usr/bin/make", ["make", "prog"], []) = 0\n'
                   'clone(child_stack=NULL, flags=SIGCHLD) = 21\n')
        self.write("t.21", 'execve("/usr/bin/cc", ["cc", "-c", "prog.c", "-o", "prog.o"], []) = 0\n'
                   'clone(child_stack=NULL, flags=SIGCHLD) = 22\n'
                   'clone(child_stack=NULL, flags=SIGCHLD) = 23\n')
        # t.22: line 1 = execve, line 2 = prog.c, then the extra probes.
        self.write("t.22", 'execve("/usr/libexec/gcc/x86_64-linux-gnu/14/cc1", ["cc1", "prog.c"], []) = 0\n'
                   'openat(AT_FDCWD, "prog.c", O_RDONLY) = 3\n' + reader_extra)
        self.write("t.23", 'execve("/usr/bin/as", ["as", "--64", "-o", "prog.o"], []) = 0\n'
                   'openat(AT_FDCWD, "prog.o", O_RDWR|O_CREAT|O_TRUNC, 0666) = 3\n' + writer_extra)

    def test_failed_read_probes_add_no_edge_and_no_finding(self):
        self.traces(reader_extra='openat(AT_FDCWD, "absent.h", O_RDONLY) = -1 ENOENT (No such file or directory)\n'
                    'openat(AT_FDCWD, "denied.h", O_RDONLY) = -1 EACCES (Permission denied)\n')
        database = self.write("db.txt", "# Files\nprog.o: prog.c\n# files hash-table stats:\n")
        result = analyze(self.folder, database, self.ROOT)
        self.assertEqual(result["observed_targets"], ["prog.o"])
        self.assertEqual([edge["dependency"] for edge in result["actual_graph"]], ["prog.c"])
        self.assertEqual(result["actual_graph"][0]["evidence"]["line"], 2)
        self.assertEqual(result["findings"], [])

    def test_failed_open_cannot_satisfy_a_declaration(self):
        self.traces(reader_extra='openat(AT_FDCWD, "absent.h", O_RDONLY) = -1 ENOENT (No such file or directory)\n')
        database = self.write("db.txt", "# Files\nprog.o: prog.c absent.h\n# files hash-table stats:\n")
        result = analyze(self.folder, database, self.ROOT)
        self.assertEqual([(f["type"], f["target"], f["dependency"]) for f in result["findings"]],
                         [("REDUNDANT", "prog.o", "absent.h")])

    def test_failed_write_probe_is_not_a_second_output(self):
        self.traces(writer_extra='openat(AT_FDCWD, "prog.o.tmp", O_WRONLY|O_CREAT|O_TRUNC, 0666) = -1 ENOSPC (No space left on device)\n')
        targets, processes = execution_graph(self.folder, self.ROOT)
        self.assertEqual(sorted(targets), ["prog.o"])
        self.assertEqual(sorted(targets["prog.o"]["dependencies"]), ["prog.c"])
        self.assertEqual([proc["pid"] for proc in processes], [20, 21, 22, 23])
        self.assertEqual(next(proc for proc in processes if proc["pid"] == 23)["job_pid"], 21)

    def test_retry_after_failure_is_recorded_at_the_successful_call(self):
        self.traces(reader_extra='openat(AT_FDCWD, "late.h", O_RDONLY) = -1 ENOENT (No such file or directory)\n'
                    'openat(AT_FDCWD, "late.h", O_RDONLY) = 6\n')
        database = self.write("db.txt", "# Files\nprog.o: prog.c late.h\n# files hash-table stats:\n")
        result = analyze(self.folder, database, self.ROOT)
        self.assertEqual(result["findings"], [])
        edge = next(edge for edge in result["actual_graph"] if edge["dependency"] == "late.h")
        self.assertEqual(edge["evidence"]["line"], 4)
        self.assertEqual(edge["evidence"]["pid"], 22)


if __name__ == "__main__":
    unittest.main()
