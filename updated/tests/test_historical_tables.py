"""Exact saved-table comparisons using the OLDER commented genNoise model.

This reference is intentionally independent of the updated fixed-width core.
Numerical keys collapse leading zeros/lengths, as the saved MATLAB dicts do.
"""
import hashlib
import json
from pathlib import Path
import unittest
from updated.core import generate_codebook

FIXTURE = Path(__file__).parent / 'fixtures/historical_cyclic_tables.json'


def older_variable_family(raw, bits):
    word = format(raw, f'0{bits}b')
    values = set()
    for phase in range(bits):
        shifted = word[phase:] + word[:phase]
        values.add(int(shifted, 2))
        for position in range(bits):
            changed = list(shifted)
            changed[position] = str(1 - int(changed[position]))
            values.add(int(''.join(changed), 2))
            values.add(int(shifted[:position] + shifted[position + 1:], 2))
            values.add(int(shifted[:position] + shifted[position] + shifted[position:], 2))
    return values


def regenerate_older(bits, exclude_constants):
    dictionary = [0] * (1 << (bits + 1))
    codes = []
    candidates = range(1, (1 << bits) - 1) if exclude_constants else range(1 << bits)
    for raw in candidates:
        values = older_variable_family(raw, bits)
        if all(dictionary[value] == 0 for value in values):
            codes.append(raw)
            for value in values:
                dictionary[value] = raw + 1
    return codes, dictionary


class HistoricalTableTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = json.loads(FIXTURE.read_text())

    def test_fixture_bound_to_exact_preserved_mat_bytes(self):
        root = Path(__file__).resolve().parents[2]
        for table in self.fixture['tables']:
            data = (root / table['source_file']).read_bytes()
            self.assertEqual(hashlib.sha256(data).hexdigest(), table['source_sha256'])
            self.assertEqual(len(table['dictionary_raw_plus_one']), 1 << (table['bits'] + 1))

    def test_five_tables_regenerate_exactly_with_explicit_older_model_policy(self):
        for table in self.fixture['tables']:
            codes, dictionary = regenerate_older(table['bits'], table['constant_policy'] == 'exclude_before_packing')
            self.assertEqual(codes, table['codes_raw'], table['bits'])
            self.assertEqual(dictionary, table['dictionary_raw_plus_one'], table['bits'])

    def test_saved_raw_value_mapping_is_not_modern_beacon_id(self):
        table = next(t for t in self.fixture['tables'] if t['bits'] == 8)
        raw_to_id = {raw + 1: index for index, raw in enumerate(table['codes_raw'], 1)}
        self.assertEqual(table['codes_raw'], [0, 7, 51, 85, 127])
        self.assertEqual(table['dictionary_raw_plus_one'][51], 52)
        self.assertEqual(raw_to_id[52], 3)
        self.assertNotEqual(52, 3)
        for raw, index in zip(table['codes_raw'], range(1, 6)):
            word = format(raw, '08b')
            for phase in range(8):
                observed = int(word[phase:] + word[:phase], 2)
                self.assertEqual(raw_to_id[table['dictionary_raw_plus_one'][observed]], index)

    def test_model_revision_and_constant_policy_changes_are_explicit(self):
        old8 = next(t for t in self.fixture['tables'] if t['bits'] == 8)
        current = generate_codebook(8, None, 'include-constants')
        self.assertEqual([int(w, 2) for w in current.words], [0, 7, 63, 85])
        self.assertNotEqual([int(w, 2) for w in current.words], old8['codes_raw'])
        operational = generate_codebook(8, None, 'nonconstant')
        self.assertEqual([int(w, 2) for w in operational.words], [1, 15, 85, 127])
        old10 = next(t for t in self.fixture['tables'] if t['bits'] == 10)
        self.assertEqual(regenerate_older(10, True)[0], old10['codes_raw'])
        self.assertNotEqual(regenerate_older(10, False)[0], old10['codes_raw'])
        # Active source script starts at 0 and stops before all-ones; separate from default policy.
        self.assertEqual([int(w, 2) for w in generate_codebook(3, None, 'source-script').words], [0])
        self.assertEqual([int(w, 2) for w in generate_codebook(3, None, 'include-constants').words], [0, 7])
        self.assertEqual([int(w, 2) for w in generate_codebook(3, None, 'nonconstant').words], [1])


if __name__ == '__main__':
    unittest.main()
