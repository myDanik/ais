// Create the first three slides from the approved lecture and the complete storyboard.
const variables=await figma.variables.getLocalVariablesAsync();
const themeColors=[C.ink,C.bg,C.accent,C.source,C.pale,C.muted,C.line,C.bg];
const mutatedVariableIds=[];
variables.filter(v=>v.resolvedType==='COLOR').forEach((v,i)=>{for(const mode of Object.keys(v.valuesByMode))v.setValueForMode(mode,{...paint(themeColors[i%8]).color,a:1});mutatedVariableIds.push(v.id);});
const styles=await figma.getLocalTextStylesAsync();const mutatedStyleIds=[];
for(const st of styles){st.fontName=['Title','Header'].includes(st.name)?F.title:F.body;st.fontSize=({Title:112,Header:84,Subheader:60,Body:56,Caption:32})[st.name]||56;st.lineHeight={unit:'PERCENT',value:120};mutatedStyleIds.push(st.id);}
let s=addSlide(1);
const titleBlock=addLayout(s,'Титул',144,244,1632,'VERTICAL',44);
addText(titleBlock,'Название лекции','Как компьютер\nработает с текстом',1632,112,C.ink,F.title,'CENTER');
const divider=figma.createRectangle();titleBlock.appendChild(divider);createdNodeIds.push(divider.id);divider.name='Зелёная линия';divider.resize(1632,4);divider.fills=[paint(C.accent)];
addText(titleBlock,'Подзаголовок','Что сохранить, когда превращаешь\nсообщение в данные',1632,56,C.ink,F.body,'CENTER');

s=addSlide(2);
const input=addLayout(s,'Исходное обращение',144,404,800,'VERTICAL',28);
addText(input,'Подпись входа','Одно сообщение',800,40,C.muted);
addText(input,'Сообщение','«Я не могу войти\nв личный кабинет»',800,68);
const out=addLayout(s,'Разные результаты',1240,326,536,'VERTICAL',36);
const a=addLayout(out,'Отдел',0,0,536,'VERTICAL',8);addText(a,'Название задачи','Выбрать отдел',536,40,C.muted);addChip(a,'ИТ',132,60);
const b=addLayout(out,'Сведения',0,0,536,'VERTICAL',8);addText(b,'Название задачи','Извлечь сведения',536,40,C.muted);addText(b,'Фрагмент','личный кабинет',536,56,C.accent);
const c=addLayout(out,'Ответ',0,0,536,'VERTICAL',8);addText(c,'Название задачи','Подготовить ответ',536,40,C.muted);addText(c,'Уточнение','«Какой кабинет\nвы используете?»',536,52);
addArrow(s,'отдел',992,550,1185,398);addArrow(s,'сведения',992,550,1185,614);addArrow(s,'ответ',992,550,1185,819);

s=addSlide(3);
placeText(s,'Общее сообщение','«Не могу войти в личный кабинет»',144,304,1632,56,C.ink,F.body,'CENTER');
const grid=addLayout(s,'Четыре формы результата',144,470,1632,'VERTICAL',58);
const top=addLayout(grid,'Первая строка',0,0,1632,'HORIZONTAL',80);
const cls=addLayout(top,'Классификация',0,0,776,'VERTICAL',18);addText(cls,'Тип результата','Классификация',776,40,C.muted);addChip(cls,'ИТ',160,64);
const ext=addLayout(top,'Извлечение',0,0,776,'VERTICAL',18);addText(ext,'Тип результата','Извлечение',776,40,C.muted);const fragment=addText(ext,'Найденный фрагмент','личный кабинет',776,64,C.accent);addText(ext,'Тип фрагмента','сервис',776,34,C.muted);
const bottom=addLayout(grid,'Вторая строка',0,0,1632,'HORIZONTAL',80);
const search=addLayout(bottom,'Поиск',0,0,776,'VERTICAL',18);addText(search,'Тип результата','Поиск',776,40,C.muted);addText(search,'Первый результат','1  Восстановление доступа',776,52);addText(search,'Порядок','Выше остальных документов',776,34,C.muted);
const gen=addLayout(bottom,'Генерация',0,0,776,'VERTICAL',18);addText(gen,'Тип результата','Генерация',776,40,C.muted);addText(gen,'Новый ответ','«Что появляется при входе?»',776,52);
return {createdNodeIds,mutatedVariableIds,mutatedStyleIds,slides:builtSlides};
