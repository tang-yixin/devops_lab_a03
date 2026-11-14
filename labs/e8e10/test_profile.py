import json, tempfile, unittest
from pathlib import Path
from lab import fixture,scan,patch,commit

class ProfileTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.p=Path(self.tmp.name)/'sample';fixture(self.p)

    def test_independent_known_edges(self):
        r=scan(self.p)
        self.assertEqual(r['actual']['main.o'],['config.h','main.c'])
        self.assertEqual({(f['type'],f['dependency']) for f in r['findings']},{('MISSING','config.h'),('REDUNDANT','unused.h')})

    def test_unchanged_reuses_both_targets(self):
        r=scan(self.p,scan(self.p));self.assertEqual(r['reused'],['main.o','helper.o']);self.assertEqual(r['refreshed'],[])

    def test_include_added_invalidates_cache(self):
        old=scan(self.p)
        (self.p/'main.c').write_text('#include "extra.h"\n'+(self.p/'main.c').read_text());commit(self.p,'new include')
        r=scan(self.p,old)
        self.assertIn(['MISSING','main.o','extra.h'],r['added']);self.assertEqual(len(r['refreshed']),2)

    def test_patch_preserves_redundant_dependency(self):
        r=scan(self.p);diff,plan=patch(self.p,r)
        self.assertIn('+main.o: main.c unused.h config.h',diff)
        self.assertNotIn('-\tgcc',diff)
        self.assertNotIn('config.h',(self.p/'Makefile').read_text())

    def test_old_report_rejected(self):
        r=scan(self.p);r['commit']='0'*40
        with self.assertRaisesRegex(ValueError,'STALE_REPORT'):patch(self.p,r)

    def test_unsafe_dependency_rejected(self):
        r=scan(self.p);r['findings']=[{'type':'MISSING','target':'main.o','dependency':'../outside.h'}]
        with self.assertRaisesRegex(ValueError,'UNSAFE_PATH'):patch(self.p,r)

    def test_unsupported_configuration_rejected(self):
        (self.p/'Makefile').write_text((self.p/'Makefile').read_text().replace('-O0','-include unknown.h'))
        with self.assertRaisesRegex(ValueError,'UNSUPPORTED_FLAGS'):scan(self.p)

class StudentE8A241250061(unittest.TestCase):
    # E8 student tests (241250061): test1 adapted from manual-08 StudentE8A; test2 own scenario (new header, indirect include).
    def test_declaration_change_reuses_actual_graph(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'sample';fixture(p);old=scan(p)
            f=p/'Makefile'
            f.write_text(f.read_text().replace('main.c unused.h','main.c unused.h config.h'))
            commit(p,'student: add missing declaration');result=scan(p,old)
            self.assertEqual(result['actual'],old['actual'])
            self.assertEqual(set(result['reused']),{'main.o','helper.o'})
            self.assertEqual(result['refreshed'],[])
            self.assertEqual({(x['type'],x['target'],x['dependency']) for x in result['findings']},{('REDUNDANT','main.o','unused.h')})

    def test_indirect_include_new_header_added_missing(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'sample';fixture(p);old=scan(p)
            (p/'tweak.h').write_text('#define TWEAK 1'+chr(10))
            cfg=p/'config.h';cfg.write_text('#include "tweak.h"'+chr(10)+cfg.read_text())
            commit(p,'student: indirect include via new header');r=scan(p,old)
            self.assertEqual(set(r['refreshed']),{'main.o','helper.o'})
            self.assertIn('tweak.h',r['actual']['main.o'])
            self.assertEqual(r['actual']['helper.o'],['helper.c'])
            self.assertIn(['MISSING','main.o','tweak.h'],r['added'])
            full=scan(p)
            self.assertEqual((r['actual'],r['declared'],r['findings']),(full['actual'],full['declared'],full['findings']))

class StudentE9A241250061(unittest.TestCase):
    # E9 student tests (241250061): test1 adapted from manual-08 StudentE9A; test2 own scenario (remove redundant declaration).
    def test_include_inside_header_invalidates(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'sample';fixture(p);old=scan(p)
            (p/'config.h').write_text('#include '+chr(34)+'extra.h'+chr(34)+chr(10)+'#define VALUE 1'+chr(10))
            commit(p,'student: header includes extra');result=scan(p,old)
            self.assertEqual(result['actual']['main.o'],['config.h','extra.h','main.c'])
            self.assertIn(['MISSING','main.o','extra.h'],result['added'])
            self.assertEqual(set(result['refreshed']),{'main.o','helper.o'})

    def test_remove_redundant_declaration_resolves_rd(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'sample';fixture(p);old=scan(p)
            f=p/'Makefile'
            f.write_text(f.read_text().replace('main.c unused.h','main.c'))
            commit(p,'student: remove redundant declaration');r=scan(p,old)
            self.assertEqual(set(r['reused']),{'main.o','helper.o'});self.assertEqual(r['refreshed'],[])
            self.assertEqual(sorted(r['resolved']),[['REDUNDANT','main.o','unused.h']]);self.assertEqual(r['added'],[])
            self.assertEqual({(x['type'],x['target'],x['dependency']) for x in r['findings']},{('MISSING','main.o','config.h')})

class StudentE8A241250093(unittest.TestCase):
    # E8 own scenario (241250093): a direct #include in helper.c must create a NEW
    # MISSING on helper.o, not just on main.o. Expectation written BEFORE running.
    def test_direct_include_in_helper_adds_missing_on_helper(self):
        # Independent expectation:
        # 1) a new preprocessor directive changes the cache key -> conservative
        #    refresh of BOTH object targets, no reuse;
        # 2) gcc -MM now reports extra.h for helper.o, whose declaration is still
        #    helper.c -> MISSING(helper.o, extra.h) appears in `added`;
        # 3) main.o's real graph and the original two findings stay unchanged;
        # 4) incremental result equals a fresh full scan (actual/declared/findings).
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'sample'
            fixture(p)
            old=scan(p)
            h=p/'helper.c'
            h.write_text('#include "extra.h"\n'+h.read_text())
            commit(p,'student: direct include in helper.c')
            r=scan(p,old)
            self.assertEqual(r['reused'],[])
            self.assertEqual(set(r['refreshed']),{'main.o','helper.o'})
            self.assertEqual(r['actual']['helper.o'],['extra.h','helper.c'])
            self.assertEqual(r['actual']['main.o'],['config.h','main.c'])
            self.assertIn(['MISSING','helper.o','extra.h'],r['added'])
            self.assertIn({'type':'MISSING','target':'helper.o','dependency':'extra.h'},r['findings'])
            self.assertIn({'type':'MISSING','target':'main.o','dependency':'config.h'},r['findings'])
            full=scan(p)
            self.assertEqual((r['actual'],r['declared'],r['findings']),
                             (full['actual'],full['declared'],full['findings']))

class StudentE9A241250093(unittest.TestCase):
    # E9 own scenario (241250093): replacing the declaration line with the exact
    # real dependency set (add config.h AND drop unused.h) resolves BOTH findings.
    def test_declaration_line_replaces_both_findings(self):
        # Independent expectation:
        # 1) a declaration-line edit does not change the key (recipes/flags/directives
        #    identical) -> the real graph is REUSED, not refreshed;
        # 2) declared(main.o) == actual(main.o) == {config.h, main.c} -> findings=[];
        # 3) resolved = the two old findings (MISSING config.h, REDUNDANT unused.h),
        #    added is empty;
        # 4) helper.o stays clean.
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'sample'
            fixture(p)
            old=scan(p)
            f=p/'Makefile'
            f.write_text(f.read_text().replace('main.c unused.h','main.c config.h'))
            commit(p,'student: declare config.h and drop unused.h')
            r=scan(p,old)
            self.assertEqual(r['reused'],['main.o','helper.o'])
            self.assertEqual(r['refreshed'],[])
            self.assertEqual(r['declared']['main.o'],['config.h','main.c'])
            self.assertEqual(r['findings'],[])
            self.assertEqual(r['added'],[])
            self.assertEqual(sorted(r['resolved']),
                             [['MISSING','main.o','config.h'],['REDUNDANT','main.o','unused.h']])
            self.assertEqual(r['declared']['helper.o'],['helper.c'])

if __name__=='__main__':unittest.main()
