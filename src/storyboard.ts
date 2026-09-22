import fs from 'node:fs/promises';
import type {Deck,GraphicObject} from './theme.js';
import {makeSlide,sectionSlide,questionSlide,subtitle,sourceCitation,paperFigure,equationSvg,imagePlacement} from './components.js';
interface StorySlide {
 id:string;section:string;anchor:string;notes:string;layout?:'section'|'question'|'figure'|'equation'|'custom';
 title:string;subtitle?:string;source?:{label:string;url?:string};figure?:string;tex?:string;objects?:GraphicObject[];
}
interface Story {id:string;title:string;lecture:string;output:string;slides:StorySlide[]}
export async function loadStoryboard(file:string):Promise<Deck> {
 const input=JSON.parse(await fs.readFile(file,'utf8')) as Story;
 if(!input.id||!input.lecture||!input.output||!input.slides?.length)throw new Error('Storyboard needs id, lecture, output and slides');
 const slides=[];
 for(const [i,item] of input.slides.entries()){
  const common=[item.id,item.section,item.anchor,item.notes,i+1] as const;
  const s=item.layout==='section'?sectionSlide(...common,item.title,item.subtitle??''):
    item.layout==='question'?questionSlide(...common,item.title):makeSlide(...common,item.title);
  if(item.subtitle&&item.layout!=='section')subtitle(s,item.subtitle);
  if(item.layout==='figure'){
   if(!item.figure||!item.source?.url)throw new Error('Paper figure requires its path and source URL');
   await paperFigure(s,item.figure,[1.0,2.85,11.3,3.8],item.source.label,item.source.url);
  } else if(item.layout==='equation'){
   if(!item.tex)throw new Error('Equation slide needs tex');
   const figure=await equationSvg(item.tex,`${input.id}-${item.id}`);
   await imagePlacement(s,figure,1.15,3.1,11.03,2.1,item.tex);
  }
  if(item.source&&item.layout!=='figure')sourceCitation(s,item.source.label,item.source.url);
  if(item.objects)s.objects.push(...item.objects);
  slides.push(s);
 }
 return {id:input.id,title:input.title,lecture:input.lecture,output:input.output,slides};
}
