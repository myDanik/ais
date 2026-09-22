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
 }else if(v.kind==='qkv'){
  placeText(s,'Вход X','X',220,512,260,132,C.ink,F.body,'CENTER');placeText(s,'Размер X','N × d',144,700,412,46,C.muted,F.body,'CENTER');
  for(const [i,p] of [['Q','Запросы'],['K','Ключи'],['V','Значения']].entries()){
   const y=310+i*225,b=addLayout(s,'Проекция '+p[0],810,y,966,'VERTICAL',8);addText(b,'Формула проекции',p[0]+' = XW_'+p[0],966,76,C.accent);addText(b,'Роль проекции',p[1],966,44,C.muted);addArrow(s,'из X в '+p[0],484,590,754,y+44);
  }
 }else if(v.kind==='heat2'){
  for(let j=0;j<2;j++)placeText(s,'Ключ '+j,'Ключ '+(j+1),610+j*370,350,350,44,C.muted,F.body,'CENTER');
  const grid=addLayout(s,'Матрица весов',610,442,720,'VERTICAL',14);
  for(let i=0;i<2;i++){
   const rr=addLayout(grid,'Запрос '+i,0,0,720,'HORIZONTAL',20);placeText(s,'Подпись запроса '+i,'Запрос '+(i+1),210,477+i*143,320,48,C.muted);
   for(let j=0;j<2;j++){const value=v.data[i][j],z=Number(String(value).replace(',','.'));const rgb=[234,245,239].map((x,k)=>Math.round(x+z*([29,154,120][k]-x)));const hex='#'+rgb.map(x=>x.toString(16).padStart(2,'0')).join('');const cell=addLayout(rr,'Вес '+i+','+j,0,0,350,'VERTICAL',0);cell.paddingTop=26;cell.paddingBottom=26;cell.paddingLeft=26;cell.paddingRight=26;cell.fills=[paint(hex)];addText(cell,'Число',String(value),298,64,z>.85?C.bg:C.ink,F.body,'CENTER');}
  }
  if(v.after)placeText(s,'Результат маски',v.after,144,785,1632,64,C.accent,F.body,'CENTER');
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
