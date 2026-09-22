"""Extract exact slide rectangles from a native PDF export of the Figma grid."""
import argparse,json
from pathlib import Path
import pymupdf as fitz
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('lesson');a=ap.parse_args();q=R/f'qa/{a.lesson}/figma'
geometry=json.loads((q/'grid_bounds.json').read_text(encoding='utf8'));g=geometry['grid']
canvas=fitz.open(q/'figma_canvas.pdf');assert len(canvas)==1
sx=canvas[0].rect.width/g['width'];sy=canvas[0].rect.height/g['height'];assert abs(sx-sy)<1e-5
combined=fitz.open();images=[]
for i,s in enumerate(geometry['slides'],1):
 b=s['bounds'];clip=fitz.Rect((b['x']-g['x'])*sx,(b['y']-g['y'])*sy,(b['x']-g['x']+b['width'])*sx,(b['y']-g['y']+b['height'])*sy)
 assert canvas[0].rect.contains(clip)
 page=combined.new_page(width=b['width'],height=b['height']);page.show_pdf_page(page.rect,canvas,0,clip=clip)
 p=q/f'slide-{i:02}.png';page.get_pixmap(matrix=fitz.Matrix(.75,.75),alpha=False).save(p);images.append(p)
 separate=fitz.open();separate.insert_pdf(combined,from_page=i-1,to_page=i-1);separate.save(q/f'slide-{i:02}.pdf',garbage=4,deflate=True);separate.close()
combined.save(q/'presentation.pdf',garbage=4,deflate=True)
for start in range(0,len(images),6):
 sheet=Image.new('RGB',(1440,1350),'#dddddd');draw=ImageDraw.Draw(sheet)
 for j,p in enumerate(images[start:start+6]):
  im=Image.open(p);im.thumbnail((690,389));x=20+(j%2)*720;y=20+(j//2)*450;sheet.paste(im,(x,y));draw.text((x,y+402),str(start+j+1),fill='black')
 sheet.save(q/f'figma-contact-{start//6+1:02}.jpg',quality=94)
print(json.dumps({'lesson':a.lesson,'slides':len(images),'source':'native Figma grid PDF; exact slide bounds','scale':sx}))
