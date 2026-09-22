"""Convert the exported Figma geometry to editable PowerPoint objects.

Figma remains the design source. This converter does not choose slide layouts.
The SVG snapshot preserves the actual line breaks, baselines, colours and paths.
"""
import argparse
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from PIL import ImageFont

ROOT = Path(__file__).resolve().parents[1]
SVG = '{http://www.w3.org/2000/svg}'
ET.register_namespace('', 'http://www.w3.org/2000/svg')
FONT_FILES = {
    ('Prata', False): ROOT/'assets/fonts/prata/Prata-Regular.ttf',
    ('Carlito', False): ROOT/'assets/fonts/carlito/Carlito-Regular.ttf',
    ('Carlito', True): ROOT/'assets/fonts/carlito/Carlito-Bold.ttf',
}
# With zero margins and explicit leading, PowerPoint's first baseline sits
# one font-size below the text box top. Verified against the rendered PDF.
FONT_BASELINE = {'Prata': 1.0, 'Carlito': 1.0}

def colour(value):
    return {'white':'FFFFFF', 'black':'000000'}.get(value, value.lstrip('#')).upper()

def transform_xy(node):
    t = node.get('transform','')
    if not t:
        return 0,0
    m = re.fullmatch(r'translate\(([-.\d]+)[ ,]+([-.\d]+)\)', t)
    if not m:
        raise ValueError('Unsupported transform: '+t)
    return tuple(map(float,m.groups()))

def object_spec(svg_file, slide_number, adjustments=None, lesson='L01'):
    tree = ET.parse(svg_file).getroot()
    scene = tree.find(SVG+'g')
    objects, spans = [], []
    for n in scene:
        kind=n.tag.removeprefix(SVG)
        if kind=='rect':
            dx,dy=transform_xy(n)
            args={'shapeType':'rect','x':(float(n.get('x',0))+dx)/144,'y':(float(n.get('y',0))+dy)/144,
                  'w':float(n.get('width'))/144,'h':float(n.get('height'))/144,
                  'options':{'fill':{'color':colour(n.get('fill'))},'line':{'transparency':100}}}
            objects.append({'tool':'add_shape','args':args})
        elif kind=='text':
            font=n.get('font-family');size=float(n.get('font-size'));bold=n.get('font-weight') in {'700','bold'}
            fontfile=FONT_FILES[(font,bold)]
            measure=ImageFont.truetype(str(fontfile),round(size*10))
            for t in n.findall(SVG+'tspan'):
                text=''.join(t.itertext()).rstrip('\n')
                if not text.strip():
                    continue
                x=float(t.get('x'));baseline=float(t.get('y'))
                width=measure.getlength(text)/10
                # Preserve the Figma baseline; allow a small width margin for
                # renderer rounding without fitting or shrinking any text.
                correction=(adjustments or {}).get(f'{slide_number}:{len(spans)}',0)
                y=baseline-size*FONT_BASELINE[font]+correction
                args={'text':text,'x':x/144,'y':y/144,'w':min(width+16,1920-x)/144,
                      'h':size*1.5/144,'fontFace':font,'fontSize':size/2,'bold':bold,
                      'color':colour(n.get('fill')),'margin':0,'valign':'top','align':'left',
                      'lineSpacing':size*.6,'charSpacing':0}
                objects.append({'tool':'add_text','args':args})
                spans.append({'text':text,'x':x,'baseline':baseline,'font':font,'size':size,'bold':bold,'width':width,
                              'object':len(objects)-1})
        elif kind=='path':
            data=n.get('d');letters=set(re.findall(r'[a-zA-Z]',data))
            if letters <= {'M','L','H','V','Z'}:
                tokens=re.findall(r'[MLHVZ]|-?\d*\.?\d+(?:[eE][-+]?\d+)?',data)
                at=0;point=None;start=None;command=None
                segments=[]
                while at<len(tokens):
                    if tokens[at].isalpha():
                        command=tokens[at];at+=1
                    if command=='Z':
                        segments.append((point,start));point=start;continue
                    count=1 if command in {'H','V'} else 2
                    nums=list(map(float,tokens[at:at+count]));at+=count
                    target=(nums[0],point[1]) if command=='H' else ((point[0],nums[0]) if command=='V' else tuple(nums))
                    if command=='M':start=target;command='L'
                    else:segments.append((point,target))
                    point=target
                for (x1,y1),(x2,y2) in segments:
                    thickness=float(n.get('stroke-width',1))
                    if abs(x2-x1)+abs(y2-y1)<thickness*.1:
                        objects.append({'tool':'add_shape','args':{'shapeType':'ellipse','x':(x1-thickness/2)/144,'y':(y1-thickness/2)/144,
                            'w':thickness/144,'h':thickness/144,'options':{'fill':{'color':colour(n.get('stroke'))},'line':{'transparency':100}}}})
                        continue
                    args={'shapeType':'line','x':min(x1,x2)/144,'y':min(y1,y2)/144,
                          'w':abs(x2-x1)/144,'h':abs(y2-y1)/144,
                          'flipH':x2<x1,'flipV':y2<y1,
                          'options':{'line':{'color':colour(n.get('stroke')),'width':float(n.get('stroke-width',1))/2,'beginArrowType':'none','endArrowType':'none'}}}
                    objects.append({'tool':'add_shape','args':args})
            else:
                # Curved Lucide artwork stays vector, separately selectable.
                # A full-slide viewBox retains the exported absolute geometry.
                doc=f'<svg xmlns="http://www.w3.org/2000/svg" width="1920" height="1080" viewBox="0 0 1920 1080" fill="none">{ET.tostring(n,encoding="unicode")}</svg>'
                path=ROOT/f'assets/figma/{lesson}'/f'slide-{slide_number:02}-path-{len(objects):02}.svg'
                path.parent.mkdir(parents=True,exist_ok=True);path.write_text(doc,encoding='utf-8')
                objects.append({'tool':'add_image','args':{'path':str(path),'x':0,'y':0,'w':1920/144,'h':7.5}})
        else:
            raise ValueError(f'Unsupported SVG element: {kind}')
    return objects,spans

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--lesson',default='L01');ap.add_argument('--output');ap.add_argument('--adjustments',type=Path)
    args=ap.parse_args()
    lid=args.lesson
    if not re.fullmatch(r'L\d{2}',lid):raise ValueError('Expected lesson id such as L02')
    args.output=args.output or f'dist/teacher/{lid}/presentation.pptx'
    metadata=json.loads((ROOT/f'source/figma/{lid}_content.json').read_text(encoding='utf-8'))
    file=json.loads((ROOT/f'source/figma/{lid}_file.json').read_text(encoding='utf-8'))
    adjustments=json.loads(args.adjustments.read_text(encoding='utf-8')) if args.adjustments else {}
    slides=[];geometry=[]
    for i,m in enumerate(metadata,1):
        objects,spans=object_spec(ROOT/f'assets/figma/{lid}/slide-{i:02}.svg',i,adjustments,lid)
        slides.append({'id':f'{lid}-{i:02}','title':m['title'],'section':m['section'],'anchor':m['anchor'],
                       'notes':'\n'.join('- '+v for v in m['notes']),'background':'FFFFFF','objects':objects,
                       'figmaNodeId':file['slides'][i-1]['id']})
        geometry.append(spans)
    spec={'id':lid,'title':metadata[0]['title'],'lecture':f'source/lectures/{lid}.md','output':args.output,
          'designSource':file['url'],'slides':slides}
    (ROOT/f'source/slides/{lid}.json').write_text(json.dumps(spec,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (ROOT/f'qa/{lid}/figma').mkdir(parents=True,exist_ok=True)
    (ROOT/f'qa/{lid}/figma/geometry.json').write_text(json.dumps(geometry,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'slides':len(slides),'native_text_objects':sum(len(s) for s in geometry),'output':args.output}))

if __name__=='__main__':main()
