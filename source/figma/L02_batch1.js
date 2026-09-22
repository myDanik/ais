let s=addSlide(1);
const titleBlock=addLayout(s,'Титул',144,244,1632,'VERTICAL',44);
addText(titleBlock,'Название лекции','Классификация\nтекста',1632,112,C.ink,F.title,'CENTER');
const divider=figma.createRectangle();titleBlock.appendChild(divider);createdNodeIds.push(divider.id);divider.name='Зелёная линия';divider.resize(1632,4);divider.fills=[paint(C.accent)];
addText(titleBlock,'Подзаголовок','От слов в сообщении\nк решению модели',1632,56,C.ink,F.body,'CENTER');

s=addSlide(2);
const training=addLayout(s,'Обучение',144,304,1632,'VERTICAL',38);
addText(training,'Этап','Обучение',1632,42,C.muted);
const tr=addLayout(training,'Что известно при обучении',0,0,1632,'HORIZONTAL',400);
addText(tr,'Данные','Тексты + верные метки',740,64);addText(tr,'Результат','Параметры\nмодели',492,64,C.accent);
addArrow(s,'обучение',932,433,1200,433);
const applying=addLayout(s,'Применение',144,654,1632,'VERTICAL',38);addText(applying,'Этап','Применение',1632,42,C.muted);
const pr=addLayout(applying,'Путь нового сообщения',0,0,1632,'HORIZONTAL',160);addText(pr,'Вход','Новый текст',500,64);addText(pr,'Модель','Модель',380,64);addText(pr,'Выход','Категория',432,64,C.accent);
addArrow(s,'новый текст',650,770,768,770);addArrow(s,'ответ',1190,770,1308,770);

s=addSlide(3);
placeText(s,'Единица разделения','Все варианты одного обращения остаются вместе',144,294,1632,48,C.ink,F.body,'CENTER');
const split=addLayout(s,'Части данных',144,424,1632,'HORIZONTAL',12);
for(const [name,groups,rows,w,col] of [['train','72','360 строк',964.8,C.accent],['validation','24','120 строк',321.6,C.source],['test','24','120 строк',321.6,C.muted]]){
 const block=addLayout(split,'Часть '+name,0,0,w,'VERTICAL',20);addText(block,'Группы',groups,w,132,col,F.title,'CENTER');
 const band=figma.createRectangle();block.appendChild(band);createdNodeIds.push(band.id);band.name='Доля '+name;band.resize(w,44);band.fills=[paint(col)];
 addText(block,'Назначение',name,w,46,C.ink,F.body,'CENTER');addText(block,'Строки',rows,w,40,C.muted,F.body,'CENTER');
}
placeText(s,'Общее число групп','120 групп · 600 строк',144,866,1632,44,C.ink,F.body,'CENTER');
source(s,'Учебный корпус · разделение по group_id');

s=addSlide(4);
const docs=addLayout(s,'Три документа',144,288,1632,'VERTICAL',10);
for(const [i,doc] of ['книга книга библиотека','книга продление','общежитие оплата'].entries()){
 const rr=addLayout(docs,'Документ '+(i+1),0,0,1632,'HORIZONTAL',30);addText(rr,'Номер','d'+(i+1),100,48,C.muted);addText(rr,'Текст',doc,1502,48);
}
matrix(s,'Счётчики слов',144,574,[142,298,298,298,298,298],[['','библиотека','книга','общежитие','оплата','продление'],['d1',1,2,0,0,0],['d2',0,1,0,0,1],['d3',0,0,1,1,0]],52,40);
source(s,'Учебный пример · строки — документы, столбцы — слова');
return {createdNodeIds,slides:builtSlides};
