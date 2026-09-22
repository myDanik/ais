"""Independent fact audit; writes evidence only under qa, never course material."""
from pathlib import Path
import contextlib
import hashlib
import io
import json
import os
import sys

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)
os.environ['MPLBACKEND'] = 'Agg'
os.environ['MPLCONFIGDIR'] = str(ROOT/'qa'/'matplotlib-cache')
def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def basic(lesson):
    paths = [ROOT/f'source/lectures/{lesson}.md', ROOT/f'source/labs/{lesson}.py',
             ROOT/f'source/labs/{lesson}.json', ROOT/f'dist/teacher/{lesson}/solution.ipynb']
    nb = json.loads(paths[-1].read_text(encoding='utf-8'))
    cells = [c for c in nb['cells'] if c['cell_type']=='code']
    result = {'lesson': lesson, 'sha256': {str(p.relative_to(ROOT)):digest(p) for p in paths},
              'code_cells': len(cells), 'execution_counts': [c.get('execution_count') for c in cells],
              'errors': [o for c in cells for o in c.get('outputs',[]) if o.get('output_type')=='error'],
              'data_copies': {}}
    for name in ['requests.csv','knowledge.csv','retrieval_queries.csv']:
        a,b = ROOT/'data'/name, ROOT/'dist/teacher/data'/name
        result['data_copies'][name] = {'sha256':digest(a),'identical': a.read_bytes()==b.read_bytes()}
    for p in [ROOT/f'outputs/{lesson}/run_records.json',ROOT/f'outputs/{lesson}/index_vectors.npz']:
        if p.exists(): result['sha256'][str(p.relative_to(ROOT))]=digest(p)
    return nb,result

for lesson in sys.argv[1:] or ['L03','L04','L05','L06','L07','L08']:
    nb, result = basic(lesson)
    if lesson in {'L03','L04','L05'}:
        ns={'display':lambda *args,**kw:None}
        with contextlib.redirect_stdout(io.StringIO()):
            for c in nb['cells']:
                if c['cell_type']=='code': exec(compile(''.join(c['source']),lesson,'exec'),ns)
        result['lightweight_reexecution']='passed; all original assertions; no model downloads or neural inference'
        if lesson=='L03':
            result['metrics']=ns['results_table'].to_dict('records')
            result['shapes']={'tfidf':list(ns['X_docs'].shape),'svd':list(ns['Z_docs'].shape),'tfidf_nnz':ns['X_docs'].nnz}
            result['diagnostics']={q:{m:ns['search'](q,m,3).to_dict('records') for m in ['tfidf','svd']} for q in ['Какие сведения нужны при технической ошибке?','Сколько рублей составляет академическая стипендия?','Кто выдаёт ключи при заселении?']}
        if lesson=='L04':
            result['comparison']=ns['comparison'].to_dict('records')
            result['test']=ns['test_result'];result['coverage']=ns['coverage']
            result['vocab_size']=len(ns['vocab']);result['generations']=ns['generations']
        if lesson=='L05':
            result['arrays']={k:v.tolist() for k,v in ns.items() if k in ['Q','K','V','scores','weights','out','causal_weights','causal_out','masked_weights','masked_out'] and hasattr(v,'tolist')}
    dest=ROOT/'qa'/lesson/'figma';dest.mkdir(parents=True,exist_ok=True)
    (dest/'facts_evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(lesson,result['code_cells'],result['execution_counts'],'errors',len(result['errors']),result.get('lightweight_reexecution','saved output inspection only'))
