"""Build the single current course from its canonical sources."""
import subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def run(*args):subprocess.run(args,cwd=ROOT,check=True)
for n in range(1,9):
    run(sys.executable,'-X','utf8','scripts/build_notebooks.py','--lesson',str(n))
    run(sys.executable,'-X','utf8','scripts/run_notebook.py','--lesson',str(n))
    run(sys.executable,'-X','utf8','scripts/build_documents.py','--lesson',str(n))
    run('node','scripts/build_cli.mjs','--deck',f'L{n:02}')
run(sys.executable,'-X','utf8','scripts/build_common.py')
run(sys.executable,'-X','utf8','scripts/package_course.py')
