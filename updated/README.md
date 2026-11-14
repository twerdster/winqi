# Updated binary-beacon core

This is a new Python implementation of cyclic binary-code generation and beacon identification. It follows the active fixed-width noise construction in the recovered [genNoise.m](../source/original/matlab/genNoise.m), with explicit packing policies and an independently tested observation-stream decoder. The historical MATLAB source remains unchanged in [source/original](../source/original/).

Python **3.10 or later**, using its standard library, is sufficient for the core, CLI, and tests. No pip installation, NumPy, SciPy, MATLAB, Android SDK, or camera is required. Run the following commands from the repository root:

```sh
python3 -m updated.cli codebook --bits 13 --count 6 --out updated/artifacts/codebook.json
python3 -m updated.cli simulate --duration 12 --observation-hz 10 --fps 30 --out updated/artifacts/simulation.json
python3 -m updated.cli decode --codebook updated/artifacts/codebook.json 00000000011110000000001111
python3 updated/run_checks.py
```

The decode example contains two repetitions of beacon 2's code. Decisions before 13 observations report `warming_up`; subsequent decisions identify beacon 2. A missing observation is omitted from the input stream, and an extra observation is supplied as an extra bit. The CLI returns JSON, writes to standard output when `--out` is absent, and rejects invalid codebook or stream input.

## Model and limits

Each beacon repeatedly emits its codeword. The receiver may begin at any cyclic phase and looks up the last `n` received binary observations. A codeword's family contains every cyclic phase and the fixed-width windows caused by a single bit flip, a missed observation with periodic boundary fill, or an inserted binary observation with boundary truncation. Greedy packing accepts a codeword only when its entire family is disjoint from all previously accepted families. IDs are one-based positions in the resulting codebook; `0` means an unrecognized window or an incomplete stream.

The default `nonconstant` policy excludes both constant candidate words **before** ascending greedy packing. The default six 13-bit words are:

| ID | Repeated word |
| --- | --- |
| 1 | `0000000000001` |
| 2 | `0000000001111` |
| 3 | `0000001010101` |
| 4 | `0000001111111` |
| 5 | `0000100110011` |
| 6 | `0000111000111` |

`--packing source-script` matches the active generator's candidate range, which includes zero and stops before all-ones. `--packing include-constants` includes both constants for comparison. Changing which candidates are excluded before packing can change later accepted codes; removing constants after packing is a different procedure. Code widths are bounded to 3–15 bits, and simulation is bounded to 10,000 sampling times.

Disjoint families give unique identification within this model. Multiple errors in one observation window can yield an unknown or an incorrect ID. Excluding constant codewords does **not** reject static lights or background: an all-zero 13-bit observation window belongs to beacon 1's one-flip family. A camera application needs separate detection, intensity/background rejection, and track association.

The caller supplies an existing track's binary observations. This component does not capture images, associate blobs, estimate phase, recover 3D pose, implement SLAM, or reproduce the historical camera/Android application. Phase offsets and beacon positions in the demonstration are supplied ground truth, rather than estimates.

## Saved historical tables use a different revision

The current MATLAB generator and the preserved `CodeCyclic*.mat` files have different semantics. The saved tables use an older, commented noise model: clean/one-flip words of length `n`, one-deletion words of length `n-1`, and duplicated-bit words of length `n+1`. Their numeric keys collapse leading zeros and word length. Their dictionaries have `2^(n+1)` entries and store **raw code value + 1**, rather than the current script's one-based codebook index. See [the original table notes](../docs/ORIGINAL_TABLES.md).

The test fixture contains full code and dictionary arrays from the preserved 3-, 6-, 8-, 10-, and 11-bit cyclic MAT files. An independent older-model implementation in the tests regenerates all five exactly, with each table's explicit constant policy. The 10-bit table excludes constant candidates; the other four include them. Each fixture is also bound to its original MAT file's SHA-256. SciPy was used once to extract these numeric fixtures and is unnecessary to run the tests.

This is historical-table validation for those five tables, not blanket equivalence between the new fixed-width implementation and every archived table. For example, the saved 8-bit codes are `[0, 7, 51, 85, 127]`; fixed-width `include-constants` generates `[0, 7, 63, 85]`, and the default policy generates `[1, 15, 85, 127]`.

## Simulation interface

[artifacts/simulation.json](artifacts/simulation.json) is a deterministic 12-second trace of six phase-offset beacons, sampled at 10 Hz and displayed at 30 fps (three frames per emitted bit). Each track receives one flip, one missing sample, and one duplicate observation, separated by more than a codeword length. The decoder consumes actual altered observations. Ground-truth IDs are used afterwards to score its decisions.

The `winqi-simulation-v1` JSON contains the codebook, rates, frame/sample counts, fault model, metrics, and `samples` array. Every sample has `sample_index`, `frame_index`, `t_seconds`, and a `beacons` array. Each beacon records:

- `track_id`, `true_id`, supplied `phase`, and procedural `position_xy`;
- `emitted_bit`, nullable `observed_bit`, and `observations` containing zero, one, or two actual receiver events;
- `events`, with each decoder input's observation index, window, decoded ID, and reason;
- `fault`, and the final event's `window`, `decoded_id`, and `reason`.

A missing sample has no decoder event and reports `no_observation`, with ID 0 in that display sample. It is not counted as an erroneous decoder decision. A duplicate produces two events. Renderers may replace the supplied 2D positions with projected scene geometry while retaining these observation and decoding fields.

The checked default trace has **720 observation events: 72 warmup and 648 correct post-warmup decisions**, with zero incorrect and zero unknown post-warmup decisions. It contains six faults of each kind. This is a deterministic, deliberately separated single-fault fixture, not a measured accuracy on camera data or arbitrary error sequences.

## Validation

`python3 updated/run_checks.py` runs 15 standard-library tests, checks saved artifacts against fresh outputs, and writes [validation/test-results.json](validation/test-results.json). The result records the interpreter version, test statuses, exact tested source hashes, artifact hashes, metrics, and scope. Tests include:

- independent physical-stream construction of every noise family for every 3–6-bit word;
- disjoint families and unique cyclic identification for default-policy codebooks of widths 3–11;
- 5,070 actual single-fault stream cases: six IDs, all 13 phases, all 13 fault positions, and flip/missing/duplicate/insert-0/insert-1;
- explicit warmup, unknown windows, invalid/ambiguous codebook rejection, immutable lookup, and JSON/CLI behavior;
- independent replay of simulation windows and metrics;
- the five full historical dictionaries, their original-file hashes, ID conversion, and revision/policy differences.

No hardware or real-camera accuracy is measured by these checks. The test runner returns a nonzero exit status if a test fails or either saved JSON artifact differs from fresh output.

## Rendered sample

The [new room demonstration](../media/README.md) includes a 12-second MP4, poster, and generated Blender scene. The room LEDs follow this trace; IDs and binary windows come from actual decoder events. Camera-inset positions are projected scene geometry. Rebuild commands and the optional Blender/Pillow/FFmpeg requirements are separate from the dependency-free core and tests.

## License

The newly written implementation, tests, documentation, and procedural demonstration code in this directory are covered by [its MIT notice](LICENSE). Historical numeric fixtures retain the separate [CoBe MIT notice](../LICENSES/CoBe-MIT.txt). This scope does not assign a new license to historical research files or third-party media; see [NOTICE](../NOTICE.md).
