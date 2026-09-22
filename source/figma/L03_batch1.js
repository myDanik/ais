if(figma.getSlideGrid().flat().length!==0)throw new Error("Unexpected existing slide count; inspect before continuing");
const META={"0": {"title": "Эмбеддинги и поиск", "section": "L03-S01", "anchor": "Классификатор может определить,", "notes": ["Категория уже известна, но для ответа нужна конкретная инструкция.", "Сегодня проследить представление, ранжирование и чтение найденного источника."]}, "1": {"title": "Пользователю нужен документ", "section": "L03-S01", "anchor": "Теперь результатом системы станет список документов,", "notes": ["Для продления книги нужен текст с условиями.", "Порядок результатов важен: документ о заселении не должен вытеснять нужную инструкцию.", "Далее векторизуем коллекцию."]}, "2": {"title": "Смысл распределён по вектору", "section": "L03-S02", "anchor": "После TF-IDF", "notes": ["В TF-IDF координаты привязаны к словарным признакам; у плотного вектора они обычно не имеют простых названий.", "Значения здесь схематические, не результаты кодирования."]}, "3": {"title": "Общее пространство векторов", "section": "L03-S02", "anchor": "Для поиска требуется общее пространство.", "notes": ["Одинаковая размерность двух векторов не гарантирует одинакового смысла координат.", "Показаны условные словарные оси, переставленные местами.", "Реальные энкодеры могут различаться сложнее."]}};const builtSlides=[];
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

function source(s,label){return placeText(s,'Источник',label,144,950,1632,26,C.source,F.body,'RIGHT');}
function matrix(parent,name,x,y,widths,rows,size=52,headerSize=40){
 const w=widths.reduce((a,b)=>a+b,0),m=addLayout(parent,name,x,y,w,'VERTICAL',14);
 rows.forEach((cells,i)=>{const r=addLayout(m,name+' · строка '+i,0,0,w,'HORIZONTAL',0);cells.forEach((cell,j)=>addText(r,name+' · '+i+','+j,String(cell),widths[j],i===0?headerSize:size,i===0?C.muted:(cell===0||cell==='0'?C.muted:C.ink),i===0?F.body:F.body,'CENTER'));});
 return m;
}
function fraction(parent,name,x,y,w,num,den,size=72){
 const box=addLayout(parent,name,x,y,w,'VERTICAL',8);addText(box,name+' · числитель',num,w,size,C.ink,F.body,'CENTER');
 const ln=figma.createRectangle();box.appendChild(ln);createdNodeIds.push(ln.id);ln.name='Черта дроби';ln.resize(w,3);ln.fills=[paint(C.accent)];
 addText(box,name+' · знаменатель',den,w,size,C.ink,F.body,'CENTER');return box;
}
function polyline(parent,name,points,color=C.accent,weight=4){
 const minX=Math.min(...points.map(p=>p[0])),minY=Math.min(...points.map(p=>p[1]));
 const v=figma.createVector();parent.appendChild(v);createdNodeIds.push(v.id);v.name=name;
 v.vectorPaths=[{windingRule:'NONZERO',data:points.map((p,i)=>(i?'L':'M')+' '+(p[0]-minX)+' '+(p[1]-minY)).join(' ')}];
 v.fills=[];v.strokes=[paint(color)];v.strokeWeight=weight;v.strokeCap='ROUND';v.strokeJoin='ROUND';v.x=minX;v.y=minY;return v;
}

// Native Figma layouts used across the remaining lectures; no slide screenshots.
function note(s,value){if(value)placeText(s,'Комментарий',value,144,892,1632,42,C.muted,F.body,'CENTER');}
function citation(s,value){if(value)placeText(s,'Источник',value,144,952,1632,26,C.source,F.body,'RIGHT');}
function stackText(parent,items,w,size=58,gap=24,color=C.ink){const b=addLayout(parent,'Текстовый блок',0,0,w,'VERTICAL',gap);for(const x of items)addText(b,'Строка',x,w,size,color);return b;}
function teachingSlide(n,v){
 const s=addSlide(n);
 if(v.kind==='cover'){
  const b=addLayout(s,'Титул',144,244,1632,'VERTICAL',44);addText(b,'Название лекции',v.title||META[n-1].title,1632,112,C.ink,F.title,'CENTER');
  const ln=figma.createRectangle();b.appendChild(ln);createdNodeIds.push(ln.id);ln.name='Зелёная линия';ln.resize(1632,4);ln.fills=[paint(C.accent)];addText(b,'Подзаголовок',v.subtitle,1632,56,C.ink,F.body,'CENTER');return s;
 }
 if(v.lead)placeText(s,'Постановка',v.lead,144,282,1632,46,C.muted,F.body,'CENTER');
 if(v.kind==='flow'){
  const count=v.items.length,gap=100,w=(1632-gap*(count-1))/count,y=v.y||440;
  const row=addLayout(s,'Последовательность',144,y,1632,'HORIZONTAL',gap);
  v.items.forEach((item,i)=>{const b=addLayout(row,'Этап '+i,0,0,w,'VERTICAL',28);addText(b,'Этап',item.text,w,v.size||60,i===count-1?C.accent:C.ink,F.body,'CENTER');if(item.sub)addText(b,'Пояснение',item.sub,w,38,C.muted,F.body,'CENTER');if(i<count-1)addArrow(s,'переход '+i,144+(i+1)*w+i*gap+18,y+45,144+(i+1)*(w+gap)-18,y+45);});
 }else if(v.kind==='compare'){
  const row=addLayout(s,'Сравнение',144,v.y||380,1632,'HORIZONTAL',96);
  v.items.forEach((item,i)=>{const b=addLayout(row,'Вариант '+i,0,0,768,'VERTICAL',30);addText(b,'Подпись',item.label,768,44,C.muted,F.body,'CENTER');if(item.big)addText(b,'Основной результат',item.big,768,item.bigSize||112,i?C.accent:C.ink,F.title,'CENTER');for(const text of item.lines||[])addText(b,'Пояснение',text,768,item.size||56,i?C.accent:C.ink,F.body,item.align||'CENTER');});
 }else if(v.kind==='stats'){
  const gap=80,w=(1632-gap*(v.items.length-1))/v.items.length,row=addLayout(s,'Показатели',144,v.y||399,1632,'HORIZONTAL',gap);
  v.items.forEach((item,i)=>{const b=addLayout(row,'Показатель '+i,0,0,w,'VERTICAL',30);addText(b,'Название',item.label,w,44,C.muted,F.body,'CENTER');addText(b,'Значение',item.value,w,v.size||124,C.accent,F.title,'CENTER');if(item.sub)addText(b,'Основание',item.sub,w,42,C.ink,F.body,'CENTER');});
 }else if(v.kind==='table'){
  const widths=v.widths||Array(v.headers.length).fill(1632/v.headers.length),rows=[v.headers,...v.rows];
  const m=matrix(s,'Таблица',144,v.y||382,widths,rows,v.size||50,v.headerSize||42);
  if(v.equation)placeText(s,'Расчёт',v.equation,144,798,1632,58,C.accent,F.body,'CENTER');
 }else if(v.kind==='equation'){
  if(v.before)placeText(s,'Условия',v.before,144,373,1632,58,C.ink,F.body,'CENTER');
  placeText(s,'Формула',v.formula,144,v.before?518:415,1632,v.size||86,C.accent,F.body,'CENTER');
  if(v.after)placeText(s,'Подстановка',v.after,144,706,1632,v.afterSize||58,C.ink,F.body,'CENTER');
 }else if(v.kind==='case'){
  const quote=placeText(s,'Пример',v.quote,144,v.y||340,1632,v.size||72);
  if(v.highlight)rich(quote,v.highlight);
  const row=addLayout(s,'Разбор примера',144,v.resultY||668,1632,'HORIZONTAL',96);
  for(const [i,item] of v.items.entries()){const b=addLayout(row,'Результат '+i,0,0,768,'VERTICAL',22);addText(b,'Подпись',item.label,768,42,C.muted);addText(b,'Вывод',item.text,768,item.size||62,i?C.accent:C.ink);}
 }else if(v.kind==='rank'){
  const row=addLayout(s,'Выдачи',144,391,1632,'HORIZONTAL',96);
  for(const list of v.lists){const b=addLayout(row,list.label,0,0,768,'VERTICAL',28);addText(b,'Метод',list.label,768,50,C.muted);for(const [i,item] of list.rows.entries())addText(b,'Позиция '+(i+1),(i+1)+'   '+item,768,58,item.includes(v.target||'###')?C.accent:C.ink);}
 }else if(v.kind==='bullets'){
  const b=addLayout(s,'Ключевые различия',144,364,1632,'VERTICAL',44);
  for(const [i,item] of v.items.entries()){const r=addLayout(b,'Различие '+i,0,0,1632,'HORIZONTAL',70);addText(r,'Ключ',item.label,440,54,C.accent,F.bold);addText(r,'Объяснение',item.text,1122,54);}
 }else if(v.kind==='vectors'){
  const ox=450,oy=823,k=310;
  polyline(s,'Ось X',[[ox,oy],[ox+500,oy]],C.line,2);polyline(s,'Ось Y',[[ox,oy],[ox,oy-490]],C.line,2);
  addArrow(s,'u',ox,oy,ox+k,oy);addArrow(s,'v',ox,oy,ox+k,oy-k,C.source);addArrow(s,'w',ox,oy,ox,oy-k,C.muted);
  placeText(s,'u','u = (1; 0)',778,850,270,42);placeText(s,'v','v = (1; 1)',782,451,290,42,C.source);placeText(s,'w','w = (0; 1)',147,447,286,42,C.muted);placeText(s,'Ноль','0',394,832,45,34,C.muted);
  const b=addLayout(s,'Косинусы',1160,445,616,'VERTICAL',50);addText(b,'Первый косинус','cos(u, v)\n≈ 0,7071',616,66,C.ink);addText(b,'Второй косинус','cos(u, w)\n= 0',616,66,C.ink);
 }else if(v.kind==='projection'){
  placeText(s,'Матрица X','X',194,370,600,54,C.muted,F.body,'CENTER');matrix(s,'Исходная матрица',194,465,[300,300],[[2,0],[0,1],[2,0]],88,88);
  addArrow(s,'проекция',900,645,1060,645);placeText(s,'Направление','V₁ = (1; 0)',846,397,274,48,C.muted,F.body,'CENTER');
  placeText(s,'Матрица Z','Z = XV₁',1160,370,616,54,C.muted,F.body,'CENTER');matrix(s,'Координата',1300,465,[300],[[2],[0],[2]],88,88);
 }else if(v.kind==='window'){
  const words=addLayout(s,'Окно контекста',144,375,1632,'HORIZONTAL',24);
  ['Студент','читает','новую','книгу'].forEach((x,i)=>addText(words,'Позиция '+i,x,390,70,i===1?C.accent:(i===3?C.muted:C.ink),i===1?F.bold:F.body,'CENTER'));
  addArrow(s,'левая пара',752,506,520,620);addArrow(s,'правая пара',830,506,1240,620);
  placeText(s,'Пара слева','читает → студент',144,689,768,60,C.ink,F.body,'CENTER');placeText(s,'Пара справа','читает → новую',1008,689,768,60,C.ink,F.body,'CENTER');
 }else{throw new Error('Unknown layout '+v.kind);}
 note(s,v.bottom);citation(s,v.source);return s;
}

const VIS=[{"kind": "cover", "title": "Эмбеддинги\nи поиск", "subtitle": "Как сравнивать тексты\nв общем пространстве"}, {"kind": "flow", "lead": "«Как продлить книгу?»", "items": [{"text": "Запрос"}, {"text": "Ранжирование"}, {"text": "Инструкция", "sub": "Срок и условия"}], "bottom": "Порядок документов влияет на полезность ответа"}, {"kind": "compare", "items": [{"label": "TF-IDF", "lines": ["Словарные признаки", "(0; x₂; 0; …)"], "size": 60}, {"label": "Плотный вектор", "lines": ["Распределённое представление", "(z₁; z₂; …; z_k)"], "size": 54}], "bottom": "Вектор может представлять слово, позицию или целый текст"}, {"kind": "compare", "lead": "Одинаковая размерность ещё не означает совместимость", "items": [{"label": "Словарь документов", "lines": ["книга → координата 1", "пароль → координата 2"], "size": 52}, {"label": "Другой словарь запроса", "lines": ["пароль → координата 1", "книга → координата 2"], "size": 52}], "bottom": "Для сравнения нужны согласованные преобразования", "source": "Условные словарные оси"}];
for(let i=0;i<VIS.length;i++)teachingSlide(1+i,VIS[i]);
return {createdNodeIds,slides:builtSlides};
