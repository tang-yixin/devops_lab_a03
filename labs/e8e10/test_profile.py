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

if __name__=='__main__':unittest.main()
