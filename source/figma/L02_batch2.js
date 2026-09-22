let s=addSlide(5);
placeText(s,'Счётчик внутри документа','В первом документе',144,320,770,46,C.muted);
const words=addLayout(s,'Два вхождения',144,451,770,'VERTICAL',26);
const pair=addLayout(words,'Повторы книги',0,0,770,'HORIZONTAL',24);addChip(pair,'книга',260,64);addChip(pair,'книга',260,64);
addText(words,'Третье слово','библиотека',770,56,C.muted);
placeText(s,'Частота','TF = 2',144,732,770,112,C.accent,F.title);
placeText(s,'Счётчик по коллекции','Во всей коллекции',1050,320,726,46,C.muted);
const docs=addLayout(s,'Документы с книгой',1050,433,726,'VERTICAL',22);
for(const [id,txt,col] of [['d1','книга книга библиотека',C.accent],['d2','книга продление',C.accent],['d3','общежитие оплата',C.muted]]){
 const rr=addLayout(docs,'Документ '+id,0,0,726,'HORIZONTAL',24);addText(rr,'Номер',id,76,44,C.muted);addText(rr,'Содержимое',txt,626,48,col);
}
placeText(s,'Число документов','DF = 2',1050,732,726,112,C.accent,F.title);
source(s,'Учебный пример · DF учитывает документ один раз');

s=addSlide(6);
placeText(s,'Размер коллекции','N = 3 документа',144,284,1632,44,C.muted,F.body,'CENTER');
placeText(s,'Формула IDF','IDF = 1 + ln((1 + N) / (1 + DF))',144,377,1632,74,C.ink,F.body,'CENTER');
const cases=addLayout(s,'Два значения IDF',144,580,1632,'HORIZONTAL',96);
for(const [term,df,value] of [['книга','DF = 2','1,2877'],['библиотека','DF = 1','1,6931']]){
 const b=addLayout(cases,'IDF: '+term,0,0,768,'VERTICAL',24);addText(b,'Слово',term,768,64,C.ink,F.body,'CENTER');addText(b,'DF',df,768,44,C.muted,F.body,'CENTER');addText(b,'IDF',value,768,104,C.accent,F.title,'CENTER');
}
source(s,'scikit-learn · сглаженный IDF; натуральный логарифм');

s=addSlide(7);
placeText(s,'Порядок координат','Координаты: библиотека, книга',144,289,1632,42,C.muted,F.body,'CENTER');
placeText(s,'До нормировки','(1,6931; 2,5754)',144,388,1632,104,C.ink,F.title,'CENTER');
addArrow(s,'L2-нормировка',960,551,960,623);placeText(s,'Делитель','÷ евклидова длина',1054,553,640,42,C.muted);
placeText(s,'После нормировки','(0,5494; 0,8356)',144,670,1632,104,C.accent,F.title,'CENTER');
placeText(s,'Проверка длины','0,5494² + 0,8356² ≈ 1',144,837,1632,48,C.ink,F.body,'CENTER');
source(s,'Сумма координат не обязана равняться 1');

s=addSlide(8);
placeText(s,'Признаки','x: книга = 0,8; пароль = 0,1',144,292,1632,56,C.ink,F.body,'CENTER');
placeText(s,'Условие расчёта','Коэффициенты заданы вручную · b = 0',144,385,1632,38,C.muted,F.body,'CENTER');
const scores=addLayout(s,'Оценки двух классов',144,540,1632,'VERTICAL',80);
for(const [cls,calc,col] of [['Библиотека','2 × 0,8 − 0,1 = 1,5',C.accent],['ИТ','−0,8 + 2 × 0,1 = −0,6',C.ink]]){
 const rr=addLayout(scores,'Оценка '+cls,0,0,1632,'HORIZONTAL',80);addText(rr,'Класс',cls,520,64,col);addText(rr,'Скалярное произведение',calc,1032,76,col);
}
source(s,'Учебный пример · s_c = w_cᵀx + b_c');
return {createdNodeIds,slides:builtSlides};
