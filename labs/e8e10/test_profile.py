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

class StudentE8A241250107(unittest.TestCase):
    def test_include_and_declaration_added_simultaneously_no_new_finding(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'sample'
            fixture(p)
            old=scan(p)
            (p/'main.c').write_text('#include "extra.h"\n'+(p/'main.c').read_text())
            f=p/'Makefile'
            f.write_text(f.read_text().replace('main.c unused.h','main.c unused.h extra.h'))
            commit(p,'student: include + declaration added together')
            r=scan(p,old)
            self.assertEqual(r['reused'],[])
            self.assertEqual(set(r['refreshed']),{'main.o','helper.o'})
            self.assertEqual(r['actual']['main.o'],['config.h','extra.h','main.c'])
            self.assertEqual(r['added'],[])
            self.assertEqual({(x['type'],x['target'],x['dependency']) for x in r['findings']},
                             {('MISSING','main.o','config.h'),('REDUNDANT','main.o','unused.h')})
            full=scan(p)
            self.assertEqual((r['actual'],r['declared'],r['findings']),
                             (full['actual'],full['declared'],full['findings']))

class StudentE9A241250107(unittest.TestCase):
    def test_config_value_change_refreshes_but_findings_unchanged(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'sample'
            fixture(p)
            old=scan(p)
            (p/'config.h').write_text('#define VALUE 2\n')
            commit(p,'student: config value 1 to 2')
            r=scan(p,old)
            self.assertEqual(r['reused'],[])
            self.assertEqual(set(r['refreshed']),{'main.o','helper.o'})
            self.assertEqual(r['actual'],old['actual'])
            self.assertEqual(r['declared'],old['declared'])
            self.assertEqual(r['findings'],old['findings'])
            self.assertEqual(r['added'],[])
            self.assertEqual(r['resolved'],[])

class StudentE8A241250106(unittest.TestCase):
    # E8 方向（241250106）：删除未被任何源文件包含的 extra.h 文件。
    # 先写独立预期：extra.h 只是躺在项目里，从未被 #include，所以
    #  1) 缓存指纹（key.directives 按文件名收录所有 .c/.h）必然变化，两个目标都不能复用；
    #  2) 真实依赖集与声明依赖集都不含 extra.h，因此实际图、声明图、MD/RD 发现集合全部不变；
    #  3) 增量结果应与一次全量 scan 完全一致（actual/declared/findings）。
    def test_removing_unincluded_header_refreshes_without_new_findings(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'sample';fixture(p);old=scan(p)
            (p/'extra.h').unlink()
            commit(p,'student: remove unincluded extra.h')
            r=scan(p,old)
            self.assertNotEqual(r['key'],old['key'])
            self.assertNotIn('extra.h',r['key']['directives'])
            self.assertIn('extra.h',old['key']['directives'])
            self.assertEqual(r['reused'],[])
            self.assertEqual(set(r['refreshed']),{'main.o','helper.o'})
            self.assertEqual(r['actual'],old['actual'])
            self.assertEqual(r['declared'],old['declared'])
            self.assertEqual(r['findings'],old['findings'])
            self.assertEqual(r['added'],[])
            self.assertEqual(r['resolved'],[])
            self.assertNotIn('extra.h',r['actual']['main.o'])
            self.assertNotIn('extra.h',r['actual']['helper.o'])
            full=scan(p)
            self.assertEqual((r['actual'],r['declared'],r['findings']),(full['actual'],full['declared'],full['findings']))

class StudentE9A241250106(unittest.TestCase):
    # E9 方向（241250106）：Makefile 的 CFLAGS 由 -O0 改为 -O1。
    # 先写独立预期：编译器选项属于依赖分析的配置身份，
    #  1) key.flags 变化 -> 两个目标保守刷新、无一复用；
    #  2) 编译选项不影响 #include 关系，实际图与声明图不变，MD/RD 发现集合与 added/resolved 都不变；
    #  3) 增量与全量一致；把 CFLAGS 换成白名单外的值必须显式拒绝，不能静默复用旧图。
    def test_cflags_change_refreshes_both_targets_keeping_findings(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'sample';fixture(p);old=scan(p)
            self.assertEqual(old['key']['flags'],'-O0')
            f=p/'Makefile'
            f.write_text(f.read_text().replace('CFLAGS = -O0','CFLAGS = -O1'))
            commit(p,'student: switch CFLAGS to -O1')
            r=scan(p,old)
            self.assertEqual(r['key']['flags'],'-O1')
            self.assertNotEqual(r['key'],old['key'])
            self.assertEqual(r['reused'],[])
            self.assertEqual(set(r['refreshed']),{'main.o','helper.o'})
            self.assertEqual(r['actual'],old['actual'])
            self.assertEqual(r['declared'],old['declared'])
            self.assertEqual(r['findings'],old['findings'])
            self.assertEqual(r['added'],[])
            self.assertEqual(r['resolved'],[])
            full=scan(p)
            self.assertEqual((r['actual'],r['declared'],r['findings']),(full['actual'],full['declared'],full['findings']))
            f.write_text(f.read_text().replace('CFLAGS = -O1','CFLAGS = -O7'))
            with self.assertRaisesRegex(ValueError,'UNSUPPORTED_FLAGS'):
                scan(p,r)

class StudentE10A241250061(unittest.TestCase):
    # E10 自主场景（241250061）：新增 deep.h 并让 config.h 间接包含它（链式第3个头）。
    # 独立预期（运行前写定）：
    #  1) 新文件 + config.h 指令行变化 => 缓存 key 必变 => 两目标全部保守刷新（reused=0）；
    #  2) gcc -MM 观察 main.o 实际图新增 deep.h，声明未含 => added 恰为 MISSING main.o deep.h；
    #  3) 原有 MD config.h 与 RD unused.h 均保留，resolved 为空；
    #  4) helper.c 不含任何 include，helper.o 实际图保持 [helper.c]；
    #  5) 增量结果与全量 scan 在 actual/declared/findings 三集合上完全一致。
    def test_chained_third_header_refreshes_and_matches_full(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'sample'
            fixture(p);old=scan(p)
            (p/'deep.h').write_text('#define DEEP 1'+chr(10))
            cfg=p/'config.h';cfg.write_text('#include '+chr(34)+'deep.h'+chr(34)+chr(10)+cfg.read_text())
            commit(p,'student: chained third header via config.h')
            r=scan(p,old)
            self.assertEqual(r['reused'],[])
            self.assertEqual(set(r['refreshed']),{'main.o','helper.o'})
            self.assertEqual(r['actual']['main.o'],['config.h','deep.h','main.c'])
            self.assertEqual(r['actual']['helper.o'],['helper.c'])
            self.assertEqual(r['added'],[['MISSING','main.o','deep.h']])
            self.assertEqual(r['resolved'],[])
            self.assertIn({'type':'MISSING','target':'main.o','dependency':'config.h'},r['findings'])
            self.assertIn({'type':'REDUNDANT','target':'main.o','dependency':'unused.h'},r['findings'])
            full=scan(p)
            self.assertEqual((r['actual'],r['declared'],r['findings']),(full['actual'],full['declared'],full['findings']))



class StudentRealProfile241250061(unittest.TestCase):
    # E11-E12 real-project adaptation (241250061): profiles extend the
    # declarations/scan target mapping to multi-directory C/Make projects.
    # Independent expectations written BEFORE running:
    #  1) A src/ + include/ profile drives gcc -MM per (target, source) pair with
    #     the profile's own CFLAGS whitelist (":=" assignments now parsed);
    #  2) the fingerprint covers the profile globs: a header edit refreshes both
    #     targets, an unchanged rescan reuses both;
    #  3) patch() still repairs the missing header on the right rule line;
    #  4) set_profile(None) fully restores the default teaching profile.
    def setUp(self):
        import lab
        self.addCleanup(lab.set_profile, None)
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.p = Path(self.tmp.name) / 'sample'
        src = self.p/'src'; inc = self.p/'include'
        src.mkdir(parents=True); inc.mkdir(parents=True)
        (src/'calc.c').write_text('#include "cfg.h' + '"' + '\n#include "extra.h' + '"' + '\nint main(void){return CFG;}\n')
        (src/'io.c').write_text('#include "io.h' + '"' + '\nint io(void){return 0;}\n')
        (inc/'cfg.h').write_text('#define CFG 0\n')
        (inc/'extra.h').write_text('#define EXTRA 1\n')
        (inc/'io.h').write_text('int io(void);\n')
        (self.p/'Makefile').write_text(
            'CFLAGS := -std=c11 -Iinclude\n'
            'calc: calc.o io.o\n\tgcc calc.o io.o -o calc\n'
            'calc.o: src/calc.c include/cfg.h\n\tgcc $(CFLAGS) -c src/calc.c -o calc.o\n'
            'io.o: src/io.c include/io.h\n\tgcc $(CFLAGS) -c src/io.c -o io.o\n'
            '.PHONY: clean\nclean:\n\trm -f calc.o io.o calc\n')
        lab.run(['git','init','-b','main'], self.p)
        lab.run(['git','config','user.name','T'], self.p)
        lab.run(['git','config','user.email','t@t'], self.p)
        lab.commit(self.p, 'c0')
        lab.set_profile({'targets': [['calc.o','src/calc.c'], ['io.o','src/io.c']],
                         'flags_whitelist': ['-std=c11 -Iinclude'],
                         'key_globs': ['src/*.c','include/*.h'],
                         'ignore': ['.git','*.o','calc'],
                         'build': ['make','all'], 'run': ['./calc'],
                         'expected': '0', 'fail_expected': '0',
                         'header': 'include/cfg.h', 'header_search': '#define CFG 0',
                         'header_repl': '#define CFG 2', 'expected_after': '2'})

    def test_profile_scan_multidir_targets_and_flags(self):
        r = scan(self.p)
        self.assertEqual(r['actual']['calc.o'], ['include/cfg.h','include/extra.h','src/calc.c'])
        self.assertEqual(r['declared']['calc.o'], ['include/cfg.h','src/calc.c'])
        self.assertEqual(r['actual']['io.o'], ['include/io.h','src/io.c'])
        self.assertEqual(r['findings'],
                         [{'type':'MISSING','target':'calc.o','dependency':'extra.h'}])

    def test_profile_header_change_refreshes_and_patch_repairs(self):
        import lab
        old = scan(self.p)
        (self.p/'include/cfg.h').write_text('#define CFG 2\n')
        commit(self.p, 'header change')
        r = scan(self.p, old)
        self.assertEqual(r['reused'], [])
        self.assertEqual(set(r['refreshed']), {'calc.o','io.o'})
        diff, edits = lab.patch(self.p, r)
        self.assertIn('+calc.o: src/calc.c include/cfg.h include/extra.h', diff)
        self.assertNotIn('extra.h', (self.p/'Makefile').read_text())

    def test_default_profile_restored(self):
        import lab
        lab.set_profile(None)
        self.assertTrue(lab.profile_is_default())
        with tempfile.TemporaryDirectory() as d:
            q = Path(d)/'sample'; fixture(q)
            r = scan(q)
            self.assertEqual(r['actual']['main.o'], ['config.h','main.c'])
            self.assertEqual({(f['type'],f['dependency']) for f in r['findings']},
                             {('MISSING','config.h'), ('REDUNDANT','unused.h')})
if __name__=='__main__':unittest.main()
