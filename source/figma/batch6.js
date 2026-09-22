let s=addSlide(20);
const forms=addLayout(s,'Три словоформы',144,349,1632,'HORIZONTAL',141);
for(const form of ['книга','книги','книгой'])addChip(forms,form,450,76);
addArrow(s,'первая форма',369,537,860,662);addArrow(s,'вторая форма',960,537,960,662);addArrow(s,'третья форма',1551,537,1060,662);
placeText(s,'Преобразование','Лемматизация',144,707,1632,42,C.muted,F.body,'CENTER');
placeText(s,'Общая лемма','книга',144,802,1632,128,C.accent,F.title,'CENTER');

s=addSlide(21);
const contexts=addLayout(s,'Два окружения',144,340,1632,'HORIZONTAL',144);
const a=addLayout(contexts,'Материал',0,0,744,'VERTICAL',24);const ta=addText(a,'Контекст','образцы стали',744,68);rich(ta,'стали');
const b=addLayout(contexts,'Глагол',0,0,744,'VERTICAL',24);const tb=addText(b,'Контекст','студенты стали\nпроверять результаты',744,68);rich(tb,'стали');
addArrow(s,'к существительному',516,624,516,722);addArrow(s,'к глаголу',1404,624,1404,722);
placeText(s,'Лемма материала','сталь',144,789,744,112,C.ink,F.title,'CENTER');placeText(s,'Лемма глагола','стать',1032,789,744,112,C.ink,F.title,'CENTER');

s=addSlide(22);
const original=addLayout(s,'Оригинал',144,406,780,'VERTICAL',28);addText(original,'Поле исходного текста','text',780,42,C.muted);
addText(original,'Исходная строка','«  Не  отменяйте\nзапись!  »',780,66);
const normalized=addLayout(s,'Подготовленный текст',1100,330,676,'VERTICAL',22);addText(normalized,'Имя столбца','normalized',676,42,C.muted);addText(normalized,'Строка после обработки','Не отменяйте запись!',676,58,C.accent);
const toks=addLayout(s,'Токены',1100,687,676,'VERTICAL',22);addText(toks,'Имя столбца','tokens',676,42,C.muted);
const ts=addLayout(toks,'Список токенов',0,0,676,'HORIZONTAL',20);['Не','отменяйте','запись','!'].forEach((v,i)=>addChip(ts,v,[96,254,180,86][i],36));
addArrow(s,'нормализация',943,545,1055,433);addArrow(s,'токенизация',1438,531,1438,625);
placeText(s,'Сохранённая опора','Оригинал остаётся рядом с результатом обработки',144,902,1632,46,C.ink,F.body,'CENTER');

s=addSlide(23);
const final=addLayout(s,'Новый пример',144,347,1632,'VERTICAL',34);
addText(final,'Условие','Исходная строка с пробелами',1632,40,C.muted);
const q=addText(final,'Обращение','«  Не  отменяйте запись\nна 12 октября!  »',1632,94,C.ink,F.body,'CENTER');rich(q,'Не');rich(q,'12 октября',C.source);
const questions=addLayout(s,'Вопросы аудитории',144,802,1632,'HORIZONTAL',120);
addText(questions,'Первый вопрос','Что убираем?',680,64,C.ink,F.body,'CENTER');addText(questions,'Второй вопрос','Что должно остаться?',832,64,C.ink,F.body,'CENTER');
return {createdNodeIds,slides:builtSlides};
