"""Run the document skill's renderer using this course's portable Windows tools."""
import argparse,os,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('docx',type=Path);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
renderer=Path('C:/Users/ruslanzalikov/.codex/plugins/cache/openai-primary-runtime/documents/26.909.12148/skills/documents/render_docx.py')
lo=R/'.tools/LibreOffice/SourceDir/LibreOffice/program'
poppler=next((R/'.tools/poppler').glob('*/Library/bin'))
env=os.environ.copy();env['PATH']=os.pathsep.join([str(lo),str(poppler),env.get('PATH','')])
subprocess.run([sys.executable,str(renderer),str(a.docx.resolve()),'--output_dir',str(a.out.resolve()),'--emit_pdf','--width','1300','--height','1700'],env=env,check=True,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
