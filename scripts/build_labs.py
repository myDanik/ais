"""Build student scaffolds and instructor solutions from authored lab specs."""
import argparse
import importlib.util
import json
import shutil
from pathlib import Path
import nbformat as nbf
from provenance import fingerprint

ROOT=Path(__file__).resolve().parents[1]

SETUP='''from pathlib import Path
import os
import json
import re
import unicodedata
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Находим корень раздачи независимо от места запуска Jupyter.
ROOT = next(p for p in [Path.cwd(), *Path.cwd().parents]
            if (p / "data" / "requests.csv").exists())
DATA = ROOT / "data"
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
np.random.seed(42)
plt.rcParams.update({"font.family": "DejaVu Sans", "figure.figsize": (8, 4)})
print("Данные:", DATA)
'''

def md(text,teacher=None): return dict(kind='md',text=text,teacher_text=teacher)
def code(text): return dict(kind='code',text=text)
def task(title,prompt,starter,solution,check='',teacher_note=''):
    return dict(kind='task',title=title,prompt=prompt,starter=starter,solution=solution,check=check,teacher_note=teacher_note)

def load_spec(n):
    path=ROOT/'source'/'labs'/f'L{n:02}.py'
    spec=importlib.util.spec_from_file_location(f'lab{n}',path)
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module.SPEC

def build_lab(n, render=True):
    from build_notebooks import build
    build(n)
    if render:
        from build_documents import build as build_documents
        build_documents(n)

if __name__ == '__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--lesson',type=int,required=True)
    build_lab(ap.parse_args().lesson)
