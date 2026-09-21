#!/usr/bin/env python3
"""Validate the repository's JSON Schema subset and cross-file semantics.

No third-party packages. This is NOT a general JSON Schema implementation.
Unknown schema keywords fail closed; task.schema.json is portable Draft 2020-12.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent
SCHEMA = json.loads((ROOT / 'contracts/task.schema.json').read_text())


class Invalid(ValueError):
    def __init__(self, code, message):
        self.code = code
        super().__init__(f'{code}: {message}')


KEYWORDS = {'$schema', '$id', 'title', '$defs', '$ref', 'oneOf', 'type',
            'properties', 'required', 'additionalProperties', 'items',
            'minItems', 'uniqueItems', 'minimum', 'minLength', 'pattern',
            'format', 'const', 'enum'}


def audit_schema(s):
    unknown = set(s) - KEYWORDS
    if unknown:
        raise RuntimeError(f'Unsupported schema keywords: {unknown}')
    for k in ('$defs', 'properties'):
        for child in s.get(k, {}).values():
            audit_schema(child)
    for child in s.get('oneOf', []):
        audit_schema(child)
    if 'items' in s:
        audit_schema(s['items'])
    if '$ref' in s:
        if not s['$ref'].startswith('#/$defs/') or s['$ref'][8:] not in SCHEMA['$defs']:
            raise RuntimeError(f'Unsupported reference: {s["$ref"]}')
    if 'format' in s and s['format'] != 'uri':
        raise RuntimeError('Unsupported format')


def fail(message, code='INPUT_1001'):
    raise Invalid(code, message)


def check(value, s, path='$'):
    if '$ref' in s:
        check(value, SCHEMA['$defs'][s['$ref'][8:]], path)
    if 'oneOf' in s:
        count = 0
        for branch in s['oneOf']:
            try:
                check(value, branch, path)
                count += 1
            except Invalid:
                pass
        if count != 1:
            fail(f'{path}: expected exactly one schema branch, matched {count}')
    types = {'object': lambda x: isinstance(x, dict),
             'array': lambda x: isinstance(x, list),
             'string': lambda x: isinstance(x, str),
             'integer': lambda x: type(x) is int,
             'boolean': lambda x: type(x) is bool,
             'null': lambda x: x is None}
    if 'type' in s:
        names = s['type'] if isinstance(s['type'], list) else [s['type']]
        if not any(types[n](value) for n in names):
            fail(f'{path}: expected {names}')
    if 'const' in s and json.dumps(value, sort_keys=True) != json.dumps(s['const'], sort_keys=True):
        fail(f'{path}: const mismatch')
    if 'enum' in s and json.dumps(value, sort_keys=True) not in [json.dumps(x, sort_keys=True) for x in s['enum']]:
        fail(f'{path}: enum mismatch')
    if isinstance(value, dict):
        for key in s.get('required', []):
            if key not in value:
                fail(f'{path}.{key}: required')
        props = s.get('properties', {})
        if s.get('additionalProperties') is False and set(value) - set(props):
            fail(f'{path}: unexpected fields {set(value) - set(props)}')
        for key, child in props.items():
            if key in value:
                check(value[key], child, path + '.' + key)
    if isinstance(value, list):
        if len(value) < s.get('minItems', 0):
            fail(f'{path}: too few items')
        if s.get('uniqueItems') and len({json.dumps(x, sort_keys=True) for x in value}) != len(value):
            fail(f'{path}: duplicate items')
        for i, item in enumerate(value):
            if 'items' in s:
                check(item, s['items'], f'{path}[{i}]')
    if isinstance(value, str):
        if len(value) < s.get('minLength', 0):
            fail(f'{path}: string too short')
        if 'pattern' in s and not re.search(s['pattern'], value):
            fail(f'{path}: pattern mismatch')
        if s.get('format') == 'uri':
            try:
                u = urlsplit(value)
                if not u.scheme or re.search(r'\s', value):
                    fail(f'{path}: invalid absolute URI')
            except ValueError:
                fail(f'{path}: malformed URI')
    if type(value) is int and 'minimum' in s and value < s['minimum']:
        fail(f'{path}: below minimum')


def read_artifact(uri):
    # Only local artifact:// references are resolved. Network is never accessed.
    u = urlsplit(uri)
    if u.scheme != 'artifact' or not u.netloc or u.query or u.fragment:
        fail('Unsupported artifact URI: ' + uri, 'ARTIFACT_2001')
    root = (ROOT / 'artifacts').resolve()
    path = (root / u.netloc / u.path.lstrip('/')).resolve()
    if not path.is_relative_to(root) or not path.is_file():
        fail('Missing or out-of-root artifact: ' + uri, 'ARTIFACT_2001')
    index = json.loads((root / 'index.json').read_text())
    records = [r for r in index if r['uri'] == uri]
    if len(records) != 1 or hashlib.sha256(path.read_bytes()).hexdigest() != records[0]['sha256']:
        fail('Artifact unregistered or hash mismatch: ' + uri, 'ARTIFACT_2001')
    return path, records[0]


def report_check(report):
    check(report, SCHEMA['$defs']['errorReport'])
    ids = set()
    for f in report['findings']:
        if f['commit'] != report['repository']['commit']:
            fail('Finding/report commit mismatch', 'INPUT_1002')
        if f['finding_id'] in ids:
            fail('Duplicate finding_id')
        ids.add(f['finding_id'])
        evidence = f['evidence']
        expected = (True, False) if f['type'] == 'MISSING' else (False, True)
        if (evidence['actual_dependency'], evidence['declared_dependency']) != expected:
            fail('Finding type disagrees with evidence')


def semantics(doc, resolve=True):
    if 'findings' in doc:
        report_check(doc)
    if 'input' not in doc:
        return
    if doc.get('status') == 'TIMED_OUT' and doc['error']['code'] != 'EXEC_4002':
        fail('TIMED_OUT requires EXEC_4002')
    inp = doc['input']
    kind = doc['job_type']
    env = inp.get('environment')
    if env and inp['build']['working_directory'] != env['project_root']:
        fail('Working directory does not match environment project_root', 'INPUT_1003')
    if kind == 'INCREMENTAL_CHECK':
        baseline = inp['baseline']
        if baseline['commit'] != inp['base_commit']:
            fail('Baseline/base_commit mismatch', 'INPUT_1002')
        if baseline['configuration_id'] != env['configuration_id']:
            fail('Baseline/environment configuration mismatch', 'INPUT_1003')
        if resolve:
            for key in ['actual_graph_uri', 'declared_graph_uri']:
                path, meta = read_artifact(baseline[key])
                expected_type = 'ACTUAL_GRAPH' if key == 'actual_graph_uri' else 'DECLARED_GRAPH'
                if meta['type'] != expected_type:
                    fail('Baseline artifact type mismatch', 'INPUT_1004')
                if meta['repository'] != {**inp['repository'], 'commit': inp['base_commit']}:
                    fail('Baseline artifact repository/commit mismatch', 'INPUT_1002')
                if meta['configuration_id'] != env['configuration_id']:
                    fail('Baseline artifact configuration mismatch', 'INPUT_1003')
    if kind == 'REPAIR' and resolve:
        path, meta = read_artifact(inp['md_report_uri'])
        report = json.loads(path.read_text())
        report_check(report)
        if meta['type'] != 'ERROR_REPORT':
            fail('Expected ERROR_REPORT artifact')
        if report['repository'] != inp['repository'] or meta['repository'] != inp['repository']:
            fail('Report repository/commit mismatch', 'INPUT_1002')
        if report['configuration_id'] != env['configuration_id'] or meta['configuration_id'] != env['configuration_id']:
            fail('Report configuration mismatch', 'INPUT_1003')
        if not report['findings'] or any(f['type'] != 'MISSING' for f in report['findings']):
            fail('REPAIR accepts a nonempty MD-only report', 'INPUT_1004')
        if any(f['location']['file'] not in inp['makefiles'] for f in report['findings']):
            fail('Finding location absent from makefiles', 'INPUT_1004')
    output = doc.get('output')
    if not output:
        return
    for key in ['build_result', 'verify_result', 'test_result']:
        if key in output and output[key]['passed'] != (output[key]['exit_code'] == 0):
            fail('passed/exit_code mismatch')
    if kind == 'DRAFT':
        if not output['build_result']['passed'] or not output['verify_result']['passed']:
            fail('DRAFT success requires build and verify success')
        if len(output['iterations']) > inp['max_iterations']:
            fail('Iteration limit exceeded')
    if kind == 'REPAIR':
        rc = output['recheck_result']
        if rc['passed'] != (rc['remaining_missing_count'] == 0):
            fail('Recheck pass/count mismatch', 'REPAIR_6001')
        if resolve:
            path, _ = read_artifact(rc['error_report_uri'])
            report = json.loads(path.read_text()); report_check(report)
            if report['repository'] != inp['repository'] or report['configuration_id'] != env['configuration_id']:
                fail('Recheck source/configuration mismatch', 'REPAIR_6001')
            if sum(f['type'] == 'MISSING' for f in report['findings']) != rc['remaining_missing_count']:
                fail('Recheck count/report mismatch', 'REPAIR_6001')
        all_passed = output['build_result']['passed'] and output['test_result']['passed'] and rc['passed']
        if output['accepted'] and (not all_passed or output['rejection_reason'] is not None):
            fail('Accepted patch must pass build/test/recheck without rejection reason', 'REPAIR_6001')
        if not output['accepted'] and not output['rejection_reason']:
            fail('Rejected candidate must include reason', 'REPAIR_6001')


def validate(doc, resolve=True):
    check(doc, SCHEMA)
    semantics(doc, resolve)


def all_examples():
    rows = json.loads((ROOT / 'contracts/examples/manifest.json').read_text())
    for row in rows:
        doc = json.loads((ROOT / row['path']).read_text())
        try:
            validate(doc)
        except Invalid as e:
            if row['valid'] or e.code != row['error_code']:
                raise AssertionError(f'{row["path"]}: unexpected {e}') from e
        else:
            if not row['valid']:
                raise AssertionError(f'{row["path"]}: invalid example was accepted')
    for meta in json.loads((ROOT / 'artifacts/index.json').read_text()):
        check(meta, SCHEMA['$defs']['artifact'])
        read_artifact(meta['uri'])
    # Resolve all URI references, including logs and evidence, in positive examples.
    def walk(x):
        if isinstance(x, dict):
            for v in x.values(): walk(v)
        elif isinstance(x, list):
            for v in x: walk(v)
        elif isinstance(x, str) and x.startswith('artifact://'):
            read_artifact(x)
    for row in rows:
        if row['valid']: walk(json.loads((ROOT / row['path']).read_text()))
    print(f'PASS: {len(rows)} examples ({sum(x["valid"] for x in rows)} valid, '
          f'{sum(not x["valid"] for x in rows)} expected rejections); artifact references and SHA-256 verified.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('file', nargs='?', type=Path)
    parser.add_argument('--structure-only', action='store_true', help='Skip cross-file semantics; no integration guarantee')
    args = parser.parse_args()
    audit_schema(SCHEMA)
    if args.file:
        data = json.loads(args.file.read_text())
        if args.structure_only: check(data, SCHEMA)
        else: validate(data)
        print('PASS:', args.file)
    else:
        if args.structure_only: parser.error('--structure-only requires a file')
        all_examples()


if __name__ == '__main__':
    try:
        main()
    except (Invalid, AssertionError, OSError, ValueError, RuntimeError) as e:
        print('FAIL:', e, file=sys.stderr)
        sys.exit(1)
