"""Download approved Figma exports and public design assets into this workspace."""
import argparse,hashlib,json
from pathlib import Path
from urllib.request import urlopen,Request
ROOT=Path(__file__).resolve().parents[1]
def download(url,destination):
    target=(ROOT/destination).resolve()
    if not target.is_relative_to(ROOT):raise ValueError('Destination outside workspace')
    with urlopen(Request(url,headers={'User-Agent':'NLP-Lecture-Authoring'}),timeout=45) as response:data=response.read()
    if target.suffix=='.pdf' and not data.startswith(b'%PDF'):raise ValueError('Not a PDF export')
    target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    print(json.dumps({'file':str(target.relative_to(ROOT)),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}),flush=True)
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('url',nargs='?');ap.add_argument('destination',nargs='?');ap.add_argument('--manifest',type=Path);args=ap.parse_args()
    if args.manifest:
        for item in json.loads(args.manifest.read_text(encoding='utf-8')):download(item['url'],item['destination'])
    else:download(args.url,args.destination)
