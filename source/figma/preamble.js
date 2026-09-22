// Shared preamble for Figma Slides. Parent first, then geometry; all text remains editable.
const C = {bg:'#FFFFFF',ink:'#161B18',accent:'#1D9A78',muted:'#65706A',source:'#0070C0',pale:'#EAF5EF',line:'#D9E3DD'};
const F = {title:{family:'Prata',style:'Regular'},body:{family:'Carlito',style:'Regular'},bold:{family:'Carlito',style:'Bold'}};
await Promise.all([F.title,F.body,F.bold,{family:'Inter',style:'Regular'}].map(f=>figma.loadFontAsync(f)));
const createdNodeIds=[];
function paint(hex){return {type:'SOLID',color:{r:parseInt(hex.slice(1,3),16)/255,g:parseInt(hex.slice(3,5),16)/255,b:parseInt(hex.slice(5,7),16)/255}};}
function addText(parent,name,value,width,size=56,color=C.ink,font=F.body,align='LEFT'){
  const t=figma.createText();parent.appendChild(t);createdNodeIds.push(t.id);
  t.name=name;t.fontName=font;t.fontSize=size;t.lineHeight={unit:'PERCENT',value:120};t.letterSpacing={unit:'PIXELS',value:0};
  t.characters=value;t.fills=[paint(color)];t.textAlignHorizontal=align;t.resize(width,1);t.textAutoResize='HEIGHT';
  return t;
}
function addRect(parent,name,x,y,w,h,color){
  const n=figma.createRectangle();parent.appendChild(n);createdNodeIds.push(n.id);
  n.name=name;n.resize(w,h);n.fills=[paint(color)];n.x=x;n.y=y;return n;
}
function addLayout(parent,name,x,y,w,direction='VERTICAL',gap=24){
  const f=figma.createAutoLayout(direction);parent.appendChild(f);createdNodeIds.push(f.id);
  f.name=name;f.fills=[];f.clipsContent=false;f.itemSpacing=gap;f.resize(w,1);
  f.primaryAxisSizingMode=direction==='VERTICAL'?'AUTO':'FIXED';
  f.counterAxisSizingMode=direction==='VERTICAL'?'FIXED':'AUTO';
  f.x=x;f.y=y;return f;
}
function placeText(parent,name,value,x,y,w,size=56,color=C.ink,font=F.body,align='LEFT'){
  const t=addText(parent,name,value,w,size,color,font,align);t.x=x;t.y=y;return t;
}
function addArrow(parent,name,x1,y1,x2,y2,color=C.accent){
  const dx=x2-x1,dy=y2-y1,len=Math.hypot(dx,dy),ux=dx/len,uy=dy/len;
  const ax=x2-ux*19+uy*9,ay=y2-uy*19-ux*9,bx=x2-ux*19-uy*9,by=y2-uy*19+ux*9;
  const minX=Math.min(x1,x2,ax,bx),minY=Math.min(y1,y2,ay,by);
  const v=figma.createVector();parent.appendChild(v);createdNodeIds.push(v.id);v.name='arrow · '+name;
  v.vectorPaths=[{windingRule:'NONZERO',data:`M ${x1-minX} ${y1-minY} L ${x2-minX} ${y2-minY} M ${ax-minX} ${ay-minY} L ${x2-minX} ${y2-minY} L ${bx-minX} ${by-minY}`}];
  v.fills=[];v.strokes=[paint(color)];v.strokeWeight=3;v.strokeCap='ROUND';v.strokeJoin='ROUND';v.x=minX;v.y=minY;return v;
}
function addChip(parent,value,w,size=54,color=C.accent){
  const f=figma.createAutoLayout('VERTICAL');parent.appendChild(f);createdNodeIds.push(f.id);f.name='Токен · '+value;
  f.fills=[paint(C.pale)];f.paddingLeft=18;f.paddingRight=18;f.paddingTop=10;f.paddingBottom=10;
  f.resize(w,1);f.primaryAxisSizingMode='AUTO';f.counterAxisSizingMode='FIXED';f.clipsContent=false;
  addText(f,'Текст токена',value,w-36,size,color,F.body,'CENTER');return f;
}
function addFooter(s,n){
  const footer=addLayout(s,'Нижняя подпись',144,1005,1632,'HORIZONTAL',24);
  addText(footer,'Курс','Системы искусственного интеллекта · NLP',1460,22,C.muted,F.body);
  addText(footer,'Номер',String(n),148,22,C.muted,F.body,'RIGHT');
}
function addSlide(n){
  const m=META[n-1];const s=figma.createSlide();createdNodeIds.push(s.id);s.name=String(n).padStart(2,'0')+' · '+m.title;
  s.fills=[paint(C.bg)];s.speakerNotes=m.notes.map(v=>'- '+v).join('\n')+'\n\n'+m.section+' · Фрагмент лекции: '+m.anchor;
  if(n!==1){
    const head=addLayout(s,'Заголовок',144,86,1632,'VERTICAL',26);
    const t=addText(head,'Главная мысль',m.title,1632,84,C.ink,F.title,'CENTER');
    const rule=figma.createRectangle();head.appendChild(rule);createdNodeIds.push(rule.id);rule.name='Зелёная линия';rule.resize(1632,4);rule.fills=[paint(C.accent)];
  }
  addFooter(s,n);builtSlides.push({number:n,id:s.id,title:m.title});return s;
}
function rich(t,word,color=C.accent,font=F.bold){
  const at=t.characters.indexOf(word);if(at<0)throw new Error('Missing highlight: '+word);
  t.setRangeFills(at,at+word.length,[paint(color)]);t.setRangeFontName(at,at+word.length,font);return t;
}
function row(parent,name,y,cells,widths,size=50){
  const r=addLayout(parent,name,0,y,widths.reduce((a,b)=>a+b,0)+32*(widths.length-1),'HORIZONTAL',32);
  cells.forEach((v,i)=>addText(r,name+' · '+i,v,widths[i],size,i===0?C.muted:C.ink));return r;
}
