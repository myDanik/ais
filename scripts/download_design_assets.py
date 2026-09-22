"""Download declared design dependencies into the project; never execute downloaded scripts."""
import hashlib,json,urllib.request,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def fetch(url,path):
    path.parent.mkdir(parents=True,exist_ok=True)
    if not path.exists():
        request=urllib.request.Request(url,headers={'User-Agent':'NLP-lecture-studio'})
        with urllib.request.urlopen(request,timeout=90) as r:path.write_bytes(r.read())
    return {'url':url,'path':str(path.relative_to(ROOT)).replace('\\','/'),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
records=[]
for family,file in [('prata','Prata-Regular.ttf'),('prata','OFL.txt'),('bodonimoda','BodoniModa[opsz,wght].ttf'),('bodonimoda','OFL.txt')]:
    url='https://raw.githubusercontent.com/google/fonts/main/ofl/'+family+'/'+urllib.parse.quote(file)
    records.append(fetch(url,ROOT/'assets/fonts'/family/file))
release='https://api.github.com/repos/oschwartz10612/poppler-windows/releases/tags/v26.07.0-0'
with urllib.request.urlopen(urllib.request.Request(release,headers={'User-Agent':'NLP-lecture-studio'}),timeout=60) as r:
    metadata=json.load(r)
asset=next(a for a in metadata['assets'] if a['name']=='Release-26.07.0-0.zip')
archive=ROOT/'.tools/downloads'/asset['name']
record=fetch(asset['browser_download_url'],archive)
if asset.get('digest','').startswith('sha256:'):
    assert record['sha256']==asset['digest'].split(':',1)[1]
destination=(ROOT/'.tools/poppler').resolve()
with zipfile.ZipFile(archive) as z:
    for item in z.infolist():
        target=(destination/item.filename).resolve()
        if not target.is_relative_to(destination):raise ValueError('Unsafe archive member')
    z.extractall(destination)
records.append(record)
from fontTools.ttLib import TTFont
for r in records:
    if r['path'].endswith('.ttf'):
        font=TTFont(ROOT/r['path']);cmap=font.getBestCmap()
        r['cyrillic']=all(ord(c) in cmap for c in 'ПриветМодельЯзыкё')
        r['family']=font['name'].getDebugName(1)
(ROOT/'assets/dependencies.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(records,ensure_ascii=False,indent=2))
