# Winqi procedural demonstration

[Watch or download the 12-second MP4](winqi-demo.mp4) · [Poster](winqi-demo-poster.png) · [Generated Blender scene](winqi-demo.blend)

The new 1600 × 900, 30 fps video shows six coded wall beacons in a procedural room, an orbiting camera, and projected head/hand camera insets. Its composition takes visual inspiration from Dani Epstein's commissioned 2016 Winqi room animation. All geometry, materials, animation, and overlays in this release are newly generated from the included scripts. Dani's original video, reference images, and email are not redistributed. The original Blender ZIP was identified in his handoff but its link was inaccessible during recovery.

Each LED's emission follows the actual emitted bit in [the simulation trace](../updated/artifacts/simulation.json), held for three video frames. The displayed binary windows, fault tags, and decoded IDs come from the receiver events in that trace. The scene positions and camera trajectories are supplied geometry. The inset dots are pinhole camera projections, not image detections or fisheye calibration. Missing samples make no decoder call; duplicated samples make two. The display distinguishes warmup, missing observations, and unknown windows.

The deterministic trace contains separated single bit flips, missed samples, and duplicate observations. It has 720 receiver events, including 72 warmup events and 648 correct post-warmup identifications. This is a code-model demonstration with supplied tracks, not a camera, pose, SLAM, or general error-rate benchmark. See the [core's model and limitations](../updated/README.md).

## Rebuild

Run from the repository root. The recorded render uses Blender 5.1.2 (Cycles, 16 samples with denoising), Python with Pillow 10.4.0, and FFmpeg 8.1.1. The decoder itself uses only Python's standard library. Rendering needs Blender, Pillow, and FFmpeg separately; it is not part of the lightweight CI tests.

```sh
python3 -m updated.cli simulate --out updated/artifacts/simulation.json
blender --background --factory-startup --disable-autoexec \
  --python updated/render_demo.py -- \
  --simulation updated/artifacts/simulation.json \
  --output frames --blend media/winqi-demo.blend
python3 updated/compose_demo.py \
  --simulation updated/artifacts/simulation.json --frames frames \
  --output media/winqi-demo.mp4 --poster media/winqi-demo-poster.png
```

To install the optional composition dependency in an isolated environment:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install Pillow==10.4.0
```

Use `.venv/bin/python` for the composition command in that case. The renderer uses Metal if available in its factory-startup process and otherwise uses the CPU default. It does not save user preferences, load external models, or execute embedded Blender scripts. Frames are temporary output; the generated `.blend` retains its camera and beacon keyframes and a relative render path. The published scene uses the CPU setting for portability. [projections.json](projections.json) preserves the per-frame projected geometry used for labels and insets.

The [media validation record](../docs/DEMO_VALIDATION.json) records hashes and the actual checks. Run `python3 scripts/verify_demo.py` from the repository root to recheck asset/input hashes, poster dimensions, and projection structure without rendering. These new procedural media are under the [scoped MIT notice](LICENSE); this does not grant rights to historical third-party assets.
