"""Build the revised teaching narrative around the verified computational exercises."""
import argparse,json,re,sys
from pathlib import Path
import nbformat as nbf
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from build_labs import load_spec,SETUP
from provenance import fingerprint

def build(number):
    lid=f'L{number:02}'
    prose=json.loads((ROOT/'source/labs'/f'{lid}.json').read_text(encoding='utf-8'))
    original=load_spec(number)
    for audience in ['student','teacher']:
        out=ROOT/'dist'/audience/lid;out.mkdir(parents=True,exist_ok=True)
        cells=[nbf.v4.new_markdown_cell(f'# {prose["title"]}\n\n{prose["intro"]}')]
        cells.append(nbf.v4.new_code_cell(SETUP.replace('print("Данные:", DATA)\n','')))
        ti=0;mi=0;ci=0
        for item in original['cells']:
            kind=item['kind']
            if kind=='md':
                text=prose['markdown'][mi]
                if audience=='teacher' and mi==len(prose['markdown'])-1:text=prose['teacher_ending']
                cells.append(nbf.v4.new_markdown_cell(text));mi+=1
            elif kind=='code':
                if str(ci) in prose.get('before_code',{}):cells.append(nbf.v4.new_markdown_cell(prose['before_code'][str(ci)]))
                cells.append(nbf.v4.new_code_cell(prose.get('code_overrides',{}).get(str(ci),item['text'])))
                ci+=1
            elif kind=='task':
                for demo in prose.get('before_task',{}).get(str(ti),[]):
                    cells.append(nbf.v4.new_code_cell(demo['text']) if demo['kind']=='code' else nbf.v4.new_markdown_cell(demo['text']))
                narrative=prose['tasks'][ti];ti+=1
                cells.append(nbf.v4.new_markdown_cell('## '+narrative['title']+'\n\n'+narrative['prompt']))
                content=(prose.get('solution_overrides',{}).get(str(ti-1),item['solution']) if audience=='teacher'
                         else prose.get('starter_overrides',{}).get(str(ti-1),item['starter']))
                if audience=='student':content=re.sub(r'# TODO[^\n]*','# Ваш код',content)
                cells.append(nbf.v4.new_code_cell(content,metadata={'tags':['solution' if audience=='teacher' else 'exercise']}))
                check=prose.get('check_overrides',{}).get(str(ti-1),item['check'])
                if check:cells.append(nbf.v4.new_code_cell(check,metadata={'tags':['public-check']}))
                if audience=='teacher' and narrative.get('teacher_note'):
                    cells.append(nbf.v4.new_markdown_cell(narrative['teacher_note']))
        assert ti==len(prose['tasks']) and mi==len(prose['markdown'])
        nb=nbf.v4.new_notebook(cells=cells,metadata={'kernelspec':{'display_name':'Python 3 (NLP)','language':'python','name':'python3'},'language_info':{'name':'python','version':'3.13'}})
        path=out/('solution.ipynb' if audience=='teacher' else 'lab.ipynb')
        if audience=='teacher' and path.exists():
            previous=nbf.read(path,as_version=4)
            if previous.metadata.get('execution_provenance')==fingerprint(ROOT,nb):
                before=[c for c in previous.cells if c.cell_type=='code']
                after=[c for c in nb.cells if c.cell_type=='code']
                for a,b in zip(before,after):b.outputs=a.get('outputs',[]);b.execution_count=a.execution_count
                nb.metadata['execution_provenance']=previous.metadata['execution_provenance']
        nbf.write(nb,path)
        print(path,flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--lesson',type=int,required=True);args=ap.parse_args();build(args.lesson)
