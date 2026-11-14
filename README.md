# WinQI: coded-beacon research and an updated decoder

WinQI (also referred to as Winqi or Winky) research source recovered from Aaron Wetzler's preserved coded-beacon experiments. The project studies binary light codes that identify beacons across phase changes and a bounded set of observation errors.

This repository keeps the **historical MATLAB source and saved tables** separate from a **new Python implementation** and a new procedural demonstration. It also links the related, separately published [CoBe implementation](https://github.com/baklawe/CoBe) and [CoBe paper](https://arxiv.org/abs/1708.05625), by Roman Rabinovich, Ibrahim Jubran, Aaron Wetzler, and Ron Kimmel. The CoBe upstream repository remains the source for its camera-tracking, localization, and firmware implementation.

[![Winqi room simulation and computed beacon IDs](media/winqi-demo-poster.png)](media/winqi-demo.mp4)

[Watch the sample video](media/winqi-demo.mp4) · [Rebuild the scene](media/README.md) · [Run the tests](updated/README.md#validation)

The new sample follows the room/head-camera/hand-camera presentation of Dani Epstein's 2016 Winqi animation, using freshly generated geometry. Its labels show actual decoder decisions on synthetic binary observations. The original Blender handoff link was found but is currently inaccessible; the original animation was recovered as a private visual reference.

```sh
python3 updated/run_checks.py
python3 -m updated.cli simulate --out simulation.json
```

The core, CLI, and 15 tests need only Python 3.10+. Tests cover 5,070 physical single-fault stream cases and exact regeneration of five historical dictionaries with their older model. The checked sample has 648 correct post-warmup decisions. These are bounded-model checks with supplied tracks, rather than camera or localization measurements. See the [recorded results](updated/validation/test-results.json) and [full scope](updated/README.md).

| Directory | Contents |
| --- | --- |
| [source/original/matlab](source/original/matlab/) | Sixteen unchanged historical code-generation, decoding, simulation, and MEX source files |
| [source/original/tables](source/original/tables/) | Forty original MAT files and three binary-text code tables |
| [source/original/third_party/lcs](source/original/third_party/lcs/) | Two preserved David Cumin LCS variants with the recovered BSD notice |
| [updated](updated/) | Independently maintained Python core and CLI; see its README for commands, tests, and limitations |
| [media](media/) | New sample MP4, poster, generated Blender scene, and rebuild instructions |
| [docs](docs/) | Provenance, source/table inventory, dependencies, and archive validation |

The updated component handles binary observations with supplied track association. It does not implement camera capture, image/blob association, intensity/background rejection, 3D pose, SLAM, or the complete historical Android application. Any procedural sample video demonstrates that limited model and is not a validation on camera footage.

For the original archive, start with [genNoise.m](source/original/matlab/genNoise.m), [genCodesCyclic.m](source/original/matlab/genCodesCyclic.m), and [decodeEditDistance.m](source/original/matlab/decodeEditDistance.m). Read [the table/version differences](docs/ORIGINAL_TABLES.md) before using saved dictionaries: the archived generator script and saved tables represent different revisions.

```sh
python3 scripts/verify_original_sources.py
```

This verifies all 62 imported historical files against exact recorded hashes without running MATLAB or MEX. Seventeen MATLAB files were statically parsed; one original malformed block-comment marker is documented and preserved. Historical experiments have not been executed or reproduced.

[NOTICE](NOTICE.md) describes individual license scopes. No new blanket license is applied to the historical research source. The original archive, updated implementation, public CoBe repository, and generated media retain distinct attribution and validation records.

GitHub Actions verifies historical hashes and runs the decoder/fixture tests on Python 3.10 and 3.14. It does not render the video or run the historical applications.
