#!/usr/bin/env python3
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
required = [
    'SKILL.md', 'README.md', 'LICENSE', 'agents/openai.yaml',
    'references/art-direction.md', 'references/ticket-layout.md',
    'references/airplane.md', 'references/railway.md', 'scripts/save_output.py',
]
missing = [name for name in required if not (ROOT / name).is_file()]
if missing:
    raise SystemExit('Missing required files: ' + ', '.join(missing))

skill = (ROOT / 'SKILL.md').read_text()
if not skill.startswith('---\n') or '\nname: travel-ticket\n' not in skill or '\ndescription:' not in skill:
    raise SystemExit('Invalid SKILL.md frontmatter')

for md in ROOT.rglob('*.md'):
    text = md.read_text()
    for ref in re.findall(r'\]\(([^)]+)\)', text):
        if '://' in ref or ref.startswith('#'):
            continue
        target = (md.parent / ref.split('#', 1)[0]).resolve()
        if not target.exists():
            raise SystemExit(f'Broken reference in {md.relative_to(ROOT)}: {ref}')

for md in ROOT.rglob('*.md'):
    text = md.read_text()
    for stale in ('B3', '第三阶段'):
        if stale in text:
            raise SystemExit(f'Stale term {stale!r} in {md.relative_to(ROOT)}')

with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp)
    src = tmp / 'source.png'
    src.write_bytes(b'\x89PNG\r\n\x1a\ntravel-ticket-test')
    cmd = [sys.executable, str(ROOT / 'scripts/save_output.py'), str(src), '--workspace', str(tmp), '--type', 'airplane']
    first = Path(subprocess.check_output(cmd, text=True).strip())
    second = Path(subprocess.check_output(cmd, text=True).strip())
    if first == second or first.read_bytes() != src.read_bytes() or second.read_bytes() != src.read_bytes():
        raise SystemExit('save_output.py overwrite protection failed')
print('travel-ticket validation passed')
