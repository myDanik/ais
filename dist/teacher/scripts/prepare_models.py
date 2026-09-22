"""Download public checkpoints once; notebooks subsequently use local files only."""
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault('HF_HOME', str(ROOT / '.cache' / 'huggingface'))
os.environ.setdefault('HF_HUB_DISABLE_SYMLINKS_WARNING', '1')
os.environ.setdefault('HF_HUB_DISABLE_XET', '1')
from huggingface_hub import HfApi, snapshot_download

MODELS = {'encoder': 'cointegrated/rubert-tiny2', 'generator': 'Qwen/Qwen3-0.6B'}
lock_path = ROOT / 'course' / 'models-lock.json'
lock = json.loads(lock_path.read_text(encoding='utf-8')) if lock_path.exists() else {}
for name, repo in MODELS.items():
    entry = lock.get(name)
    if not entry:
        info = HfApi().model_info(repo, token=False)
        entry = {'repo_id': repo, 'revision': info.sha, 'local_dir': f'.cache/models/{name}'}
        lock[name] = entry
        lock_path.parent.mkdir(exist_ok=True)
        lock_path.write_text(json.dumps(lock, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Downloading {repo}@{entry["revision"]}', flush=True)
    snapshot_download(repo_id=repo, revision=entry['revision'], token=False,
                      local_dir=Path(os.environ.get('NLP_MODELS_DIR',ROOT/'.cache'/'models')) / name,
                      allow_patterns=['*.json', '*.safetensors', 'vocab.txt', '*.model', 'merges.txt', 'README.md'],
                      max_workers=2)
print('Models ready. No network is required for the notebooks.', flush=True)
