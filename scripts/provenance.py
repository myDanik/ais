"""Match stored notebook outputs to executable cells and fixed local inputs."""
import hashlib
import json
import os
import sys
from importlib.metadata import version,PackageNotFoundError
from pathlib import Path

def fingerprint(root, notebook):
    root=Path(root)
    code=[c.source for c in notebook.cells if c.cell_type=='code']
    inputs={}
    paths=list((root/'data').glob('*.csv'))+[root/'data'/'manifest.json',root/'course'/'models-lock.json',root/'course'/'requirements-lock.txt']
    for path in sorted(paths):
        if path.exists(): inputs[str(path.relative_to(root))]=hashlib.sha256(path.read_bytes()).hexdigest()
    models=Path(os.environ.get('NLP_MODELS_DIR',root/'.cache'/'models'))
    weights={str(p.relative_to(models)):[p.stat().st_size,p.stat().st_mtime_ns]
             for p in sorted(models.rglob('*')) if p.is_file() and p.suffix in {'.json','.safetensors','.txt','.model'}} if models.exists() else {}
    packages={}
    for name in ['numpy','pandas','scikit-learn','torch','transformers','tokenizers','huggingface-hub','nbclient','matplotlib']:
        try: packages[name]=version(name)
        except PackageNotFoundError: packages[name]=None
    payload=json.dumps({'code':code,'inputs':inputs,'model_files':weights,'python':sys.version,'packages':packages},ensure_ascii=False,sort_keys=True).encode('utf-8')
    return hashlib.sha256(payload).hexdigest()
