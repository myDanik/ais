let s=addSlide(4);
placeText(s,'Общее слово','ключ',144,302,1632,116,C.ink,F.title,'CENTER');
const left=addLayout(s,'Комната',144,523,720,'VERTICAL',24);
addText(left,'Контекст','от комнаты',720,72,C.ink,F.body,'CENTER');
const right=addLayout(s,'Сервис',1056,523,720,'VERTICAL',24);
addText(right,'Контекст','доступа к сервису',720,72,C.ink,F.body,'CENTER');
function icon(svg,parent,name,x,y,size){const node=figma.createNodeFromSvg(svg.replaceAll('currentColor',C.accent));parent.appendChild(node);node.rescale(size/node.width);node.name=name;node.x=x;node.y=y;createdNodeIds.push(node.id,...node.findAll(n=>true).map(n=>n.id));return node;}
icon(ICONS.door,s,'Комната · Lucide',416,693,176);icon(ICONS.key,s,'Доступ · Lucide',1328,693,176);
addArrow(s,'к комнате',845,461,590,517);addArrow(s,'к сервису',1075,461,1330,517);
placeText(s,'Источник иконок','Lucide · ISC',144,950,1632,26,C.source,F.body,'RIGHT');

s=addSlide(5);
const irony=addLayout(s,'Фраза с иронией',220,384,1480,'VERTICAL',44);
const q=addText(irony,'Цитата','«Отлично,\nпортал снова не работает»',1480,92);rich(q,'Отлично');rich(q,'не работает');
addText(irony,'Пояснение','Тон задаёт сочетание слов',1480,46,C.muted);

s=addSlide(6);
const sentences=addLayout(s,'Роли в предложениях',144,331,1632,'VERTICAL',52);
let a=addText(sentences,'Преподаватель действует','Преподаватель консультирует студента',1632,64);rich(a,'Преподаватель');rich(a,'студента',C.source);
let b=addText(sentences,'Студент действует','Студент консультирует преподавателя',1632,64);rich(b,'Студент');rich(b,'преподавателя',C.source);
addArrow(s,'к набору',960,591,960,650);
const bag=addLayout(s,'Общий набор',144,695,1632,'VERTICAL',24);
addText(bag,'Условие преобразования','Леммы без порядка',1632,42,C.muted,F.body,'CENTER');
const terms=addLayout(bag,'Один набор лемм',0,0,1632,'HORIZONTAL',32);
addChip(terms,'преподаватель',538,52);addChip(terms,'консультировать',610,52);addChip(terms,'студент',420,52);

s=addSlide(7);
const example=addLayout(s,'Одно обращение',144,366,810,'VERTICAL',34);
addText(example,'Сообщение','«Не открывается\nучебный портал»',810,72);
addChip(example,'ИТ',152,60);
const fields=addLayout(s,'Поля корпуса',1070,329,706,'VERTICAL',20);
for(const [field,meaning] of [['id','запись'],['text','сообщение'],['label','категория'],['group_id','исходная ситуация'],['split','часть выборки']]){
  const rr=addLayout(fields,'Поле '+field,0,0,706,'HORIZONTAL',36);
  addText(rr,'Имя поля',field,244,46,C.accent,F.bold);addText(rr,'Назначение',meaning,426,46);
}
return {createdNodeIds,slides:builtSlides};
