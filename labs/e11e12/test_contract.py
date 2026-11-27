import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import pipeline
import server

class Contracts(unittest.TestCase):
    def report(self):return {'schema_version':'e11e12-1','kind':'incremental-check','commit':'a'*40,'status':'SUCCEEDED'}
    def test_accept_current_report(self):pipeline.check_envelope(self.report(),'a'*40,'incremental-check')
    def test_reject_old_commit(self):
        with self.assertRaisesRegex(pipeline.Failure,'another commit'):pipeline.check_envelope(self.report(),'b'*40)
    def test_reject_schema(self):
        r=self.report();r['schema_version']='old'
        with self.assertRaises(pipeline.Failure):pipeline.check_envelope(r,'a'*40)
    def test_reject_failed_upstream(self):
        r=self.report();r['status']='FAILED'
        with self.assertRaises(pipeline.Failure):pipeline.check_envelope(r,'a'*40)
    def test_reject_wrong_artifact_kind(self):
        with self.assertRaises(pipeline.Failure):pipeline.check_envelope(self.report(),'a'*40,'fixed-md')
    def test_artifact_uses_relative_uri_and_content_hash(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);p=root/'x.json';p.write_text('{}')
            a=pipeline.artifact(p,root,'job-1');self.assertEqual(a['uri'],'artifact://job-1/x.json');self.assertEqual(len(a['sha256']),64)
    def test_existing_evidence_not_overwritten(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'keep').write_text('keep')
            with self.assertRaises(pipeline.Failure):pipeline.execute({},root)
            self.assertEqual((root/'keep').read_text(),'keep')
    def test_changed_artifact_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'r.json';p.write_text('{}')
            with self.assertRaises(pipeline.Failure):pipeline.load_artifact(p,'0'*64)
    def test_same_key_same_request_same_job(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);store=server.Store(root/'jobs')
            request={'mode':'e11-a','repo':str(pipeline.ROOT/'data/p'),'base':'a','target':'b'}
            with patch.object(store.pool,'submit'):
                one=store.submit(request,'same');two=store.submit(request,'same')
                self.assertEqual(one['job_id'],two['job_id'])
                changed=dict(request,target='c')
                with self.assertRaisesRegex(ValueError,'IDEMPOTENCY_CONFLICT'):store.submit(changed,'same')
            store.pool.shutdown()
    def test_api_rejects_repo_outside_data(self):
        with tempfile.TemporaryDirectory() as d:
            store=server.Store(Path(d)/'jobs')
            with self.assertRaises(ValueError):store.submit({'mode':'e11-a','repo':str(Path(d)),'base':'a','target':'b'},'k')
            store.pool.shutdown()



class StudentContract241250061(unittest.TestCase):
    # Personal contract test (241250061). Independent expectation written first:
    # the idempotency-key contract (non-empty, max 128 characters) is enforced before
    # any request validation, so an over-long key can never reach the path/mode
    # checks or occupy job storage.
    def test_overlong_idempotency_key_rejected_before_request_checks(self):
        with tempfile.TemporaryDirectory() as d:
            store=server.Store(Path(d)/'jobs')
            with self.assertRaisesRegex(ValueError,'max 128'):
                store.submit({'mode':'e12','repo':str(d),'base':'a','target':'b'},'k'*129)
            store.pool.shutdown()


class StudentPipelineProfile241250061(unittest.TestCase):
    # Adaptation contract (241250061): a request may carry a project profile that
    # widens snapshot/normalization to its own targets. Independent expectations:
    #  1) execute() installs the profile before snapshot and fails fast with
    #     UNSUPPORTED_PROJECT (no stage recorded) when profile sources are absent;
    #  2) set_profile installs tuple targets from JSON lists; None restores default.
    def test_missing_profile_sources_fail_before_stages(self):
        import lab
        self.addCleanup(lab.set_profile, None)
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); repo = root/'repo'; repo.mkdir()
            lab.run(['git','init','-b','main'], repo)
            lab.run(['git','config','user.name','T'], repo)
            lab.run(['git','config','user.email','t@t'], repo)
            (repo/'README.md').write_text('x\n')
            lab.commit(repo, 'c0')
            sha = lab.run(['git','rev-parse','HEAD'], repo).strip()
            profile = {'targets': [['main.o','src/main.c']],
                       'flags_whitelist': ['-std.c11'], 'key_globs': ['src/*.c'],
                       'ignore': ['.git','*.o','app'], 'build': ['make'], 'run': ['./app'],
                       'expected': '1', 'header': 'include/config.h', 'header_to': 'x',
                       'expected_after': '1'}
            request = {'mode':'e12','repo':str(repo),'base':sha,'target':sha,
                       'candidate':str(root/'candidate.Dockerfile'),'expected_output':'1',
                       'build_timeout':60,'profile':profile}
            result = pipeline.execute(request, root/'out')
            self.assertEqual(result['status'], 'FAILED')
            self.assertEqual(result['error']['code'], 'UNSUPPORTED_PROJECT')
            self.assertEqual(result['stages'], [])

    def test_set_profile_tuples_and_default_restore(self):
        import lab
        self.addCleanup(lab.set_profile, None)
        got = lab.set_profile({'targets': [['a.o','src/a.c']],
                               'flags_whitelist': ['-x'], 'key_globs': ['src/*.c'],
                               'ignore': ['.git','*.o','a'], 'build': ['make'],
                               'run': ['./a'], 'expected': '1', 'header': 'h.h',
                               'header_to': 'x', 'expected_after': '1'})
        self.assertEqual(got, ['a.o'])
        self.assertFalse(lab.profile_is_default())
        self.assertEqual(lab.set_profile(None), ['main.o','helper.o'])
        self.assertTrue(lab.profile_is_default())
class StudentContract241250093(unittest.TestCase):
    # E11-E12 自有契约测试（093 方向）：幂等键空串 / 非字符串输入的拒收分支。
    # 独立预期（运行前写定）：
    #  1) Store.submit 在 mode / repo 路径校验之前先校验键类型与长度，
    #     所以 ''、None、int、list、dict 都抛 ValueError('idempotency_key required, ...')；
    #  2) 拒绝发生在写入 keys/jobs 之前，因此不产生任何 job-* 目录（不占存储）；
    #  3) 被拒的空键不占用命名空间：随后用同一个合法键提交仍可成功并正确幂等；
    #  4) HTTP 层把这类 ValueError 映射为 400（实测见 work/api-client/联调记录.json）。
    def test_empty_and_non_string_keys_rejected_before_job_creation(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); store = server.Store(root/'jobs')
            request = {'mode':'e11-a','repo':str(pipeline.ROOT/'data/p'),'base':'a','target':'b'}
            for key in ['', None, 7, [], {}]:
                with self.assertRaisesRegex(ValueError, 'idempotency_key required'):
                    store.submit(request, key)
            self.assertEqual(store.keys, {})
            self.assertEqual(store.jobs, {})
            self.assertEqual(list((root/'jobs').glob('job-*')), [])
            with patch.object(store.pool, 'submit'):
                ok = store.submit(request, 'e12-241250093-valid')
                self.assertTrue(ok['job_id'].startswith('job-'))
            store.pool.shutdown()

    def test_empty_key_does_not_occupy_the_namespace(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); store = server.Store(root/'jobs')
            request = {'mode':'e12','repo':str(pipeline.ROOT/'data/p'),'base':'a','target':'b'}
            with self.assertRaisesRegex(ValueError, 'idempotency_key required'):
                store.submit(request, '')
            self.assertEqual(store.keys, {})
            with patch.object(store.pool, 'submit'):
                one = store.submit(request, 'e12-241250093-valid')
                two = store.submit(request, 'e12-241250093-valid')
                self.assertEqual(one['job_id'], two['job_id'])
            self.assertEqual(len(store.keys), 1)
            store.pool.shutdown()

if __name__=='__main__':unittest.main()
