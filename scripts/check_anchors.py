import json,re,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1]
for lid in sys.argv[1:]:
 d=json.loads((R/'source/slides'/f'{lid}.json').read_text(encoding='utf-8'))
 lecture=(R/d['lecture']).read_text(encoding='utf-8')
 for s in d['slides']:
  if s['anchor'] not in lecture:print(lid,s['id'],'MISSING',s['anchor'])
  elif s['anchor'] not in lecture.split('<!-- '+s['section']+' -->',1)[-1].split('<!-- ',1)[0]:print(lid,s['id'],'WRONG SECTION')
