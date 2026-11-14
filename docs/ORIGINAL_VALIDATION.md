# Original archive validation — 2026-11-14

- **62 files** match the recorded original and publication SHA-256 values and sizes, with no source transformations.
- **40 MAT files** were inspected with SciPy `loadmat`: variables contain numeric arrays or numeric structs/cells only. Their schema/count summaries are in ORIGINAL_TABLE_INVENTORY.json. This is data inspection, not execution of MATLAB source or validation of the codebook's theoretical properties.
- **3 DAT files** contain only ASCII binary digits and line endings.
- **19 cyclic MAT files** match the same members byte-for-byte in the public CoBe repository's pinned `CodeCyclic.zip`.
- **17 MATLAB files** were parsed/linted with MISS_HIT 0.9.44. The tool exited successfully with one preserved low-priority check: `genBalls.m:15` has text after `%{`, so MATLAB does not treat that marker as a block-comment opener. No source was silently repaired.
- Source selection retained the LCS BSD notice and CoBe MIT notice. The selected publication code contains no detected private paths, key markers, or private endpoints.

Repeat the exact offline archive check with:

```sh
python3 scripts/verify_original_sources.py
```

This uses the Python standard library and never executes project code. To repeat the optional static MATLAB parse in a task-scoped environment:

```sh
python3 -m venv /tmp/winqi-source-check
/tmp/winqi-source-check/bin/pip install miss-hit==0.9.44
/tmp/winqi-source-check/bin/mh_lint --single --ignore-config --brief source/original
```

Original MATLAB/MEX experiments, video/camera tracking, firmware, pose recovery, and SLAM have not been executed or validated. Results for new code and generated media are recorded separately under `updated/` and their own provenance files.
