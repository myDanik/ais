let s=addSlide(21);
placeText(s,'Выбранная модель','TF-IDF char_wb + логистическая регрессия',144,293,1632,50,C.muted,F.body,'CENTER');
const results=addLayout(s,'Качество на test',144,437,1632,'HORIZONTAL',96);
const count=addLayout(results,'Верные ответы',0,0,768,'VERTICAL',40);addText(count,'Подпись','Правильные ответы',768,48,C.ink,F.body,'CENTER');addText(count,'Счётчик','95 / 120',768,152,C.accent,F.title,'CENTER');addText(count,'Accuracy','Accuracy ≈ 0,792',768,48,C.muted,F.body,'CENTER');
const macro=addLayout(results,'Среднее по классам',0,0,768,'VERTICAL',40);addText(macro,'Подпись','Macro-F1',768,48,C.ink,F.body,'CENTER');addText(macro,'Метрика','0,765',768,152,C.accent,F.title,'CENTER');addText(macro,'Состав test','24 исходные ситуации',768,48,C.muted,F.body,'CENTER');
source(s,'Выполненная лабораторная L02 · выбранный вариант, отложенный test');

s=addSlide(22);
const quote=placeText(s,'Ошибочное обращение','«Не могу найти монографию\nв списке доступной литературы.»',144,351,1632,80);rich(quote,'монографию');
const compare=addLayout(s,'Правильный и полученный ответ',144,654,1632,'HORIZONTAL',96);
for(const [label,category,col] of [['Верная категория','Библиотека',C.ink],['Ответ модели','ИТ',C.accent]]){
 const b=addLayout(compare,label,0,0,768,'VERTICAL',24);addText(b,'Подпись',label,768,42,C.muted);addText(b,'Категория',category,768,76,col);
}
placeText(s,'Вопрос для разбора','Какие признаки могли повлиять на ответ?',144,868,1632,48,C.ink,F.body,'CENTER');
source(s,'Учебный корпус · точная строка из ошибок выбранной модели');

s=addSlide(23);
placeText(s,'Общая правильная метка','Верная категория — библиотека',144,280,1632,48,C.muted);
placeText(s,'Исходная просьба','«Мне нужна помощь в подборе\nисточников для курсовой.»',144,393,1100,58);
placeText(s,'Ответ без приветствия','ИТ',1390,419,386,76,C.accent);
addArrow(s,'первое предсказание',1250,452,1340,452);
const greeted=placeText(s,'Просьба с приветствием','«Здравствуйте! Мне нужна помощь\nв подборе источников для курсовой.»',144,655,1100,58);rich(greeted,'Здравствуйте!');
placeText(s,'Ответ с приветствием','Учебный\nпроцесс',1390,657,386,64,C.accent);
addArrow(s,'второе предсказание',1250,718,1340,718);
placeText(s,'Вопрос после опыта','Как проверить устойчивость к формулировке?',144,872,1632,46,C.ink,F.body,'CENTER');
source(s,'library-20 · все пять ошибочны: один ответ ИТ, четыре — учебный процесс');
return {createdNodeIds,slides:builtSlides};
