"""Render the current course documents."""
import runpy
from pathlib import Path
if __name__ == '__main__':
    runpy.run_path(str(Path(__file__).with_name('build_common.py')),run_name='__main__')
