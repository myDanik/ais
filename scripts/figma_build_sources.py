"""Generate inspectable Figma creation scripts from the lecture and storyboard."""
import argparse,json,math
from pathlib import Path
R=Path(__file__).resolve().parents[1];F=R/'source/figma'
ap=argparse.ArgumentParser();ap.add_argument('lesson');a=ap.parse_args();lid=a.lesson
m=json.loads((F/f'{lid}_content.json').read_text(encoding='utf8'));v=json.loads((F/f'{lid}_visuals.json').read_text(encoding='utf8'));assert len(m)==len(v)
helpers='\n'.join((F/n).read_text(encoding='utf8') for n in ['preamble.js','math_helpers.js','teaching_visuals.js'])
for start in range(0,len(m),4):
    end=min(start+4,len(m));subset={str(i):m[i] for i in range(start,end)}
    code=f'// Creation batch {start//4+1}; target canvas must be inspected before running this batch.\n'
    code+='const META='+json.dumps(subset,ensure_ascii=False)+';const builtSlides=[];\n'+helpers+'\n'
    code+='const VIS='+json.dumps(v[start:end],ensure_ascii=False)+';\n'
    code+=f'for(let i=0;i<VIS.length;i++)teachingSlide({start+1}+i,VIS[i]);\nreturn {{createdNodeIds,slides:builtSlides}};\n'
    (F/f'{lid}_batch{start//4+1}.js').write_text(code,encoding='utf8')
print(json.dumps({'lesson':lid,'slides':len(m),'batches':math.ceil(len(m)/4)}))
