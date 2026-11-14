#!/usr/bin/env python3
"""Check exact historical source bytes without running MATLAB, MEX, or firmware."""
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
manifest = json.loads((ROOT / 'docs/ORIGINAL_SOURCE_MANIFEST.json').read_text())
seen = set()
errors = []
exact = 0
for item in manifest['files']:
    rel = Path(item['path'])
    if rel.is_absolute() or '..' in rel.parts or rel.parts[:2] != ('source', 'original'):
        errors.append(f'Unsafe original-source path: {rel}')
        continue
    if str(rel) in seen:
        errors.append(f'Duplicate original-source path: {rel}')
    seen.add(str(rel))
    p = ROOT / rel
    if not p.is_file() or p.is_symlink():
        errors.append(f'Missing source or unexpected symlink: {rel}')
        continue
    data = p.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    if digest != item['published_sha256'] or len(data) != item['bytes']:
        errors.append(f'Published source hash/size mismatch: {rel}')
    if digest != item['original_sha256'] or item['transformations']:
        errors.append(f'Original archive bytes changed: {rel}')
    if digest == item['original_sha256'] == item['published_sha256'] and len(data) == item['bytes'] and not item['transformations']:
        exact += 1
    if p.suffix.lower() not in {'.m', '.cpp', '.mat', '.dat', '.txt'}:
        errors.append(f'Unexpected original file type: {rel}')
    if p.suffix.lower() != '.mat':
        if re.search(rb'/Users/|/Volumes/|BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY', data):
            errors.append(f'Private path or key marker: {rel}')
    if p.suffix.lower() == '.dat' and set(data) - {10, 13, 48, 49}:
        errors.append(f'Non-binary-text content in table: {rel}')

actual = {str(p.relative_to(ROOT)) for p in (ROOT / 'source/original').rglob('*') if p.is_file()}
for rel in sorted(actual - seen):
    errors.append(f'Unreviewed file inside original-source archive: {rel}')
for rel in sorted(seen - actual):
    errors.append(f'Absent file from original-source archive: {rel}')

for notice in manifest.get('supporting_notices', []):
    p = ROOT / notice['path']
    if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest() != notice['sha256'] or p.stat().st_size != notice['bytes']:
        errors.append(f'Missing or changed supporting notice: {notice["path"]}')

license_file = ROOT / 'source/original/third_party/lcs/LICENSE.txt'
if not license_file.exists() or b'Copyright (c) 2009, David Cumin' not in license_file.read_bytes():
    errors.append('Missing original LCS attribution/license')
co_license = ROOT / 'LICENSES/CoBe-MIT.txt'
if not co_license.exists() or b'Copyright (c) 2020 baklawe' not in co_license.read_bytes():
    errors.append('Missing CoBe notice for byte-identical public cyclic tables')

print(json.dumps({'original_files': len(seen), 'byte_exact_files': exact,
                  'errors': errors, 'scope': 'Original file integrity, allowed publication paths/types, text privacy markers, table text alphabet, and retained third-party notices; no research code executed.'}, indent=2))
sys.exit(1 if errors else 0)
