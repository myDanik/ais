"""Compare Unicode text and baselines in rendered PPTX against the Figma SVG."""
import argparse,json
from pathlib import Path
import pymupdf as fitz

ROOT=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('--lesson',default='L01');args=ap.parse_args()
q=ROOT/f'qa/{args.lesson}/figma'
g=json.loads((q/'geometry.json').read_text(encoding='utf8'))
pdf=fitz.open(q/'editable.pdf')
adjustments={};report=[]
for i,(page,expected) in enumerate(zip(pdf,g),1):
    actual=[s for b in page.get_text('rawdict')['blocks'] for l in b.get('lines',[]) for s in l['spans']]
    for a in actual:a['text']=''.join(c['c'] for c in a['chars'])
    errors=[];matches=[]
    for j,e in enumerate(expected):
        options=[]
        for a in actual:
            start=0
            while (at:=a['text'].find(e['text'],start))>=0:
                options.append({'origin':a['chars'][at]['origin']})
                start=at+1
        if not options:
            errors.append({'missing':e['text']});continue
        a=min(options,key=lambda item:abs(item['origin'][0]-e['x']/2)+abs(item['origin'][1]-e['baseline']/2))
        dy=a['origin'][1]*2-e['baseline'];dx=a['origin'][0]*2-e['x']
        adjustments[f'{i}:{j}']=-dy
        matches.append({'text':e['text'],'dx_svg_px':round(dx,3),'dy_svg_px':round(dy,3)})
    report.append({'slide':i,'expected':len(expected),'matched':len(matches),'errors':errors,
                   'max_baseline_error_px':round(max([abs(x['dy_svg_px']) for x in matches] or [0]),3),'matches':matches})
(q/'baseline_adjustments.json').write_text(json.dumps(adjustments,indent=2),encoding='utf8')
(q/'powerpoint_comparison.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps([{k:v for k,v in r.items() if k!='matches'} for r in report],ensure_ascii=False))
