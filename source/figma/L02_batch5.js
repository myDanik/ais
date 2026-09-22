let s=addSlide(17);
let a=placeText(s,'Первая словоформа','книга',144,358,768,116,C.ink,F.body,'CENTER');rich(a,'книг');
let b=placeText(s,'Вторая словоформа','книгу',1008,358,768,116,C.ink,F.body,'CENTER');rich(b,'книг');
addArrow(s,'общая часть слева',580,540,848,681);addArrow(s,'общая часть справа',1340,540,1072,681);
placeText(s,'Не полный словарь','Например',144,593,1632,44,C.muted,F.body,'CENTER');
const fragments=addLayout(s,'Примеры триграмм',648,726,624,'HORIZONTAL',24);addChip(fragments,'кни',300,74);addChip(fragments,'ниг',300,74);
placeText(s,'Настройка char_wb','char_wb · длины 3–5 · внутри границ слов',144,891,1632,46,C.ink,F.body,'CENTER');

s=addSlide(18);
placeText(s,'Критерий выбора','Macro-F1 на validation',144,288,1632,52,C.muted,F.body,'CENTER');
const compare=addLayout(s,'Два представления',144,410,1632,'HORIZONTAL',96);
for(const [label,details,value,col] of [['Слова','Униграммы и биграммы','0,4120',C.ink],['Символы','char_wb, длины 3–5','0,7430',C.accent]]){
 const block=addLayout(compare,label,0,0,768,'VERTICAL',30);addText(block,'Представление',label,768,70,col,F.body,'CENTER');addText(block,'Диапазон',details,768,42,C.muted,F.body,'CENTER');addText(block,'Macro-F1',value,768,126,col,F.title,'CENTER');
}
placeText(s,'Сопоставимость опыта','Одинаковый train и алгоритм · отдельное обучение',144,859,1632,48,C.ink,F.body,'CENTER');
source(s,'Выполненная лабораторная L02 · validation: 120 строк');

s=addSlide(19);
for(const [label,y,input,first,second] of [['Обучение',310,'Тексты train','fit','fit(X, y)'],['Применение',642,'Новые тексты','transform','predict']]){
 const block=addLayout(s,label,144,y,1632,'VERTICAL',28);addText(block,'Этап',label,1632,42,C.muted);
 const lane=addLayout(block,label+' · шаги',0,0,1632,'HORIZONTAL',108);
 const left=addLayout(lane,'Вход',0,0,440,'VERTICAL',18);addText(left,'Текст',input,440,58);addText(left,'Часть',label==='Обучение'?'train':'validation / test',440,40,C.muted);
 const middle=addLayout(lane,'Векторизатор',0,0,440,'VERTICAL',18);addText(middle,'Шаг','TF-IDF',440,62,C.accent);addText(middle,'Метод',first,440,46,C.muted);
 const right=addLayout(lane,'Классификатор',0,0,536,'VERTICAL',18);addText(right,'Шаг','Классификатор',536,58,C.accent);addText(right,'Метод',second,536,46,C.muted);
 addArrow(s,label+' · признаки',593,y+126,656,y+126);addArrow(s,label+' · решение',1141,y+126,1204,y+126);
}
source(s,'y — верные метки train · predict использует сохранённые словарь, IDF и веса');

s=addSlide(20);
const bad=addLayout(s,'Ошибочный порядок',144,305,1632,'VERTICAL',30);addText(bad,'Подпись','Ошибка: сначала обучили преобразователь на всех текстах',1632,46,C.muted);
const badrow=addLayout(bad,'Порядок с утечкой',0,0,1632,'HORIZONTAL',126);addText(badrow,'Корпус','Все тексты',460,68);addText(badrow,'Общий fit','fit TF-IDF',540,68);addText(badrow,'Поздний split','split',380,68);
addArrow(s,'общая векторизация',624,434,704,434);addArrow(s,'позднее разделение',1290,434,1370,434);
addText(bad,'Что раскрыто','Словарь и IDF уже учитывают test',1632,44,C.source);
const good=addLayout(s,'Порядок без утечки',144,678,1632,'VERTICAL',30);addText(good,'Подпись','Сначала отделяем проверочные ситуации',1632,46,C.muted);
const goodrow=addLayout(good,'Правильные шаги',0,0,1632,'HORIZONTAL',300);addText(goodrow,'Первый шаг','split по группам',666,68,C.ink);addText(goodrow,'Второй шаг','fit только на train',666,68,C.accent);
addArrow(s,'обучение после split',840,807,1070,807);
source(s,'Отложенные тексты проходят transform');
return {createdNodeIds,slides:builtSlides};
