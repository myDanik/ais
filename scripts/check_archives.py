"""Verify ZIP contents against their own manifests and the current staged files."""
import hashlib,json,zipfile
from pathlib import Path
R=Path(__file__).resolve().parents[1];D=R/'dist';report={}
for audience in ['student','teacher']:
 path=D/f'NLP_{audience}.zip';prefix=f'NLP_{audience}/'
 with zipfile.ZipFile(path) as z:
  assert z.testzip() is None,path
  names=z.namelist();assert len(names)==len(set(names))
  assert not any('..' in Path(n).parts or not n.startswith(prefix) for n in names)
  manifest=json.loads(z.read(prefix+'FILES_SHA256.json'))
  assert set(names)=={prefix+p for p in manifest}|{prefix+'FILES_SHA256.json'}
  for name,sha in manifest.items():
   assert hashlib.sha256(z.read(prefix+name)).hexdigest()==sha,name
   assert hashlib.sha256((D/audience/name).read_bytes()).hexdigest()==sha,'Stale archive: '+name
  if audience=='student':assert not any('solution.ipynb' in p or 'EXAM_KEYS' in p or 'run_records' in p for p in names)
  report[audience]={'files':len(names),'bytes':path.stat().st_size,'status':'passed'}
with zipfile.ZipFile(D/'NLP_sources.zip') as z:
 assert z.testzip() is None
 names=set(z.namelist());prefix='NLP_sources/'
 required=['README.md','SKILL.md','PRESENTATIONS.md','src/theme.ts','src/components.ts','src/build.ts','package.json','package-lock.json','requirements.txt','scripts/setup_mcp.mjs','.tools/mypoint-mcp/src/index.ts','.tools/mypoint-mcp/package-lock.json','scripts/package_course.py','scripts/build_notebooks.py','scripts/build_documents.py','scripts/build_common.py','scripts/mcp_render.mjs','scripts/render_presentation.py','assets/fonts/prata/Prata-Regular.ttf','assets/fonts/prata/OFL.txt','papers/switch_transformers.pdf']
 for n in range(1,9):required += [f'source/lectures/L{n:02}.md',f'source/labs/L{n:02}.json',f'source/labs/L{n:02}.py',f'src/lecture{n}.ts']
 for p in required:assert prefix+p in names,'Missing source: '+p
 assert not any('/node_modules/' in p or '/.venv/' in p or '/.cache/' in p for p in names)
 for n in names:
  if n.endswith('.py'):compile(z.read(n).decode('utf-8'),n,'exec')
 report['sources']={'files':len(names),'bytes':(D/'NLP_sources.zip').stat().st_size,'status':'passed'}
hashes=json.loads((D/'ARCHIVES_SHA256.json').read_text(encoding='utf-8'))
assert all(hashlib.sha256((D/n).read_bytes()).hexdigest()==h for n,h in hashes.items())
(R/'qa/archive_integrity.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
