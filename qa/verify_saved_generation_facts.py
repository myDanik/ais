"""Verify saved observations, source consistency, token lengths and index arithmetic; no model inference."""
from pathlib import Path
import hashlib
import importlib.metadata
import json
import sys
import numpy as np
import pandas as pd
from transformers import AutoTokenizer

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from build_labs import load_spec,SETUP

def read(path): return json.loads((ROOT/path).read_text(encoding='utf-8'))
def save(lesson,extra):
    path=ROOT/f'qa/{lesson}/figma/facts_evidence.json'
    result=json.loads(path.read_text(encoding='utf-8'));result.update(extra)
    path.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')

for n in range(3,9):
    lesson=f'L{n:02}'
    prose=read(f'source/labs/{lesson}.json');original=load_spec(n)
    expected=[SETUP.replace('print("Данные:", DATA)\n','')]
    ti=ci=0
    for item in original['cells']:
        if item['kind']=='code':
            expected.append(prose.get('code_overrides',{}).get(str(ci),item['text']));ci+=1
        elif item['kind']=='task':
            expected.extend(d['text'] for d in prose.get('before_task',{}).get(str(ti),[]) if d['kind']=='code')
            expected.append(prose.get('solution_overrides',{}).get(str(ti),item['solution']))
            check=prose.get('check_overrides',{}).get(str(ti),item['check'])
            if check:expected.append(check)
            ti+=1
    actual=[''.join(c['source']) for c in read(f'dist/teacher/{lesson}/solution.ipynb')['cells'] if c['cell_type']=='code']
    assert expected==actual,lesson
    save(lesson,{'code_matches_current_lab_sources':True,'matched_code_cells':len(actual)})
    print(lesson,'all code cells match current source specifications',len(actual),flush=True)

tok=AutoTokenizer.from_pretrained(ROOT/'.cache/models/generator',local_files_only=True)
docs=pd.read_csv(ROOT/'data/knowledge.csv',keep_default_na=False)
queries=pd.read_csv(ROOT/'data/retrieval_queries.csv',keep_default_na=False)
docmap=docs.set_index('doc_id').to_dict('index')
qmap=queries.set_index('query_id').to_dict('index')
record7=read('outputs/L07/run_records.json')
rows7=record7['prompt_runs']+record7['decoding_runs']+[record7['json_run']]
outputs7=''.join(''.join(o.get('text',[])) for c in read('dist/teacher/L07/solution.ipynb')['cells'] for o in c.get('outputs',[]))
for row in rows7:
    rendered=tok.apply_chat_template([{'role':'system','content':record7['system']},{'role':'user','content':row['prompt']}],tokenize=False,add_generation_prompt=True,enable_thinking=False)
    assert len(tok(rendered,add_special_tokens=False)['input_ids'])==row['input_tokens']
    assert repr(row['text']) in outputs7
    assert docmap['D03']['text'] in row['prompt']
assert len(rows7)==11
assert all(r['text']=='14 дней.' for r in record7['decoding_runs'])
assert json.loads(record7['json_run']['text'])=={'answer':'14','has_answer':True}
utils=ROOT/'.venv/Lib/site-packages/transformers/generation/utils.py'
lines=utils.read_text(encoding='utf-8').splitlines()
warpers={name:[i+1 for i,line in enumerate(lines) if 'processors.append' in line and name in line or name+'(top_' in line] for name in ['TemperatureLogitsWarper','TopKLogitsWarper','TopPLogitsWarper']}
assert warpers['TemperatureLogitsWarper'][0]<warpers['TopKLogitsWarper'][0]<warpers['TopPLogitsWarper'][0]
save('L07',{'saved_rows_verified':len(rows7),'exact_texts_match_notebook':True,'all_input_lengths_retokenized':True,'transformers_version':importlib.metadata.version('transformers'),'warper_lines':warpers,'runs_summary':[{k:r.get(k) for k in ['question_id','variant','text','input_tokens','new_tokens','stop','mode','temperature','top_p','top_k','seed']} for r in rows7]})

record8=read('outputs/L08/run_records.json')
index=np.load(ROOT/'outputs/L08/index_vectors.npz',allow_pickle=False)
D,Q=index['documents'],index['queries']
assert list(index['doc_ids'])==docs.doc_id.tolist() and list(index['query_ids'])==queries.query_id.tolist()
assert D.shape==(12,312) and Q.shape==(30,312)
scores=Q@D.T;ranks={}
for i,row in enumerate(queries.itertuples()):
    order=sorted(range(len(D)),key=lambda j:(-float(scores[i,j]),docs.iloc[j].doc_id))[:3]
    ids=[docs.iloc[j].doc_id for j in order]
    recorded=record8['rankings'][row.query_id]
    assert ids==recorded['top3']
    assert np.allclose([scores[i,j] for j in order],recorded['scores'],atol=1e-7)
    rank=ids.index(row.relevant_doc)+1 if row.relevant_doc in ids else None
    assert rank==recorded['rank3'];ranks[row.query_id]=rank
metrics={}
for split in ['validation','test']:
    rs=[ranks[r.query_id] for r in queries.itertuples() if r.split==split and r.relevant_doc]
    metrics[split]={'n':len(rs),'recall1':sum(r==1 for r in rs)/len(rs),'recall3':sum(r is not None for r in rs)/len(rs),'mrr3':sum(1/r if r else 0 for r in rs)/len(rs),'rank_counts':{str(v):rs.count(v) for v in [1,2,3,None]}}
    assert all(abs(metrics[split][k]-v)<1e-10 for k,v in record8['metrics'][split].items())
rows8=record8['runs']+record8['diagnostics']
outputs8=''.join(''.join(o.get('text',[])) for c in read('dist/teacher/L08/solution.ipynb')['cells'] for o in c.get('outputs',[]))
for row in rows8:
    rendered=tok.apply_chat_template(row['messages'],tokenize=False,add_generation_prompt=True,enable_thinking=False)
    assert rendered==row['rendered']
    assert len(tok(rendered,add_special_tokens=False)['input_ids'])==row['input_tokens']
    assert repr(row['text']) in outputs8
    assert row['included_ids']==[c['doc_id'] for c in row['context']]
    for c in row['context']:
        assert c['start']==0 and c['end']==len(c['text'])
        assert c['text']==docmap[c['doc_id']]['text'] or (row['mode']=='injection' and c['doc_id']=='D03')
    if row['mode']=='rag':assert row['retrieved_ids']==row['included_ids']==record8['rankings'][row['query_id']]['top3']
assert len(rows8)==14 and all(r['stop']=='EOS' for r in rows8)
enc=AutoTokenizer.from_pretrained(ROOT/'.cache/models/encoder',local_files_only=True)
dl=[len(x) for x in enc((docs.title+'. '+docs.text).tolist(),truncation=False)['input_ids']]
ql=[len(x) for x in enc(queries['query'].tolist(),truncation=False)['input_ids']]
save('L08',{'saved_rows_verified':len(rows8),'exact_texts_match_notebook':True,'all_rendered_inputs_and_lengths_verified':True,'index_arithmetic_verified':True,'metrics_recomputed':metrics,'encoder_doc_length_range':[min(dl),max(dl)],'encoder_query_length_range':[min(ql),max(ql)],'all_context_boundaries_verified':True,'runs_summary':[{k:r[k] for k in ['query_id','mode','retrieved_ids','included_ids','input_tokens','new_tokens','stop','text','citations','unknown','exact_refusal']} for r in rows8]})
print('L07: all 11 saved texts and prompt lengths verified; L08: all 14 texts, input lengths, source boundaries, 30 rankings and metrics verified; no inference.',flush=True)
