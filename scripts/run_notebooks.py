"""Execute instructor notebooks in fresh local kernels and record resource use."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import time
ROOT=Path(__file__).resolve().parents[1]
for key,subdir in [('IPYTHONDIR','ipython'),('JUPYTER_CONFIG_DIR','jupyter_config'),('JUPYTER_RUNTIME_DIR','jupyter_runtime')]:
    os.environ[key]=str(ROOT/'.cache'/subdir)
os.environ['JUPYTER_PATH']=str(ROOT/'.venv'/'share'/'jupyter')
os.environ['HF_HUB_OFFLINE']='1'; os.environ['TRANSFORMERS_OFFLINE']='1'
os.environ['TOKENIZERS_PARALLELISM']='false'; os.environ['MPLCONFIGDIR']=str(ROOT/'.cache'/'matplotlib')
def run_one(n):
    from run_notebook import run
    run(n)

if __name__ == '__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--lesson',type=int,required=True)
    run_one(ap.parse_args().lesson)
