import copy
import itertools
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from updated.core import Codebook, StreamDecoder, cyclic_noise_family, generate_codebook, noise_variants, rotations, simulate


def physical_family(word):
    """Independent channel construction: edit a long repeated transmitted stream."""
    n = len(word)
    stream = word * 5
    result = set()
    for phase in range(n):
        start = n + phase
        result.add(stream[start:start + n])
        for index in range(start, start + n):
            flipped = stream[:index] + str(1 - int(stream[index])) + stream[index + 1:]
            result.add(flipped[start:start + n])
            missed = stream[:index] + stream[index + 1:]
            result.add(missed[start:start + n])
            for bit in '01':
                inserted = stream[:index] + bit + stream[index:]
                result.add(inserted[start:start + n])
    return result


class CodebookTests(unittest.TestCase):
    def test_noise_matches_independent_physical_channel_exhaustively(self):
        for n in range(3, 7):
            for bits in itertools.product('01', repeat=n):
                word = ''.join(bits)
                self.assertEqual(cyclic_noise_family(word), physical_family(word), word)

    def test_rotation_order_and_periodic_words(self):
        self.assertEqual(rotations('0101'), ('0101', '1010'))
        self.assertEqual(rotations('001'), ('001', '010', '100'))
        self.assertTrue(all(len(v) == 4 for v in noise_variants('0011')))

    def test_code_invariants_and_disjoint_families(self):
        for n in range(3, 12):
            book = generate_codebook(n, None)
            occupied = set()
            for beacon_id, word in enumerate(book.words, 1):
                self.assertGreater(len(set(word)), 1)
                self.assertEqual(min(rotations(word)), word)
                family = physical_family(word)
                self.assertTrue(occupied.isdisjoint(family))
                occupied.update(family)
                for phase in rotations(word):
                    self.assertEqual(book.decode_window(phase), beacon_id)
            self.assertEqual(occupied, set(book.lookup))

    def test_modelled_error_streams_all_ids_phases_positions(self):
        book = generate_codebook(13, 6)
        n = book.bits
        for beacon_id, word in enumerate(book.words, 1):
            for phase in range(n):
                clean = (word * 6)[phase:phase + n * 5]
                for offset in range(n):
                    position = 2 * n + offset
                    modified = {
                        'flip': clean[:position] + str(1 - int(clean[position])) + clean[position + 1:],
                        'missing': clean[:position] + clean[position + 1:],
                        'duplicate': clean[:position] + clean[position] + clean[position:],
                        'insert0': clean[:position] + '0' + clean[position:],
                        'insert1': clean[:position] + '1' + clean[position:],
                    }
                    for kind, stream in modified.items():
                        decoder = StreamDecoder(book)
                        for index, bit in enumerate(stream):
                            decision = decoder.push(bit)
                            if index >= n - 1:
                                self.assertEqual(decision['decoded_id'], beacon_id,
                                                 (beacon_id, phase, offset, kind, decision))

    def test_unknown_and_warmup_are_explicit(self):
        book = generate_codebook()
        unknown = next(f'{i:013b}' for i in range(1 << 13) if f'{i:013b}' not in book.lookup)
        decoder = StreamDecoder(book)
        for bit in unknown[:-1]:
            self.assertEqual(decoder.push(bit)['reason'], 'warming_up')
        final = decoder.push(unknown[-1])
        self.assertEqual(final['decoded_id'], 0)
        self.assertEqual(final['reason'], 'unknown')

    def test_ambiguous_invalid_or_noncanonical_codebooks_are_rejected(self):
        for kwargs in [dict(bits=2, words=('01',)), dict(bits=5, words=('00000',)),
                       dict(bits=5, words=('00001', '00101')), dict(bits=5, words=('00010',))]:
            with self.assertRaises(ValueError):
                Codebook(**kwargs)
        for bits, count in [(True, 1), (3, 0), (3, True), (3, 100), (16, 1)]:
            with self.assertRaises(ValueError):
                generate_codebook(bits, count)
        with self.assertRaises(ValueError):
            generate_codebook(5, 1, 'not-a-policy')
        decoder = StreamDecoder(generate_codebook())
        for bad in [None, True, 2, -1, '', '10', 'x', 0.0]:
            with self.assertRaises(ValueError):
                decoder.push(bad)
        with self.assertRaises(ValueError):
            decoder.codebook.decode_window('01')
        with self.assertRaises(TypeError):
            decoder.codebook.lookup['0000000000000'] = 999

    def test_codebook_json_roundtrip_and_metadata_validation(self):
        book = generate_codebook()
        self.assertEqual(Codebook.from_dict(json.loads(json.dumps(book.to_dict()))), book)
        altered = copy.deepcopy(book.to_dict())
        altered['codes'][0]['beacon_id'] = 2
        with self.assertRaises(ValueError):
            Codebook.from_dict(altered)
        altered = copy.deepcopy(book.to_dict())
        altered['codes'][0]['raw_code_value'] = 999
        with self.assertRaises(ValueError):
            Codebook.from_dict(altered)

    def test_constant_noise_is_not_a_background_detector(self):
        # Removing constant candidates does not remove their words from another code's noise ball.
        self.assertEqual(generate_codebook().decode_window('0' * 13), 1)


class SimulationTests(unittest.TestCase):
    def test_default_fixture_actual_events_and_independent_metrics(self):
        result = simulate()
        book = Codebook.from_dict(result['codebook'])
        histories = {i: '' for i in range(1, 7)}
        reference = {word: beacon_id for beacon_id, code in enumerate(book.words, 1)
                     for word in physical_family(code)}
        counts = {'observation_events': 0, 'warming_up_events': 0, 'correct_events': 0,
                  'incorrect_events': 0, 'unknown_events': 0}
        faults = {'flip': 0, 'missing': 0, 'duplicate': 0}
        last_fault = {}
        for index, sample in enumerate(result['samples']):
            self.assertEqual(sample['sample_index'], index)
            self.assertEqual(sample['frame_index'], index * 3)
            self.assertEqual(sample['t_seconds'], index / 10)
            for beacon in sample['beacons']:
                true_id = beacon['true_id']
                self.assertEqual(len(beacon['events']), len(beacon['observations']))
                if beacon['fault'] != 'none':
                    faults[beacon['fault']] += 1
                    self.assertGreater(index - last_fault.get(true_id, -1000), book.bits)
                    last_fault[true_id] = index
                if beacon['fault'] == 'missing':
                    self.assertEqual(beacon['events'], [])
                    self.assertIsNone(beacon['observed_bit'])
                    self.assertEqual(beacon['reason'], 'no_observation')
                for bit, event in zip(beacon['observations'], beacon['events']):
                    histories[true_id] += str(bit)
                    window = histories[true_id][-book.bits:]
                    expected = reference.get(window, 0) if len(window) == book.bits else 0
                    self.assertEqual(event['window'], window)
                    self.assertEqual(event['decoded_id'], expected)
                    counts['observation_events'] += 1
                    if len(histories[true_id]) < book.bits:
                        counts['warming_up_events'] += 1
                    elif expected == true_id:
                        counts['correct_events'] += 1
                    elif expected == 0:
                        counts['unknown_events'] += 1
                    else:
                        counts['incorrect_events'] += 1
        for key, count in counts.items():
            self.assertEqual(result['metrics'][key], count)
        self.assertEqual(faults, {'flip': 6, 'missing': 6, 'duplicate': 6})
        self.assertEqual(result['metrics']['fault_samples'], faults)
        self.assertEqual(result['metrics']['post_warmup_correct_fraction'], 1.0)
        self.assertEqual(counts['incorrect_events'], 0)
        self.assertEqual(result['frame_count'], 360)

    def test_simulation_reproducible_and_inputs_bounded(self):
        self.assertEqual(simulate(duration=2), simulate(duration=2))
        for kwargs in [dict(duration=0), dict(duration=float('nan')), dict(duration=10001),
                       dict(observation_hz=0), dict(fps=29), dict(fps=1)]:
            with self.assertRaises(ValueError):
                simulate(**kwargs)

    def test_cli_codebook_decode_and_simulation(self):
        root = Path(__file__).resolve().parents[2]
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / 'book.json'
            command = [sys.executable, '-m', 'updated.cli']
            subprocess.run(command + ['codebook', '--out', str(path)], cwd=root, check=True, capture_output=True)
            book = Codebook.from_dict(json.loads(path.read_text()))
            decoded = subprocess.run(command + ['decode', '--codebook', str(path), book.words[1] * 2],
                                     cwd=root, check=True, capture_output=True, text=True)
            value = json.loads(decoded.stdout)
            self.assertEqual(value['decisions'][-1]['decoded_id'], 2)
            sim = subprocess.run(command + ['simulate', '--duration', '1'], cwd=root,
                                 check=True, capture_output=True, text=True)
            self.assertEqual(json.loads(sim.stdout)['sample_count'], 10)
            bad = subprocess.run(command + ['codebook', '--bits', '2'], cwd=root, capture_output=True)
            self.assertNotEqual(bad.returncode, 0)


if __name__ == '__main__':
    unittest.main()
