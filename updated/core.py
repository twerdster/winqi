"""Cyclic coded-beacon identification, derived from genNoise/genCodesCyclic.

This is a new, dependency-free implementation of a bounded binary observation
model. It does not implement cameras, blob association, pose estimation or SLAM.
"""
from collections import deque
from dataclasses import dataclass, field
import math
from types import MappingProxyType


def _binary(word: str, length: int | None = None) -> str:
    if not isinstance(word, str) or not word or set(word) - {'0', '1'}:
        raise ValueError('Expected a nonempty binary string.')
    if length is not None and len(word) != length:
        raise ValueError(f'Expected exactly {length} bits.')
    return word


def rotations(word: str) -> tuple[str, ...]:
    """Unique left rotations in phase order; periodic words have fewer rotations."""
    _binary(word)
    return tuple(dict.fromkeys(word[i:] + word[:i] for i in range(len(word))))


def noise_variants(word: str) -> frozenset[str]:
    """Fixed-width variants from the active genNoise.m implementation.

    Includes clean word, one flip, one deletion with periodic boundary fill on
    either side, or insertion of 0/1 after a bit followed by dropping first bit.
    This is not arbitrary edit-distance correction or simultaneous errors.
    """
    _binary(word)
    n = len(word)
    variants = {word}
    for i in range(n):
        variants.add(word[:i] + ('1' if word[i] == '0' else '0') + word[i + 1:])
        deleted = word[:i] + word[i + 1:]
        variants.add(deleted + word[0])
        variants.add(word[-1] + deleted)
        for bit in '01':
            variants.add((word[:i + 1] + bit + word[i + 1:])[1:])
    return frozenset(variants)


def cyclic_noise_family(word: str) -> frozenset[str]:
    return frozenset(variant for phase in rotations(word) for variant in noise_variants(phase))


@dataclass(frozen=True)
class Codebook:
    bits: int
    words: tuple[str, ...]
    packing: str = 'nonconstant'
    lookup: dict[str, int] = field(init=False, repr=False, compare=False)

    def __post_init__(self):
        if isinstance(self.bits, bool) or not isinstance(self.bits, int) or not 3 <= self.bits <= 15:
            raise ValueError('bits must be an integer from 3 through 15.')
        if self.packing not in {'nonconstant', 'include-constants', 'source-script'}:
            raise ValueError('Unknown packing policy.')
        if not isinstance(self.words, tuple) or not self.words:
            raise ValueError('A nonempty tuple of codewords is required.')
        lookup = {}
        for beacon_id, word in enumerate(self.words, 1):
            _binary(word, self.bits)
            if self.packing == 'nonconstant' and len(set(word)) == 1:
                raise ValueError('Constant codes cannot identify operational flashing beacons.')
            if word != min(rotations(word)):
                raise ValueError('Codewords must use their smallest cyclic representative.')
            family = cyclic_noise_family(word)
            if any(variant in lookup for variant in family):
                raise ValueError('Overlapping cyclic noise families are ambiguous.')
            lookup.update((variant, beacon_id) for variant in family)
        object.__setattr__(self, 'lookup', MappingProxyType(lookup))

    def decode_window(self, window: str) -> int:
        """Return 1-based codebook ID, or 0 for an unrecognized n-bit window."""
        return self.lookup.get(_binary(window, self.bits), 0)

    def to_dict(self) -> dict:
        return {'schema': 'winqi-codebook-v1', 'bits': self.bits, 'packing': self.packing,
                'unknown_id': 0, 'id_semantics': 'one-based codebook position',
                'noise_model': 'one fixed-window flip, missed observation, or inserted binary observation',
                'codes': [{'beacon_id': i, 'word': w, 'raw_code_value': int(w, 2)}
                          for i, w in enumerate(self.words, 1)]}

    @classmethod
    def from_dict(cls, value: dict):
        if value.get('schema') != 'winqi-codebook-v1' or value.get('unknown_id') != 0:
            raise ValueError('Unsupported codebook schema/unknown ID.')
        codes = value['codes']
        if [c['beacon_id'] for c in codes] != list(range(1, len(codes) + 1)):
            raise ValueError('Beacon IDs must be consecutive and one-based.')
        if any(c.get('raw_code_value') != int(_binary(c['word']), 2) for c in codes):
            raise ValueError('Raw code values must match the binary words.')
        return cls(value['bits'], tuple(c['word'] for c in codes), value['packing'])


def generate_codebook(bits: int = 13, count: int | None = 6,
                      packing: str = 'nonconstant') -> Codebook:
    """Ascending greedy packing of disjoint cyclic genNoise families.

    Default excludes both constant candidates BEFORE packing. The optional
    include-constants policy scans all candidates, including both constants,
    as a comparison policy. source-script includes zero but excludes all-ones,
    matching the active genCodesCyclic.m loop. Saved MAT tables instead use an
    older variable-length model; see the independent historical fixture tests.
    """
    if isinstance(bits, bool) or not isinstance(bits, int) or not 3 <= bits <= 15:
        raise ValueError('bits must be an integer from 3 through 15.')
    if count is not None and (isinstance(count, bool) or not isinstance(count, int) or count < 1):
        raise ValueError('count must be a positive integer or None.')
    if packing not in {'nonconstant', 'include-constants', 'source-script'}:
        raise ValueError('Unknown packing policy.')
    occupied = set()
    words = []
    start = 1 if packing == 'nonconstant' else 0
    stop = (1 << bits) if packing == 'include-constants' else (1 << bits) - 1
    for raw in range(start, stop):
        word = f'{raw:0{bits}b}'
        phases = rotations(word)
        if word != min(phases) or word in occupied:
            continue
        family = frozenset(v for phase in phases for v in noise_variants(phase))
        if occupied.isdisjoint(family):
            words.append(word)
            occupied.update(family)
            if count is not None and len(words) == count:
                break
    if count is not None and len(words) < count:
        raise ValueError(f'{bits} bits support only {len(words)} codes with this policy; requested {count}.')
    if not words:
        raise ValueError('No codewords available.')
    return Codebook(bits, tuple(words), packing)


class StreamDecoder:
    """Last-n-observation lookup. Track association is supplied by the caller."""
    def __init__(self, codebook: Codebook):
        self.codebook = codebook
        self._window = deque(maxlen=codebook.bits)
        self.observations_seen = 0

    @property
    def window(self) -> str:
        return ''.join(self._window)

    def push(self, bit: int | str) -> dict:
        if type(bit) is int and bit in (0, 1):
            value = str(bit)
        elif isinstance(bit, str) and bit in ('0', '1'):
            value = bit
        else:
            raise ValueError('An observation must be binary 0/1; omit missing observations.')
        self._window.append(value)
        self.observations_seen += 1
        warmup = len(self._window) < self.codebook.bits
        decoded = 0 if warmup else self.codebook.decode_window(self.window)
        return {'observation_index': self.observations_seen - 1, 'window': self.window,
                'decoded_id': decoded,
                'reason': 'warming_up' if warmup else 'identified' if decoded else 'unknown'}


def simulate(codebook: Codebook | None = None, duration: float = 12.0,
             observation_hz: int = 10, fps: int = 30) -> dict:
    """Procedural 2D trajectories and binary observations, with actual decoding.

    All detections/track associations are supplied synthetically. Each record's
    events is the actual sequence of calls to StreamDecoder.push; ground-truth
    IDs are only used afterwards to compute metrics. A missing sample makes no
    push call. A duplicate makes two calls. Faults are separated > word length.
    """
    book = codebook or generate_codebook()
    if (not math.isfinite(duration) or duration <= 0 or isinstance(observation_hz, bool)
            or type(observation_hz) is not int or observation_hz < 1 or type(fps) is not int
            or fps < observation_hz or fps % observation_hz):
        raise ValueError('Use finite positive duration, positive integer rates and integer frames per observation.')
    if duration * observation_hz > 10000:
        raise ValueError('Simulation is bounded to 10,000 observation times.')
    sample_count = int(duration * observation_hz)
    hold = fps // observation_hz
    decoders = [StreamDecoder(book) for _ in book.words]
    phases = [(i * 2 + i // 2) % book.bits for i in range(len(book.words))]
    samples = []
    metrics = {'observation_events': 0, 'warming_up_events': 0, 'correct_events': 0,
               'incorrect_events': 0, 'unknown_events': 0,
               'fault_samples': {'flip': 0, 'missing': 0, 'duplicate': 0}}
    schedules = []
    # Limit to one event in any n-observation neighborhood, including duplicated samples.
    for i in range(len(book.words)):
        offset = i % max(1, book.bits // 2)
        gap = book.bits + 12
        schedules.append({book.bits + 12 + offset: 'flip',
                          book.bits + 12 + gap + offset: 'missing',
                          book.bits + 12 + 2 * gap + offset: 'duplicate'})
    for index in range(sample_count):
        time = index / observation_hz
        beacons = []
        for i, word in enumerate(book.words):
            truth_id = i + 1
            emitted = int(word[(index + phases[i]) % book.bits])
            fault = schedules[i].get(index, 'none')
            observations = [] if fault == 'missing' else [1 - emitted] if fault == 'flip' else [emitted] * (2 if fault == 'duplicate' else 1)
            events = [decoders[i].push(value) for value in observations]
            for event in events:
                metrics['observation_events'] += 1
                if event['reason'] == 'warming_up':
                    metrics['warming_up_events'] += 1
                elif event['decoded_id'] == truth_id:
                    metrics['correct_events'] += 1
                elif event['decoded_id'] == 0:
                    metrics['unknown_events'] += 1
                else:
                    metrics['incorrect_events'] += 1
            if fault != 'none':
                metrics['fault_samples'][fault] += 1
            last = events[-1] if events else {'window': decoders[i].window, 'decoded_id': 0, 'reason': 'no_observation'}
            col, row = i % 3, i // 3
            xy = [round(0.18 + col * 0.32 + 0.045 * math.sin(0.7 * time + i), 6),
                  round(0.3 + row * 0.35 + 0.04 * math.cos(0.5 * time + i), 6)]
            beacons.append({'track_id': f'track-{i + 1:02d}', 'true_id': truth_id,
                            'phase': phases[i], 'position_xy': xy, 'emitted_bit': emitted,
                            'observed_bit': None if not observations else observations[-1],
                            'observations': observations, 'events': events, 'fault': fault,
                            'window': last['window'], 'decoded_id': last['decoded_id'], 'reason': last['reason']})
        samples.append({'sample_index': index, 'frame_index': index * hold,
                        't_seconds': time, 'beacons': beacons})
    attempted = metrics['observation_events'] - metrics['warming_up_events']
    metrics['post_warmup_events'] = attempted
    metrics['post_warmup_correct_fraction'] = metrics['correct_events'] / attempted if attempted else None
    return {'schema': 'winqi-simulation-v1', 'scope': 'procedural binary observations with supplied track association; no camera/pose/SLAM',
            'codebook': book.to_dict(), 'fps': fps, 'observation_hz': observation_hz,
            'frames_per_sample': hold, 'duration_seconds': duration, 'sample_count': sample_count,
            'frame_count': sample_count * hold, 'fault_model': 'separated single flip, missed sample, duplicate observation per track',
            'metrics': metrics, 'samples': samples}
