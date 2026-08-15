from pathlib import Path
p = Path('reports/executive_summary.pdf')
if not p.exists():
    print('MISSING')
    raise SystemExit(2)
size = p.stat().st_size
with p.open('rb') as f:
    header = f.read(4)
print('EXISTS', p.exists())
print('SIZE', size)
print('HEADER', header)
# simple heuristic
if header.startswith(b'%PDF'):
    print('PDF_OK')
else:
    print('PDF_HEADER_MISSING')
    raise SystemExit(3)
