"""Shared LibreOffice export for the current course."""
import os,shutil,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def libreoffice():
    override=os.environ.get('LIBREOFFICE_BIN')
    if override:
        if not Path(override).is_file(): raise FileNotFoundError('LIBREOFFICE_BIN does not point to a file')
        return override
    candidate=ROOT/'.tools'/'LibreOffice'/'SourceDir'/'LibreOffice'/'program'/'soffice.com'
    if candidate.exists(): return str(candidate)
    found=shutil.which('soffice')
    if found: return found
    raise RuntimeError('LibreOffice renderer not found')

def to_pdf(path: Path):
    profile=(ROOT/'.cache'/'lo_profile').as_uri()
    cmd=[libreoffice(),f'-env:UserInstallation={profile}','--headless','--convert-to','pdf','--outdir',str(path.parent),str(path)]
    p=subprocess.run(cmd,capture_output=True,timeout=150,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    if p.returncode or not path.with_suffix('.pdf').exists(): raise RuntimeError(p.stdout.decode(errors='replace')+p.stderr.decode(errors='replace'))

