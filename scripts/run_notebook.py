import argparse,json,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
# The shared runner configures the local kernel directories and offline environment.
import run_notebooks
import nbformat
from nbclient import NotebookClient
from provenance import fingerprint
os.environ['NLP_MODELS_DIR']=str(ROOT/'.cache/models')
def run(number):
    lid=f'L{number:02}'
    path=ROOT/'dist/teacher'/lid/'solution.ipynb'
    nb=nbformat.read(path,as_version=4)
    client=NotebookClient(nb,timeout=420,kernel_name='python3',resources={'metadata':{'path':str(path.parent)}})
    client.execute()
    code=[c for c in nb.cells if c.cell_type=='code']
    assert all(c.execution_count is not None for c in code)
    assert not any(o.get('output_type')=='error' for c in code for o in c.get('outputs',[]))
    nb.metadata['execution_provenance']=fingerprint(ROOT,nb)
    nbformat.write(nb,path)
    q=ROOT/'qa'/lid;q.mkdir(parents=True,exist_ok=True)
    report={'lesson':lid,'status':'passed','executed_cells':len(code),'offline':True}
    (q/'execution.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report),flush=True)
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--lesson',type=int,required=True);args=ap.parse_args();run(args.lesson)
