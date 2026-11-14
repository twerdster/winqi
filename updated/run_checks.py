"""Run the standard-library test suite and save a portable JSON result."""
from datetime import datetime, timezone
import hashlib
import io
import json
import os
from pathlib import Path
import platform
import sys
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'

from updated.core import generate_codebook, simulate  # noqa: E402


class RecordingResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.records = []

    def addSuccess(self, test):
        super().addSuccess(test)
        self.records.append({'test': test.id(), 'status': 'passed'})

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.records.append({'test': test.id(), 'status': 'failed'})

    def addError(self, test, err):
        super().addError(test, err)
        self.records.append({'test': test.id(), 'status': 'error'})

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self.records.append({'test': test.id(), 'status': 'skipped', 'reason': reason})


def main():
    started = time.perf_counter()
    suite = unittest.defaultTestLoader.discover(str(ROOT / 'updated/tests'))
    log = io.StringIO()
    result = unittest.TextTestRunner(stream=log, verbosity=2,
                                    resultclass=RecordingResult).run(suite)
    # Include deterministic artifacts as executable fixture checks, not only a
    # list of metrics copied from an earlier invocation.
    artifacts = {}
    for filename, fresh in [('codebook.json', generate_codebook().to_dict()),
                            ('simulation.json', simulate())]:
        path = ROOT / 'updated/artifacts' / filename
        artifacts[filename] = {'matches_fresh_output': json.loads(path.read_text()) == fresh,
                               'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
    passed = result.wasSuccessful() and all(a['matches_fresh_output'] for a in artifacts.values())
    paths = ['updated/core.py', 'updated/cli.py', 'updated/run_checks.py',
             'updated/tests/test_core.py', 'updated/tests/test_historical_tables.py',
             'updated/tests/fixtures/historical_cyclic_tables.json']
    payload = {
        'schema': 'winqi-test-results-v1',
        'checked_at_utc': datetime.now(timezone.utc).isoformat(timespec='seconds'),
        'python_version': platform.python_version(),
        'python_implementation': platform.python_implementation(),
        'command': 'python3 updated/run_checks.py',
        'status': 'passed' if passed else 'failed',
        'tests_run': result.testsRun, 'failures': len(result.failures),
        'errors': len(result.errors), 'skipped': len(result.skipped),
        'elapsed_seconds': round(time.perf_counter() - started, 6),
        'tests': result.records,
        'source_sha256': {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in paths},
        'artifacts': artifacts,
        'default_simulation_metrics': simulate()['metrics'],
        'coverage': {
            'independent_channel_all_words_bits': [3, 4, 5, 6],
            'default_policy_codebook_invariants_bits': list(range(3, 12)),
            'physical_single_fault_stream_cases': 6 * 13 * 13 * 5,
            'fault_types': ['flip', 'missing', 'duplicate', 'insert0', 'insert1'],
            'historical_full_dictionary_fixtures_bits': [3, 6, 8, 10, 11],
            'historical_model': 'older variable-length noise model; explicit per-table constant policy',
            'camera_or_hardware_validation': False,
        },
    }
    output = ROOT / 'updated/validation/test-results.json'
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2) + '\n')
    # Any tracebacks printed on failure are local console output only. The
    # portable JSON records test names/statuses without machine paths.
    print(log.getvalue(), end='')
    print(f"{'PASS' if passed else 'FAIL'}; result: updated/validation/test-results.json")
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
