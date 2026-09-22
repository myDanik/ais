from pathlib import Path
import json
import xml.etree.ElementTree as ET
import pymupdf as fitz
from PIL import Image, ImageDraw

ROOT = Path(__file__).parent
OUT = ROOT / 'review_png'
OUT.mkdir(exist_ok=True)
summary = []
for path in sorted(ROOT.glob('slide-??.pdf')):
    with fitz.open(path) as doc:
        page = doc[0]
        png = OUT / (path.stem + '.png')
        if not png.exists() or png.stat().st_mtime < path.stat().st_mtime:
            page.get_pixmap(matrix=fitz.Matrix(0.75, 0.75), alpha=False).save(png)
        spans = [s for b in page.get_text('dict')['blocks'] for l in b.get('lines', []) for s in l['spans']]
        outside = [s['text'] for s in spans if s['text'].strip() and not page.rect.contains(fitz.Rect(s['bbox']))]
        svg = ET.parse(path.with_suffix('.svg'))
        texts = [''.join(el.itertext()) for el in svg.getroot().iter() if el.tag.rsplit('}', 1)[-1] == 'text']
        summary.append({'slide': path.stem, 'size': [page.rect.width, page.rect.height], 'outside': outside, 'fonts': sorted({f[3] for f in page.get_fonts()}), 'text': texts})
images = sorted(OUT.glob('slide-??.png'))
for start in range(0, len(images), 4):
    sheet = Image.new('RGB', (1920, 1160), '#e6e8e7')
    draw = ImageDraw.Draw(sheet)
    for j, path in enumerate(images[start:start+4]):
        im = Image.open(path)
        im.thumbnail((960,540))
        x, y = j % 2 * 960, j // 2 * 580
        sheet.paste(im, (x, y))
        draw.text((x + 20, y + 550), path.stem, fill='black')
    sheet.save(OUT / f'contact-{start // 4 + 1:02}.png')
(ROOT / 'review_evidence.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'count': len(summary), 'outside': {s['slide']: s['outside'] for s in summary if s['outside']}, 'fonts': sorted({f for s in summary for f in s['fonts']})}))
