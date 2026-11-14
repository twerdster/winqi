"""Check published demo assets and their input binding without rendering."""
import hashlib
import json
from pathlib import Path
import struct

root = Path(__file__).resolve().parents[1]
record = json.loads((root/'docs/DEMO_VALIDATION.json').read_text())
for name, expected in record['files'].items():
    path = Path(name)
    assert not path.is_absolute() and '..' not in path.parts
    data = (root/path).read_bytes()
    assert len(data) == expected['bytes'], name
    assert hashlib.sha256(data).hexdigest() == expected['sha256'], name

simulation = json.loads((root/'updated/artifacts/simulation.json').read_text())
projections = json.loads((root/'media/projections.json').read_text())
assert simulation['frame_count'] == record['video']['frames'] == 360
assert [r['frame_index'] for r in projections] == list(range(360))
for row in projections:
    for name in ['orbit', 'head', 'hand']:
        assert len(row[name]) == 6 and all(len(p) == 3 for p in row[name])
poster = (root/'media/winqi-demo-poster.png').read_bytes()
assert poster[:8] == b'\x89PNG\r\n\x1a\n'
assert struct.unpack('>II', poster[16:24]) == (1600, 900)
assert (root/'media/winqi-demo.mp4').read_bytes()[4:8] == b'ftyp'
print(json.dumps({'status': 'passed', 'files_verified': len(record['files']),
                  'projection_frames': len(projections),
                  'scope': 'Published hashes, input binding, PNG dimensions and projection structure; no new render or camera validation.'}))
