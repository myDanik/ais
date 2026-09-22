import fs from 'node:fs/promises';
import path from 'node:path';
import sharp from 'sharp';
import {Resvg} from '@resvg/resvg-js';
import {mathjax} from 'mathjax-full/js/mathjax.js';
import {TeX} from 'mathjax-full/js/input/tex.js';
import {SVG} from 'mathjax-full/js/output/svg.js';
import {liteAdaptor} from 'mathjax-full/js/adaptors/liteAdaptor.js';
import {RegisterHTMLHandler} from 'mathjax-full/js/handlers/html.js';
import {theme as T,type Slide} from './theme.js';

const adaptor=liteAdaptor();RegisterHTMLHandler(adaptor);
const math=mathjax.document('',{InputJax:new TeX(),OutputJax:new SVG({fontCache:'none'})});

export function text(s:Slide,value:unknown,x:number,y:number,w:number,h:number,options:Record<string,unknown>={}) {
  s.objects.push({tool:'add_text',args:{text:value,x,y,w,h,fontFace:T.bodyFont,fontSize:T.bodySize,color:T.ink,
    margin:0,valign:'middle',...options}});
}
export function line(s:Slide,x:number,y:number,w:number,h=0,color:string=T.accent,width=2,arrow=false,dash=false) {
  s.objects.push({tool:'add_shape',args:{shapeType:'line',x:w<0?x+w:x,y:h<0?y+h:y,w:Math.abs(w),h:Math.abs(h),
    flipH:w<0,flipV:h<0,options:{line:{color,width,endArrowType:arrow?'triangle':'none',dashType:dash?'dash':'solid'}}}});
}
export function rect(s:Slide,x:number,y:number,w:number,h:number,fill:string,options:Record<string,unknown>={}) {
  s.objects.push({tool:'add_shape',args:{shapeType:'rect',x,y,w,h,fill,line:fill,lineSize:0,options}});
}
export function title(s:Slide,value:string) {
  text(s,value,T.left,T.titleY,T.right-T.left,T.titleH,{fontFace:T.headingFont,fontSize:T.titleSize,align:'center'});
  line(s,T.left,T.ruleY,T.right-T.left,0,T.accent,2);
}
export function subtitle(s:Slide,value:string,options:Record<string,unknown>={}) {
  text(s,value,1.02,T.bodyY,11.29,.62,{fontSize:T.bodySize,...options});
}
export function sourceCitation(s:Slide,label:string,url?:string,where:'top'|'bottom'='top') {
  const value=url?[{text:label,options:{hyperlink:{url},color:T.source,underline:false}}]:label;
  text(s,value,.92,where==='top'?.09:6.75,11.53,.4,{fontSize:T.sourceSize,color:T.source,align:where==='top'?'right':'left'});
}
export function makeSlide(id:string,section:string,anchor:string,notes:string,index:number,heading?:string):Slide {
  const s:Slide={id,section,anchor,notes,background:T.background,objects:[],title:heading};
  if(heading)title(s,heading);
  text(s,'Системы искусственного интеллекта · NLP',3.85,T.footerY,5.65,.25,{fontSize:10,color:T.muted,align:'center'});
  text(s,String(index),12.0,T.footerY,.4,.25,{fontSize:10,color:T.muted,align:'right'});
  return s;
}
export function sectionSlide(id:string,section:string,anchor:string,notes:string,index:number,heading:string,subheading:string):Slide {
  const s=makeSlide(id,section,anchor,notes,index);
  text(s,heading,1.0,2.08,11.3,1.28,{fontFace:T.headingFont,fontSize:52,align:'center'});
  line(s,T.left,3.7,T.right-T.left,0,T.accent,2);
  text(s,subheading,1.25,4.22,10.83,1.2,{fontSize:30,align:'center'});
  return s;
}
export function questionSlide(id:string,section:string,anchor:string,notes:string,index:number,question:string):Slide {
  const s=makeSlide(id,section,anchor,notes,index);
  rect(s,T.left,.72,T.right-T.left,1.3,T.accent);
  text(s,question,1.18,.85,10.98,1.02,{fontFace:T.headingFont,fontSize:39,color:'FFFFFF',align:'center'});
  return s;
}
export async function imagePlacement(s:Slide,file:string,x:number,y:number,w:number,h:number,alt:string) {
  const meta=await sharp(file).metadata();
  if(!meta.width||!meta.height)throw new Error('Unknown image dimensions: '+file);
  const ratio=meta.width/meta.height;
  const width=Math.min(w,h*ratio),height=width/ratio;
  s.objects.push({tool:'add_image',args:{path:path.resolve(file),x:x+(w-width)/2,y:y+(h-height)/2,w:width,h:height}});
  s.notes+='\nИллюстрация: '+alt;
}
export async function paperFigure(s:Slide,file:string,box:[number,number,number,number],label:string,url:string) {
  await imagePlacement(s,file,...box,label);sourceCitation(s,label,url);
}
export async function equationSvg(tex:string,name:string):Promise<string> {
  const node=math.convert(tex,{display:true});
  let svg=adaptor.outerHTML(adaptor.firstChild(node) as Parameters<typeof adaptor.outerHTML>[0]);
  const box=svg.match(/viewBox="([^"]+)"/)?.[1].split(/\s+/).map(Number);
  if(!box||box.length!==4)throw new Error('MathJax did not return a viewBox');
  const width=1600,height=Math.ceil(width*box[3]/box[2]);
  svg=svg.replace(/width="[^"]+"/,`width="${width}px"`).replace(/height="[^"]+"/,`height="${height}px"`).replaceAll('currentColor','#000000');
  await fs.mkdir('assets/generated',{recursive:true});
  const file=path.resolve('assets/generated',name+'.svg');
  await fs.writeFile(file,svg);
  const png=new Resvg(svg).render().asPng();
  await sharp(png).png().toFile(file.replace(/\.svg$/,'.png'));
  await fs.writeFile(file.replace(/\.svg$/,'.tex'),tex+'\n');
  return file;
}
export function expert(s:Slide,label:string,x:number,y:number,active=true,w=1.75,h=.75) {
  rect(s,x,y,w,h,active?T.pale:'F2F3F3');
  text(s,label,x+.06,y+.08,w-.12,h-.16,{fontSize:24,color:active?T.ink:'8D9292',align:'center'});
}
