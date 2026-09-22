"""Verify the revised two-text demo using only the pinned tokenizer, no encoder weights."""
from pathlib import Path
import hashlib
import importlib.metadata
import json
from transformers import AutoTokenizer

ROOT=Path(__file__).resolve().parents[3]
model=ROOT/'.cache/models/encoder'
tokenizer=AutoTokenizer.from_pretrained(model,local_files_only=True)
texts=['Как продлить книгу?','Спасибо']
separate=tokenizer(texts,padding=False,truncation=False)
batch=tokenizer(texts,padding=True,truncation=False)
tokens=[tokenizer.convert_ids_to_tokens(ids) for ids in batch['input_ids']]
assert [len(x) for x in separate['input_ids']]==[6,3]
assert tokens==[['[CLS]','Как','продлить','книгу','?','[SEP]'],['[CLS]','Спасибо','[SEP]','[PAD]','[PAD]','[PAD]']]
assert batch['attention_mask']==[[1,1,1,1,1,1],[1,1,1,0,0,0]]
config=json.loads((model/'config.json').read_text(encoding='utf-8'))
assert config['hidden_size']==312
result={'texts':texts,'lengths_without_padding':[6,3],'batch':dict(batch),'tokens':tokens,
        'batch_shape':[2,6],'hidden_shape_from_config':[2,6,312],'cls_shape_from_config':[2,312],
        'encoder_inference_performed':False,'transformers_version':importlib.metadata.version('transformers'),
        'sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [model/'tokenizer.json',model/'tokenizer_config.json',model/'config.json',ROOT/'course/models-lock.json']}}
(Path(__file__).parent/'demo_batch_evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
