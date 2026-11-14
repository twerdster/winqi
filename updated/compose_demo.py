"""Compose Blender room frames and actual decoder events into an annotated MP4.

Requires Pillow and an ffmpeg executable. All inset locations are projections
from scene geometry, not detected image features or estimated camera poses.
"""
import argparse
import json
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT = 1600, 900
BG = '#0b1323'
PANEL = '#111f33'
MUTED = '#9cacc1'
WHITE = '#edf3f9'
GREEN = '#50e4a5'
AMBER = '#ffc265'
BLUE = '#73b7ff'


def font(size, mono=False):
    candidates = (['/System/Library/Fonts/Menlo.ttc', 'DejaVuSansMono.ttf'] if mono else
                  ['/System/Library/Fonts/Supplemental/Arial.ttf', 'DejaVuSans.ttf'])
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            pass
    return ImageFont.load_default(size=size)


def camera_panel(draw, bounds, title, points, beacons):
    x, y, w, h = bounds
    draw.rounded_rectangle((x, y, x+w, y+h), radius=12, fill='#07111f', outline='#3a506a', width=2)
    draw.text((x+12, y+10), title, fill=MUTED, font=font(15, True))
    for point, beacon in zip(points, beacons):
        u, v, depth = point
        if depth <= 0 or not (0 <= u <= 1 and 0 <= v <= 1):
            continue
        px, py = x+12+u*(w-24), y+33+v*(h-45)
        color = GREEN if beacon['emitted_bit'] else '#344457'
        draw.ellipse((px-4, py-4, px+4, py+4), fill=color)
        if beacon['decoded_id']:
            draw.text((px+7, py-8), str(beacon['decoded_id']), fill=WHITE, font=font(13, True))


def compose(simulation, projection, room, index):
    sample = simulation['samples'][index//simulation['frames_per_sample']]
    beacons = sample['beacons']
    image = Image.new('RGB', (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(image)
    draw.text((32, 20), 'Winqi', fill=GREEN, font=font(43))
    draw.text((175, 30), 'Coded light, stable identities', fill=WHITE, font=font(30))
    draw.text((34, 75), 'New decoder + procedural room  /  cyclic binary codes  /  unsynchronized beacon phases', fill=MUTED, font=font(20))
    # Room render is a visual explanation; the algorithm receives binary track data.
    image.paste(room.convert('RGB'), (24, 116))
    draw = ImageDraw.Draw(image)
    for point, beacon in zip(projection['orbit'], beacons):
        u, v, depth = point
        if depth <= 0 or not (0 <= u <= 1 and 0 <= v <= 1):
            continue
        px, py = 24+u*1120, 116+v*700
        decoded = beacon['decoded_id']
        text = f'ID {decoded:02d}' if decoded else 'T'+beacon['track_id'].split('-')[-1]
        color = GREEN if decoded else MUTED
        draw.rounded_rectangle((px+12, py-15, px+99, py+13), radius=5, fill=BG, outline=color)
        draw.text((px+20, py-12), text, fill=color, font=font(17, True))
    camera_panel(draw, (44, 640, 256, 160), 'HEAD / projected', projection['head'], beacons)
    camera_panel(draw, (320, 640, 256, 160), 'HAND / projected', projection['hand'], beacons)
    draw.rounded_rectangle((1160, 116, 1576, 816), radius=14, fill=PANEL)
    draw.text((1182, 136), 'LIVE DECODER OUTPUT', fill=WHITE, font=font(21, True))
    draw.text((1182, 173), f'{index/simulation["fps"]:05.2f} s   |   {simulation["observation_hz"]} observations/s', fill=MUTED, font=font(17, True))
    for row, beacon in enumerate(beacons):
        y = 216+row*88
        decoded = beacon['decoded_id']
        fault = beacon['fault']
        reasons = {'no_observation': 'NO SAMPLE', 'warming_up': 'WARMUP', 'unknown': 'UNKNOWN'}
        status = f'ID {decoded:02d}' if decoded else reasons.get(beacon['reason'], 'UNKNOWN')
        color = GREEN if decoded else MUTED
        draw.text((1182, y), 'TRACK '+beacon['track_id'].split('-')[-1], fill=MUTED, font=font(17, True))
        draw.text((1363, y-3), status, fill=color, font=font(21, True))
        window = beacon['window']
        for j in range(simulation['codebook']['bits']):
            x = 1184+j*27
            bit = window[j] if j < len(window) else None
            fill = GREEN if bit == '1' else ('#2d435d' if bit == '0' else '#1a2a3f')
            draw.rounded_rectangle((x, y+30, x+21, y+48), radius=3, fill=fill)
        draw.text((1183, y+54), 'LAST OBSERVED WINDOW', fill=MUTED, font=font(11, True))
        if fault != 'none':
            draw.text((1398, y+54), fault.upper(), fill=AMBER, font=font(13, True))
    correct = sum(b['decoded_id'] == b['true_id'] for b in beacons)
    draw.text((1182, 761), f'{correct}/6 IDs in this sample', fill=WHITE, font=font(20))
    draw.text((1182, 790), 'Tracks supplied; IDs computed', fill=MUTED, font=font(16))
    # Segments describe the actual deterministic perturbation schedule.
    faults = {beacon['fault'] for beacon in beacons}
    stage = ('Acquiring one full code window' if any(b['reason'] == 'warming_up' for b in beacons) else
             'Single bit flips' if 'flip' in faults else
             'Missed observations' if 'missing' in faults else
             'Duplicated observations' if 'duplicate' in faults else
             'Decoding cyclic phases')
    draw.text((34, 836), stage, fill=AMBER if 'observations' in stage or 'flips' in stage else GREEN, font=font(21))
    draw.text((620, 839), 'Synthetic geometry + binary inputs; no camera, pose or SLAM benchmark', fill=MUTED, font=font(18))
    draw.rectangle((34, 877, 1566, 881), fill='#23364f')
    draw.rectangle((34, 877, 34+1532*(index+1)/simulation['frame_count'], 881), fill=GREEN)
    return image


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--simulation', type=Path, required=True)
    parser.add_argument('--frames', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--poster', type=Path)
    parser.add_argument('--preview-frame', type=int)
    parser.add_argument('--ffmpeg', default='ffmpeg')
    args = parser.parse_args()
    simulation = json.loads(args.simulation.read_text())
    projections = {r['frame_index']: r for r in json.loads((args.frames/'projections.json').read_text())}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.preview_frame is not None:
        index = args.preview_frame
        with Image.open(args.frames/f'{index:04d}.png') as room:
            compose(simulation, projections[index], room, index).save(args.output)
        return
    executable = shutil.which(args.ffmpeg)
    if not executable:
        raise SystemExit('ffmpeg not found; provide --ffmpeg /path/to/ffmpeg')
    assert set(projections) == set(range(simulation['frame_count'])), 'Incomplete Blender projection records'
    command = [executable, '-hide_banner', '-loglevel', 'error', '-y', '-f', 'rawvideo',
               '-pix_fmt', 'rgb24', '-s', f'{WIDTH}x{HEIGHT}', '-r', str(simulation['fps']),
               '-i', '-', '-an', '-c:v', 'libx264', '-crf', '19', '-preset', 'medium',
               '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(args.output)]
    process = subprocess.Popen(command, stdin=subprocess.PIPE)
    try:
        for index in range(simulation['frame_count']):
            with Image.open(args.frames/f'{index:04d}.png') as room:
                frame = compose(simulation, projections[index], room, index)
            if args.poster and index == 84:
                args.poster.parent.mkdir(parents=True, exist_ok=True)
                frame.save(args.poster)
            process.stdin.write(frame.tobytes())
    finally:
        process.stdin.close()
    if process.wait():
        raise SystemExit('ffmpeg encoding failed')


if __name__ == '__main__':
    main()
