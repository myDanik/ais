"""Create the single current course at its ordinary dist paths."""
import argparse,hashlib,html,json,re,shutil,sys,zipfile
from pathlib import Path
import nbformat
from pptx import Presentation
R=Path(__file__).resolve().parents[1];D=R/'dist';C=R/'course'
sys.path.insert(0,str(R/'scripts'))
from build_documents import convert,to_pdf
TOPICS=['Как компьютер работает с текстом','Классификация текста','Эмбеддинги и поиск','Как языковая модель продолжает текст','Внимание и Transformer','Предобученный энкодер','Инструкции и ответы LLM','RAG: ответ по документам']
PUBLIC=['RPD','START','ASSESSMENT','EXAM_TICKETS'];PRIVATE=['EXAM_KEYS','PRESENTATION_DESIGN','PRESENTATION_MCP_RESEARCH']
def copy(src,dst):dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def slide_count(n):
 ending='слайдов' if 11<=n%100<=14 else ('слайд' if n%10==1 else 'слайда' if 2<=n%10<=4 else 'слайдов')
 return f'{n} {ending}'
def sidecars(lessons=None):
 for n in (lessons if lessons is not None else range(1,9)):
  lid=f'L{n:02}';spec=json.loads((R/'source/slides'/f'{lid}.json').read_text(encoding='utf-8'))
  lecture=(R/spec['lecture']).read_text(encoding='utf-8');out=D/'teacher'/lid
  notes=['# Заметки к презентации', '',TOPICS[n-1],''];mapping=['# Связь презентации и лекции','',TOPICS[n-1],'']
  for i,s in enumerate(spec['slides'],1):
   assert s['anchor'] in lecture
   heading=(s.get('title') or TOPICS[n-1]).replace('\n',' ')
   notes += [f'## {i:02}. {heading}','',s['notes'],'']
   paragraph=next((p for p in lecture.split('\n\n') if s['anchor'] in p),s['anchor'])
   mapping += [f'## Слайд {i:02}. {heading}','',f'Раздел: `{s["section"]}`. Идентификатор слайда: `{s["id"]}`.','',paragraph,'']
  for stem,lines in [('speaker_notes',notes),('slide_map',mapping)]:
   source=out/f'{stem}.md';body='\n'.join(lines)
   if source.exists() and source.read_text(encoding='utf-8')==body and source.with_suffix('.pdf').exists():continue
   source.write_text(body,encoding='utf-8');convert(source,source.with_suffix('.docx'));to_pdf(source.with_suffix('.docx'))
  print('Sidecars',lid,flush=True)
def index(folder,audience):
 teacher=audience=='teacher';label='Преподавателю' if teacher else 'Студенту';rows=[];count=0
 md=[f'# Курс NLP · {label.lower()}','', 'Редакция 2. Восемь лекций и восемь лабораторных; 72 академических часа.','',
 '- [РПД](course/RPD.pdf)','- [Начало работы](course/START.pdf)','- [Оценивание](course/ASSESSMENT.pdf)','- [16 билетов](course/EXAM_TICKETS.pdf)','',
 '| Тема | Материалы |','|---|---|']
 for n,topic in enumerate(TOPICS,1):
  lid=f'L{n:02}';nb='solution.ipynb' if teacher else 'lab.ipynb';slides=len(Presentation(folder/lid/'presentation.pptx').slides);count+=slides
  links=[('Лекция PDF',f'{lid}/lecture.pdf'),('Лекция DOCX',f'{lid}/lecture.docx'),('PowerPoint',f'{lid}/presentation.pptx'),('Слайды PDF',f'{lid}/presentation.pdf'),('Методичка',f'{lid}/lab_guide.pdf'),('Ноутбук',f'{lid}/{nb}')]
  figma_file=R/'source/figma'/f'{lid}_file.json'
  if figma_file.exists():links.insert(2,('Figma Slides',json.loads(figma_file.read_text(encoding='utf-8'))['url']))
  if teacher:links += [('План',f'{lid}/plan.pdf'),('Заметки',f'{lid}/speaker_notes.pdf'),('Карта слайдов',f'{lid}/slide_map.pdf')]
  md.append(f'| {n}. {topic} | '+' · '.join(f'[{a}]({b})' for a,b in links)+' |')
  rows.append(f'<tr><td class="n">{n:02}</td><td><h2>{html.escape(topic)}</h2><p class="links">'+''.join(f'<a href="{b}">{a}</a>' for a,b in links)+f'</p><small>{slide_count(slides)}</small></td></tr>')
 extras=''
 if teacher:
  extras='<a href="course/EXAM_KEYS.pdf">Ключи зачёта</a><a href="QA_SUMMARY.md">Проверки</a>'
  md += ['','- [Ключи зачёта](course/EXAM_KEYS.pdf)','- [Проверки материалов](QA_SUMMARY.md)','', 'Исходные журналы генерации находятся в outputs/L07 и outputs/L08.']
 md+=['','Ноутбуки открываются в JupyterLab. Подготовьте среду и модели по START. Для редактирования PPTX нужны Prata и Carlito из assets/fonts; в PDF шрифты уже сохранены.']
 (folder/'README.md').write_text('\n'.join(md),encoding='utf-8')
 page=f'''<!doctype html><html lang="ru"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>NLP · {label}</title>
<style>@font-face{{font-family:Prata;src:url(assets/fonts/prata/Prata-Regular.ttf)}}*{{box-sizing:border-box}}body{{margin:0;background:white;color:#15211e;font:17px/1.5 Arial,sans-serif}}main{{max-width:1100px;margin:auto;padding:55px 28px}}h1{{font:48px/1.25 Prata,Georgia,serif;max-width:950px;border-bottom:2px solid #1d9a78;padding-bottom:25px}}h2{{font-size:23px;margin:0 0 12px}}a{{color:#0070c0;text-underline-offset:4px}}nav,.links{{display:flex;gap:13px 20px;flex-wrap:wrap}}nav{{margin:30px 0}}table{{width:100%;border-collapse:collapse}}td{{border-top:1px solid #dce4df;padding:23px 0;vertical-align:top}}.n{{width:65px;color:#1d9a78;font-size:25px}}small{{color:#63756c}}.links{{font-size:15px;margin:0 0 8px}}@media(max-width:600px){{h1{{font-size:32px}}main{{padding:25px 18px}}}}</style>
<main><small>СИСТЕМЫ ИСКУССТВЕННОГО ИНТЕЛЛЕКТА · РЕДАКЦИЯ 2</small><h1>Обработка естественного языка</h1><p>{label} · 8 лекций · {slide_count(count)} · 8 лабораторных</p><nav><a href="course/RPD.pdf">РПД</a><a href="course/START.pdf">Начать работу</a><a href="course/ASSESSMENT.pdf">Оценивание</a><a href="course/EXAM_TICKETS.pdf">16 билетов</a>{extras}</nav><table>{''.join(rows)}</table><p>Ноутбуки открываются в JupyterLab. Все обращения и правила университета «Север» созданы для учебных задач.</p></main></html>'''
 (folder/'INDEX.html').write_text(page,encoding='utf-8')
 return count
def stage():
 counts=[]
 for audience in ['student','teacher']:
  target=D/audience;target.mkdir(parents=True,exist_ok=True)
  for p in (R/'data').iterdir():
   if p.is_file():copy(p,target/'data'/p.name)
  for name in PUBLIC+(PRIVATE if audience=='teacher' else []):
   for ext in ['md','docx','pdf']:copy(C/f'{name}.{ext}',target/'course'/f'{name}.{ext}')
  for name in ['requirements-lock.txt','models-lock.json']:copy(R/'course'/name,target/'course'/name)
  copy(R/'scripts/prepare_models.py',target/'scripts/prepare_models.py')
  for p in (R/'assets/fonts/prata').iterdir():copy(p,target/'assets/fonts/prata'/p.name)
  for p in (R/'assets/fonts/carlito').iterdir():copy(p,target/'assets/fonts/carlito'/p.name)
  if audience=='student':
   for n in range(1,9):
    lid=f'L{n:02}'
    for ext in ['pptx','pdf']:copy(D/'teacher'/lid/f'presentation.{ext}',target/lid/f'presentation.{ext}')
  else:
   for n in [7,8]:
    for p in (R/'outputs'/f'L{n:02}').iterdir():
     if p.is_file():copy(p,target/'outputs'/f'L{n:02}'/p.name)
   for p in (R/'qa').glob('*.md'):
    if p.name!='README.md':copy(p,target/'reviews'/p.name)
   (target/'reviews/README.md').write_text('# Рецензии курса\n\nТекущие проверки Figma, PowerPoint, языка и чисел имеют имена Lxx_figma_*.md. Общая приёмка оставшихся тем — remaining_package_review.md. Полная сводка находится в ../QA_SUMMARY.md.\n\nРанние отчёты сохранены как история исправлений; их оценки прежних макетов не заменяют приёмку текущих презентаций.\n',encoding='utf-8')
   for n in range(1,9):
    lid=f'L{n:02}'
    for p in (R/'qa'/lid/'figma').glob('*review.md'):copy(p,target/'reviews'/f'{lid}_figma_{p.name}')
  counts.append(index(target,audience))
 assert len(set(counts))==1
 (D/'INDEX.html').write_text(f'''<!doctype html><html lang="ru"><meta charset="utf-8"><title>Курс NLP · редакция 2</title><style>body{{font:21px/1.7 Arial;max-width:900px;margin:65px auto;padding:25px;color:#17261e}}h1{{font-family:Georgia;border-bottom:2px solid #1d9a78}}a{{color:#0070c0}}</style><h1>Курс NLP · редакция 2</h1><p>8 лекций · {slide_count(counts[0])} · 8 лабораторных · 16 билетов</p><p><a href="teacher/INDEX.html">Материалы преподавателя</a></p><p><a href="student/INDEX.html">Материалы студента</a></p><p><a href="NLP_teacher.zip">Архив преподавателя</a> · <a href="NLP_student.zip">Архив студента</a> · <a href="NLP_sources.zip">Исходники</a></p></html>''',encoding='utf-8')
 print('Portable distribution staged;',counts[0],'slides',flush=True)
def archives():
 for audience in ['student','teacher']:
  base=D/audience
  files=[p for p in base.rglob('*') if p.is_file() and not any(x in {'.ipynb_checkpoints','__pycache__','.cache','.venv'} for x in p.relative_to(base).parts) and p.name!='FILES_SHA256.json']
  if audience=='student':assert not any('solution' in p.name or 'EXAM_KEYS' in p.name or 'run_records' in p.name for p in files)
  manifest={p.relative_to(base).as_posix():digest(p) for p in files};(base/'FILES_SHA256.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8');files.append(base/'FILES_SHA256.json')
  archive=D/f'NLP_{audience}.zip'
  with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
   for p in sorted(files):z.write(p,f'NLP_{audience}/{p.relative_to(base).as_posix()}')
  print(archive.name,archive.stat().st_size,flush=True)
 paths=[]
 for name in ['src','source','scripts','course','data','assets/fonts/prata','assets/fonts/carlito','assets/figma','assets/generated','papers']:
  paths += [p for p in (R/name).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix in {'.ts','.js','.py','.mjs','.md','.json','.csv','.txt','.tex','.svg','.png','.ttf','.pdf'} and (name!='source/labs' or p.suffix=='.py') and (name!='course' or p.suffix!='.pdf')]
 for name in ['package.json','package-lock.json','tsconfig.json','requirements.txt','SKILL.md','PRESENTATIONS.md']:paths.append(R/name)
 for name in ['src','package.json','package-lock.json','tsconfig.json','LICENSE','README.md']:
  p=R/'.tools/mypoint-mcp'/name
  if p.is_dir():paths += [x for x in p.rglob('*') if x.is_file()]
  elif p.exists():paths.append(p)
 paths += [p for p in (R/'qa').glob('*') if p.is_file() and p.suffix in {'.md','.json'} and p.name!='archive_integrity.json']
 for n in range(1,9):
  paths += [p for p in (R/f'qa/L{n:02}/figma').glob('*review.md') if p.is_file()]
  for name in ['facts_evidence.json','powerpoint_comparison.json','geometry.json','final_figma_state.json','grid_bounds.json','narrative_evidence.json','presentation_review_evidence.json','powerpoint_review_evidence.json']:
   p=R/f'qa/L{n:02}/figma'/name
   if p.exists():paths.append(p)
 for n in range(1,9):
  for name in ['execution.json','mcp_calls.json']:
   p=R/'qa'/f'L{n:02}'/name
   if p.exists():paths.append(p)
 with zipfile.ZipFile(D/'NLP_sources.zip','w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  z.write(C/'REBUILD.md','NLP_sources/README.md')
  for p in sorted(set(paths)):z.write(p,'NLP_sources/'+p.relative_to(R).as_posix())
 hashes={p.name:digest(p) for p in D.glob('NLP_*.zip')};(D/'ARCHIVES_SHA256.json').write_text(json.dumps(hashes,indent=2),encoding='utf-8')
 print('Source archive and archive hashes written',flush=True)
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--stage-only',action='store_true');ap.add_argument('--skip-sidecars',action='store_true');args=ap.parse_args()
 if not args.skip_sidecars:sidecars()
 stage()
 if not args.stage_only:archives()
