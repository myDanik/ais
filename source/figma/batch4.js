let s=addSlide(12);
placeText(s,'Один исходный текст','ИТ-поддержка: вход не работает!',144,306,1632,64,C.ink,F.body,'CENTER');
placeText(s,'Первый метод','split() · 4 токена',144,465,1632,40,C.muted);
const first=addLayout(s,'Четыре токена',144,537,1632,'HORIZONTAL',24);
['ИТ-поддержка:','вход','не','работает!'].forEach((v,i)=>addChip(first,v,[590,280,180,510][i],52));
placeText(s,'Второй метод',String.raw`\w+|[^\w\s] · 8 токенов`,144,702,1632,40,C.muted);
const second=addLayout(s,'Восемь токенов',144,773,1632,'HORIZONTAL',18);
['ИТ','-','поддержка',':','вход','не','работает','!'].forEach((v,i)=>addChip(second,v,[150,90,450,90,230,120,310,60][i],48));

s=addSlide(13);
placeText(s,'Адрес целиком','help@sever.example',144,333,1632,106,C.ink,F.body,'CENTER');
addArrow(s,'разбиение адреса',960,520,960,589);
const address=addLayout(s,'Пять элементов адреса',144,650,1632,'HORIZONTAL',40);
['help','@','sever','.','example'].forEach((v,i)=>addChip(address,v,[290,140,380,100,562][i],66));
placeText(s,'Вывод','Один адрес для человека — пять элементов для этого правила',144,853,1632,46,C.muted,F.body,'CENTER');

s=addSlide(14);
placeText(s,'Число вхождений','3 вхождения',144,302,1632,42,C.muted,F.body,'CENTER');
const occurrences=addLayout(s,'Вхождения',144,394,1632,'HORIZONTAL',126);
for(const v of ['книга','книга','журнал'])addChip(occurrences,v,460,76);
addArrow(s,'первая книга',374,551,544,682);addArrow(s,'вторая книга',960,551,656,682);addArrow(s,'журнал',1546,551,1340,682);
const types=addLayout(s,'Уникальные типы',330,731,1260,'HORIZONTAL',260);addChip(types,'книга',500,76);addChip(types,'журнал',500,76);
placeText(s,'Число типов','2 типа в словаре',144,902,1632,46,C.muted,F.body,'CENTER');

s=addSlide(15);
const before=addLayout(s,'До нормализации',144,337,1632,'VERTICAL',26);
addText(before,'Подпись','Исходная запись',1632,40,C.muted);
const raw=addText(before,'Пробелы до','··Не··отменяйте·запись!··',1632,80,C.ink,F.body,'CENTER');rich(raw,'Не');
addArrow(s,'сжатие пробелов',960,554,960,625);
const after=addLayout(s,'После нормализации',144,691,1632,'VERTICAL',26);
addText(after,'Подпись','После сжатия пробелов',1632,40,C.muted);
const normalized=addText(after,'Пробелы после','Не·отменяйте·запись!',1632,80,C.ink,F.body,'CENTER');rich(normalized,'Не');
placeText(s,'Обозначение','· обозначает пробел',144,925,1632,32,C.muted,F.body,'RIGHT');
return {createdNodeIds,slides:builtSlides};
