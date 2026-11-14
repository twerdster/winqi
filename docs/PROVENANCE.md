# Source provenance

## WinQI research archive

The historical folder contained WinQI paper figures, code-generation and decoding experiments, saved codebooks/dictionaries, research notes, and prototype media. The reviewed publication subset consists of 16 source files, 43 tables, and the separately licensed LCS helper's two variants and notice: **62 imported files**, all byte-exact copies. Logical original paths and SHA-256 hashes are recorded in [ORIGINAL_SOURCE_MANIFEST.json](ORIGINAL_SOURCE_MANIFEST.json). Private storage paths and cloud/mail identifiers are excluded.

The source was recovered on 2026-11-14. Public publication copies retain original formatting and code, with no source sanitization necessary for this selected subset. No credentials, private machine paths, or private endpoints were found in the selected code. MAT files were reviewed as numeric arrays or structs/cells of numeric arrays; the three DAT files contain only binary digits and line endings. Raw notes, patent/invention materials, unpublished paper archives, photographs, videos, and backup containers are outside this source release.

The historic Android capture experiments remain a separate, unbuilt effort. Their existence does not establish that a complete Android beacon decoder was recovered, and their private repository is not exposed here.

## Relationship to CoBe

The public [baklawe/CoBe repository](https://github.com/baklawe/CoBe) describes *Coded Beacons for Localization, Object Tracking, and SLAM Augmentation* and links [arXiv:1708.05625](https://arxiv.org/abs/1708.05625). The paper credits Roman Rabinovich, Ibrahim Jubran, Aaron Wetzler, and Ron Kimmel; its initial arXiv submission was in 2017 and its revised version in 2020. The observed upstream source commit is `576d6f9ba833ec16c46e0645141b9a0e92e4dc55` (2020-09-02).

All **19 cyclic MAT files** in this recovery are byte-identical to files in that upstream repository's `CodeCyclic.zip`. The source manifest records each matching member and pinned commit. The public repository includes Python tracking/localization components and ATtiny firmware under its own MIT notice. This evidence supports a direct code-table connection; it does not mean every WinQI experiment or newer implementation here is identical to CoBe.

This repository links CoBe as the separate public implementation. It does not copy its complete application or claim new validation of its hardware/camera system. New Python code in `updated/` is a separate bounded binary-observation implementation, with its own explicit behavior and tests.

## Source selection and third-party scope

`hmmDecode2.m` includes a copied MathWorks implementation and is omitted. Other omitted helpers have author attribution or third-party origins without a complete recovered redistribution grant. General grep demos, a curve/superellipse experiment, an im2col experiment, and bare link notes are outside the selected coded-beacon source scope. Each source exclusion appears in the manifest.

The recovered David Cumin LCS package has an explicit BSD notice. Its packaged and modified variants are preserved in separate directories with their original `LCS.m` filename. Other research sources retain their original comments without assigning new authorship or license terms. See [NOTICE](../NOTICE.md).

## New demonstration

Dani Epstein’s commissioned 2016 room animation was recovered as a private visual reference. Its original Blender ZIP handoff was identified but the link was inaccessible under current access. This release uses entirely new procedural room/mannequin geometry and materials, with no original Dani media, external models, invoice, or correspondence included. The new video follows actual emitted bits and decoder events from the deterministic binary trace. Inset and label positions are projections of supplied scene geometry, not detected image features or estimated poses. See [the media guide](../media/README.md) and [render validation](DEMO_VALIDATION.json) for tools, checks, and license scope.
