from pathlib import Path
import urllib.request,hashlib,json
ROOT=Path(__file__).resolve().parents[1]
url='https://jmlr.org/papers/volume23/21-0998/21-0998.pdf'
p=ROOT/'papers/switch_transformers.pdf';p.parent.mkdir(exist_ok=True)
if not p.exists():
    with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'NLP-lecture-studio'}),timeout=90) as r:p.write_bytes(r.read())
(ROOT/'papers/switch_transformers.source.json').write_text(json.dumps({'url':url,'title':'Switch Transformers','authors':['William Fedus','Barret Zoph','Noam Shazeer'],'year':2022,'venue':'JMLR','sha256':hashlib.sha256(p.read_bytes()).hexdigest()},indent=2),encoding='utf-8')
print(p.stat().st_size)
