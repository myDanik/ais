import fs from 'node:fs/promises';
import {theme as T,type Slide,type Deck} from './theme.js';
import {makeSlide,text,line,rect,sectionSlide} from './components.js';

export class LectureDeck {
  slides:Slide[]=[];
  constructor(public id:string,public title:string,public lecture:string){}
  add(heading:string,section:number,anchor:string,notes:string):Slide{
    const n=this.slides.length+1;
    const s=makeSlide(`${this.id}-${String(n).padStart(2,'0')}`,`${this.id}-S${String(section).padStart(2,'0')}`,anchor,notes,n,heading);
    this.slides.push(s);return s;
  }
  cover(heading:string,subheading:string,anchor:string,notes:string):Slide{
    const s=sectionSlide(`${this.id}-01`,`${this.id}-S01`,anchor,notes,1,heading,subheading);
    s.title=heading;this.slides.push(s);return s;
  }
  async save():Promise<Deck>{
    try{
      const notes:Record<string,string>=JSON.parse(await fs.readFile(`source/slides/${this.id}_notes.json`,'utf8'));
      for(const s of this.slides)if(notes[s.id])s.notes=notes[s.id];
    }catch(e){if((e as NodeJS.ErrnoException).code!=='ENOENT')throw e;}
    const d:Deck={id:this.id,title:this.title,lecture:this.lecture,output:`dist/teacher/${this.id}/presentation.pptx`,slides:this.slides};
    await fs.mkdir('source/slides',{recursive:true});
    await fs.writeFile(`source/slides/${this.id}.json`,JSON.stringify(d,null,2));return d;
  }
}
export function label(s:Slide,v:string,x:number,y:number,w:number,size=27,color:string=T.ink,h=.6,align='left'){
 text(s,v,x,y,w,h,{fontSize:size,color,align});
}
export function quote(s:Slide,v:string,y=2.7,size=34){text(s,v,1.18,y,10.98,1.38,{fontSize:size,align:'center'});}
export function token(s:Slide,v:string,x:number,y:number,w:number,fill:string=T.pale,size=27){rect(s,x,y,w,.72,fill);text(s,v,x+.06,y+.07,w-.12,.57,{fontSize:size,align:'center'});}
export function arrow(s:Slide,x:number,y:number,w:number,h=0,color:string=T.accent){line(s,x,y,w,h,color,1.7,true);}
export function rule(s:Slide,y:number){line(s,1.03,y,11.24,0,'D9DEDC',.8);}
export function table(s:Slide,head:string[],rows:string[][],widths:number[],y=2.8,rowH=.7,size=25){
 let x=1.06;head.forEach((v,j)=>{label(s,v,x,y,widths[j]-.12,22,T.accent,.5);x+=widths[j];});
 rule(s,y+.58);
 rows.forEach((row,i)=>{x=1.06;row.forEach((v,j)=>{label(s,v,x,y+.78+i*rowH,widths[j]-.12,size,T.ink,rowH-.05);x+=widths[j];});});
}
export function matrix(s:Slide,rows:string[][],x:number,y:number,w:number,h:number,color:string=T.ink,size=30){
 line(s,x,y,0,h,color,1.4);line(s,x,y,.12,0,color,1.4);line(s,x,y+h,.12,0,color,1.4);
 line(s,x+w,y,0,h,color,1.4);line(s,x+w-.12,y,.12,0,color,1.4);line(s,x+w-.12,y+h,.12,0,color,1.4);
 rows.forEach((row,i)=>row.forEach((v,j)=>label(s,v,x+.15+j*(w-.3)/row.length,y+i*h/rows.length,(w-.3)/row.length,size,color,h/rows.length,'center')));
}
export function dot(s:Slide,x:number,y:number,r=.055,color:string=T.accent){s.objects.push({tool:'add_shape',args:{shapeType:'ellipse',x:x-r,y:y-r,w:r*2,h:r*2,fill:color,line:color,lineSize:0}});}
export function bar(s:Slide,value:number,max:number,x:number,y:number,w:number,caption:string,color:string=T.accent){
 rect(s,x,y,w*value/max,.44,color);label(s,caption,x,y-.61,w,24);label(s,String(value).replace('.',','),x+w*value/max+.16,y-.02,1.45,25,color,.49);
}
