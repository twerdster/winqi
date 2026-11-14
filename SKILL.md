# WinQI maintenance

Read SUMMARY.md, README.md, NOTICE.md, and docs/PROVENANCE.md before changes. The repository separates original coded-beacon research from updated software and procedural media. The related CoBe public application remains linked upstream with its original author/license attribution.

## Research presentation

Keep the README focused on how coded beacons work, the demonstration, published research results, runnable examples and useful code entry points. Link archive/recovery details from supporting docs. Cite original Winqi with arXiv:1708.05625v1 (2017, Wetzler and Kimmel) and later CoBe with v3 (2020, Rabinovich, Jubran, Wetzler and Kimmel); they are versions of the same arXiv record. Attribute experimental results to the specific paper and setup. Keep the new binary-stream checks and synthetic demonstration separate from hardware/localization results. CoBe's reported submillimeter rail ground-truth precision is not system tracking accuracy.

## Historical archive

`source/original/` is the reviewed exact-byte archive. Do not edit or reformat it. Any justified source sanitization requires explicit original/published hashes and named transformations in docs/ORIGINAL_SOURCE_MANIFEST.json. Put new behavior in updated/, with separate tests, notices, and documentation. Preserve the two LCS variants in separate directories and retain their BSD license. The CoBe MIT notice applies to the already-public identical cyclic tables, not to every historical source.

Never import private paths, account identifiers, raw mail/backup containers, invention disclosures, unpublished paper archives, or source without an applicable publication basis. Omitted MathWorks HMM and unattributed third-party helpers remain omitted unless a scoped grant is established.

Run `python3 scripts/verify_original_sources.py` to verify archive hashes, allowed file inventory, retained notices, and privacy markers without executing historical code. Optional MATLAB static parsing uses MISS_HIT 0.9.44; preserve and document the known genBalls malformed block-comment marker. Original research scripts can allocate substantial arrays, write outputs, and invoke shell commands; do not run them as a routine smoke test.

## Tables and claims

Saved MAT dictionary values are raw code + 1, not ordered beacon IDs. The archived generator script uses a different dictionary revision. Always name exact fixtures, translate dictionary semantics explicitly, and document operational constant-code policy. Preserve original numeric tables and keep derived fixtures/results in updated/ with source hashes.

New binary-observation tests or procedural videos do not validate camera acquisition, blob/track association, intensity/background rejection, pose, SLAM, firmware, or the private Android experiments. Updated documentation and media captions must state their actual input/model scope.

Preserve .gitattributes and its exact original-file whitespace exceptions; hashes enforce archived bytes. Keep new code, documentation and tooling subject to normal whitespace checks.

Run `python3 updated/run_checks.py` after core/test changes. It verifies the 15-test suite and exact simulation/codebook artifacts and refreshes interpreter/source-hash evidence. Saved-table reference tests use the older variable-length model and explicit constant policies; do not merge that model silently into the active fixed-width core. Nonconstant candidate selection does not imply static-background rejection.

For media changes follow media/README.md. Use factory-startup Blender with autoexec disabled, generated geometry, and the actual simulation trace. Verify all LED keyframes and projected labels against their intended inputs. Warmup, missing and unknown statuses must remain distinct. Preserve Dani Epstein’s visual-reference credit without importing his private correspondence or unlicensed assets. Record rendering/encoding versions, frame dimensions/count, hashes and inspection scope in docs/DEMO_VALIDATION.json. Run `python3 scripts/verify_demo.py` to check its published assets/input bindings; this lightweight check also runs in CI. Full decoding and browser playback remain separately recorded checks; a browser check should verify actual progress to the video end, rather than only metadata loading. Keep large temporary frames on verified task storage and record actual private scratch paths outside the public repository.

Before each commit, review SUMMARY.md and this file and update them for current scope, commands, outputs, operating assumptions, status, and handoff. Publish normally to twerdster/winqi main with a verified permitted account, then verify the public commit/tree/media and CI. The website link belongs beside the CoBe publication; keep its original upstream application link and this recovered/new implementation distinct.
