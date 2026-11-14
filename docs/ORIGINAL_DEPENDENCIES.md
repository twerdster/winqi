# Historical experiment dependencies and limitations

The archived MATLAB code has not been executed. Several files are exploratory scripts rather than packaged entry points: they create figures, allocate large arrays, write MAT/DAT files, invoke shell commands, or contain unfinished/debugging statements.

- `genCodes.m`, `genCodesCyclic.m`, and `genCodesNonCyclic.m` explore code generation and dictionary packing. Their variable conventions and save behavior differ by revision. Consult the table-schema document before interpreting results.
- `flasher.m`, `genGraphs.m`, `genBalls.m`, and `simulateCodes.m` contain exploratory plotting, sampling, or HMM experiments. `flasher.m` includes a debug statement; `genBalls.m` has a malformed block-comment marker and references unfinished variables; `simulateCodes.m` calls an excluded HMM helper and ends with free-form planning text. A parser accepting these files is not a claim that the experiments complete successfully.
- `findCode.m` invokes Unix shell `grep`, `cut`, and `uniq` using supplied filenames and patterns and writes `out.txt`. Treat it as a historical controlled-input experiment, not an exposed service or safe arbitrary-input interface.
- `popcnt.cpp` is MATLAB MEX source with x86/SSE and Microsoft-style population-count intrinsics; `demo_popcnt.m` tries to compile it and allocates a large descriptor array. It was not compiled or run on the current machine. This is not the new portable decoder.
- Historical Hamming coding, smoothing, statistics, HMM, or plotting functions may require MATLAB toolboxes. The omitted MathWorks routine is not redistributed.
- The two licensed LCS variants are alternatives and should not both be placed on the MATLAB path indiscriminately. The modified version returns additional matrices/indices.

No original camera pipeline, binary SDK, Android application, firmware flashing, pose solver, or SLAM deployment is validated by this archive. The related CoBe application remains linked upstream. Modern commands, tests, scope, and dependency information belong to `updated/README.md`.
