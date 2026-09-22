import json
from collections import Counter
from pathlib import Path
import pymupdf as fitz
ROOT=Path(__file__).resolve().parents[1]
source=Path(r'C:\Users\ruslanzalikov\Downloads\Lecture7-UvA-FoMo2026.pdf')
out=ROOT/'qa/style-reference';out.mkdir(parents=True,exist_ok=True)
report=[]
with fitz.open(source) as doc:
    for i in [0,5,7,10,13,16,17,19,22,24]:
        page=doc[i]
        page.get_pixmap(matrix=fitz.Matrix(1.45,1.45),alpha=False).save(out/f'page_{i+1:02}.png')
        spans=[s for b in page.get_text('dict')['blocks'] for l in b.get('lines',[]) for s in l['spans']]
        report.append({'page':i+1,'spans':[{'text':s['text'],'font':s['font'],'size':round(s['size'],2),'color':f"{s['color']:06X}",'bbox':s['bbox']} for s in spans if s['text'].strip()],
                       'lines':[{'rect':list(d['rect']),'color':d['color'],'width':d['width']} for d in page.get_drawings() if d['color']]})
(out/'reference_measurements.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
for page in report:
    print(page['page'],[(s['text'][:40],s['font'],s['size'],s['color']) for s in page['spans'][:4]])
