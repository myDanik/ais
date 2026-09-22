"""Read-only slide/lecture review support: source links, PDF geometry and QA PNGs."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import subprocess
import fitz

ROOT=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('lesson');ap.add_argument('--render',action='store_true');args=ap.parse_args()
lesson=args.lesson;folder=ROOT/'qa'/lesson/'figma';folder.mkdir(parents=True,exist_ok=True)
paths={k:ROOT/p for k,p in {'lecture_source':f'source/lectures/{lesson}.md','content':f'source/figma/{lesson}_content.json','visuals':f'source/figma/{lesson}_visuals.json','presentation':f'qa/{lesson}/figma/presentation.pdf','lecture_pdf':f'dist/teacher/{lesson}/lecture.pdf'}.items()}
text=paths['lecture_source'].read_text(encoding='utf-8')
content=json.loads(paths['content'].read_text(encoding='utf-8'))
visuals=json.loads(paths['visuals'].read_text(encoding='utf-8'))
heads=list(re.finditer(r'^### Слайд (\d+)\. (.+)$',text,re.M))
evidence={'lesson':lesson,'sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths.values() if p.exists()},'count':{'headings':len(heads),'content':len(content),'visuals':len(visuals)},'source_map':[],'pdfs':{}}
for i,s in enumerate(content):
    h=heads[i];end=heads[i+1].start() if i+1<len(heads) else len(text)
    fragment=text[h.end():end]
    sections=re.findall(r'<!-- (L\d+-S\d+) -->',text[:h.start()])
    row={'slide':i+1,'title':s['title'],'kind':visuals[i]['kind'],'number_matches':int(h.group(1))==i+1,'title_matches':h.group(2)==s['title'],'anchor_in_fragment':s['anchor'] in fragment,'anchor_count_in_lecture':text.count(s['anchor']),'section_matches':sections[-1]==s['section'] if sections else False,'fragment_characters':len(fragment)}
    evidence['source_map'].append(row)

poppler=ROOT/'.tools/poppler/poppler-26.07.0/Library/bin/pdftoppm.exe'
for kind in ['presentation','lecture_pdf']:
    p=paths[kind]
    if not p.exists():evidence['pdfs'][kind]={'status':'not yet exported'};continue
    if p.stat().st_mtime<paths['lecture_source'].stat().st_mtime:
        evidence['pdfs'][kind]={'status':'older than current lecture source; do not approve'};continue
    doc=fitz.open(p);out=folder/('review_png' if kind=='presentation' else 'lecture_png');out.mkdir(exist_ok=True)
    pages=[]
    for n,page in enumerate(doc):
        spans=[s for b in page.get_text('dict')['blocks'] if 'lines' in b for line in b['lines'] for s in line['spans']]
        outside=[{'text':s['text'],'bbox':s['bbox']} for s in spans if s['bbox'][0]<-1 or s['bbox'][1]<-1 or s['bbox'][2]>page.rect.width+1 or s['bbox'][3]>page.rect.height+1]
        pages.append({'page':n+1,'size':[page.rect.width,page.rect.height],'text':page.get_text(),'outside_text':outside})
    evidence['pdfs'][kind]={'status':'current export','pages':pages}
    if args.render:
        if poppler.exists():
            subprocess.run([str(poppler),'-png','-scale-to',('1920' if kind=='presentation' else '1800'),str(p),str(out/'page')],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
        else:
            for n,page in enumerate(doc):
                page.get_pixmap(matrix=fitz.Matrix((1920 if kind=='presentation' else 1800)/max(page.rect.width,page.rect.height),(1920 if kind=='presentation' else 1800)/max(page.rect.width,page.rect.height))).save(out/f'page-{n+1:02}.png')
    if kind=='lecture_pdf':
        markers=[]
        for n,page in enumerate(doc):
            for m in re.finditer(r'Слайд\s+(\d+)\.',page.get_text()):markers.append({'slide':int(m.group(1)),'page':n+1})
        evidence['lecture_switches']=markers

svg_paths=sorted((ROOT/'assets/figma'/lesson).glob('slide-*.svg'))
evidence['svg_count']=len(svg_paths)
for p in svg_paths:evidence['sha256'][str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest()
(folder/'presentation_review_evidence.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'counts':evidence['count'],'source_mismatches':[r for r in evidence['source_map'] if not all(r[k] for k in ['number_matches','title_matches','anchor_in_fragment','section_matches'])],'pdf_status':{k:v['status'] for k,v in evidence['pdfs'].items()},'svg_count':len(svg_paths),'lecture_switches':evidence.get('lecture_switches')},ensure_ascii=False,indent=2))
