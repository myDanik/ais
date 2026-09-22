"""Read-only checks of data used by the L08 presentation; writes QA evidence only."""
from pathlib import Path
import ast
import csv
import gc
import hashlib
import json
import os

os.environ['HF_HUB_OFFLINE'] = '1'
os.environ['TRANSFORMERS_OFFLINE'] = '1'
import numpy as np
import torch
from transformers import AutoModel, AutoTokenizer

torch.set_num_threads(4)
root = Path(__file__).resolve().parents[2]
os.chdir(root)
records = json.loads(Path('outputs/L08/run_records.json').read_text(encoding='utf-8'))
documents = list(csv.DictReader(Path('data/knowledge.csv').open(encoding='utf-8-sig', newline='')))
queries = list(csv.DictReader(Path('data/retrieval_queries.csv').open(encoding='utf-8-sig', newline='')))
by_id = {r['doc_id']: dict(doc_id=r['doc_id'], title=r['title'], text=r['text'], start=0, end=len(r['text'])) for r in documents}
query_by_id = {r['query_id']: r for r in queries}

enc_tok = AutoTokenizer.from_pretrained('.cache/models/encoder', local_files_only=True)
encoder, info = AutoModel.from_pretrained('.cache/models/encoder', local_files_only=True, dtype=torch.float32, output_loading_info=True)
assert not info['missing_keys'] and not info['mismatched_keys'] and not info['error_msgs']
assert all(k.startswith('cls.') for k in info['unexpected_keys'])
encoder.eval().requires_grad_(False)

def encode(texts):
    parts = []
    with torch.inference_mode():
        for i in range(0, len(texts), 16):
            batch = enc_tok(texts[i:i+16], padding=True, truncation=True, max_length=128, return_tensors='pt')
            parts.append(torch.nn.functional.normalize(encoder(**batch).last_hidden_state[:, 0, :], dim=1).numpy())
    return np.concatenate(parts)

doc_texts = [r['title'] + '. ' + r['text'] for r in documents]
doc_lengths = [len(x) for x in enc_tok(doc_texts, truncation=False)['input_ids']]
query_lengths = [len(x) for x in enc_tok([r['query'] for r in queries], truncation=False)['input_ids']]
assert max(doc_lengths + query_lengths) <= 128
D, Q = encode(doc_texts), encode([r['query'] for r in queries])
scores = Q @ D.T
ids = [r['doc_id'] for r in documents]
ranks = {}
max_score_delta = 0.0
for i, q in enumerate(queries):
    order = sorted(range(len(ids)), key=lambda j: (-float(scores[i, j]), ids[j]))[:3]
    top = [ids[j] for j in order]
    expected = records['rankings'][q['query_id']]
    assert top == expected['top3'], (q['query_id'], top, expected['top3'])
    rank = top.index(q['relevant_doc']) + 1 if q['relevant_doc'] in top else None
    assert rank == expected['rank3']
    ranks[q['query_id']] = rank
    max_score_delta = max(max_score_delta, max(abs(float(scores[i, j]) - e) for j, e in zip(order, expected['scores'])))
metrics = {}
for split in ['validation', 'test']:
    sample = [ranks[q['query_id']] for q in queries if q['split'] == split and q['relevant_doc']]
    metrics[split] = dict(n=len(sample), recall1=sum(r == 1 for r in sample)/len(sample), recall3=sum(r is not None for r in sample)/len(sample), mrr3=sum(1/r if r else 0 for r in sample)/len(sample))
    assert all(np.isclose(v, records['metrics'][split][k]) for k, v in metrics[split].items())
del encoder, enc_tok
gc.collect()

tokenizer = AutoTokenizer.from_pretrained('.cache/models/generator', local_files_only=True)
all_runs = records['runs'] + records['diagnostics']
lengths = []
for run in all_runs:
    rendered = tokenizer.apply_chat_template(run['messages'], tokenize=False, add_generation_prompt=True, enable_thinking=False)
    assert rendered == run['rendered']
    length = len(tokenizer(rendered, add_special_tokens=False)['input_ids'])
    assert length == run['input_tokens'] and length <= 768
    assert [c['doc_id'] for c in run['context']] == run['included_ids']
    for c in run['context']:
        assert c['start'] == 0 and c['end'] == len(c['text'])
        if run['mode'] == 'injection' and c['doc_id'] == 'D03':
            assert c['text'].startswith(by_id['D03']['text'] + '\n')
        else:
            assert c == by_id[c['doc_id']]
    lengths.append(dict(query_id=run['query_id'], mode=run['mode'], actual_input_tokens=length, new_tokens=run['new_tokens'], stop=run['stop']))

nb = json.loads(Path('dist/teacher/L08/solution.ipynb').read_text(encoding='utf-8'))
namespace = {'tokenizer': tokenizer, 'MAX_INPUT': 768, 'SYSTEM': records['runs'][0]['messages'][0]['content']}
for cell in nb['cells']:
    if cell['cell_type'] != 'code':
        continue
    for node in ast.parse(''.join(cell['source'])).body:
        if isinstance(node, ast.FunctionDef) and node.name in {'render_input', 'pack_context'}:
            exec(compile(ast.Module(body=[node], type_ignores=[]), '<reviewed notebook function>', 'exec'), namespace)
pack = namespace['pack_context']
for run in all_runs:
    packed = pack(query_by_id[run['query_id']]['query'], run['context'])
    assert packed['rendered'] == run['rendered']
huge_text = by_id['D03']['text'] * 100
huge = dict(by_id['D03'], text=huge_text, end=len(huge_text))
budget_pack = pack(query_by_id['Q05']['query'], [huge, by_id['D04']])
assert budget_pack['retrieved_ids'] == ['D03', 'D04']
assert budget_pack['included_ids'] == ['D04']
assert budget_pack['omitted'] == [{'doc_id': 'D03', 'reason': 'budget'}]
try:
    pack(query_by_id['Q05']['query'] * 1000, [])
except ValueError:
    long_question_rejected = True
else:
    raise AssertionError('Long question accepted')

ev_path = Path('qa/L08_presentation_review_evidence_01.json')
ev = json.loads(ev_path.read_text(encoding='utf-8'))
checks = dict(fresh_encoder_shapes={'D': list(D.shape), 'Q': list(Q.shape), 'scores': list(scores.shape)}, doc_lengths=[min(doc_lengths), max(doc_lengths)], query_lengths=[min(query_lengths), max(query_lengths)], metrics=metrics, ranks=ranks, ranking_top3_matches=30, maximum_score_delta=max_score_delta, fresh_generator_tokenizer_lengths=lengths, all_context_provenance_valid=True, all_14_inputs_reconstructed_exactly=True, fresh_budget_test={k: budget_pack[k] for k in ['retrieved_ids', 'included_ids', 'omitted', 'input_tokens']}, long_question_rejected=long_question_rejected, fresh_generation_performed=False, all_snapshot_hashes_unchanged=all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in ev['sha256'].items()))
ev['independent_computation'] = checks
ev_path.write_text(json.dumps(ev, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(checks, ensure_ascii=False, indent=2))
