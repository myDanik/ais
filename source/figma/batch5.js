let s=addSlide(16);
const unicode=addLayout(s,'Две записи буквы',144,303,1632,'HORIZONTAL',192);
const composed=addLayout(unicode,'Одна позиция',0,0,720,'VERTICAL',18);addText(composed,'Буква','й',720,182,C.ink,F.title,'CENTER');addText(composed,'Кодовая позиция','U+0439',720,46,C.muted,F.body,'CENTER');
const decomposed=addLayout(unicode,'Две позиции',0,0,720,'VERTICAL',18);addText(decomposed,'Буква с комбинируемым знаком','и\u0306',720,182,C.ink,F.title,'CENTER');addText(decomposed,'Кодовые позиции','U+0438 + U+0306',720,46,C.muted,F.body,'CENTER');
addArrow(s,'NFC слева',504,665,873,740);addArrow(s,'NFC справа',1416,665,1047,740);
placeText(s,'Операция','NFC',144,741,1632,52,C.accent,F.bold,'CENTER');
placeText(s,'Общая запись','й',144,821,1632,106,C.ink,F.title,'CENTER');

s=addSlide(17);
const reviews=addLayout(s,'Два отзыва',144,327,1632,'VERTICAL',58);
addText(reviews,'Положительный отзыв','«Я доволен работой портала»',1632,68,C.ink,F.body,'CENTER');
const neg=addText(reviews,'Отрицательный отзыв','«Я не доволен работой портала»',1632,68,C.ink,F.body,'CENTER');rich(neg,'не');
addArrow(s,'потеря отрицания',960,594,960,656);
const same=addLayout(s,'Совпавшие строки',144,702,1632,'VERTICAL',30);addText(same,'Операция','Удалили «я» и «не»',1632,42,C.muted,F.body,'CENTER');addText(same,'Результат обоих отзывов','доволен работой портала',1632,76,C.accent,F.body,'CENTER');

s=addSlide(18);
const numbered=placeText(s,'Исходная ошибка','Ошибка 403',144,346,1632,136,C.ink,F.body,'CENTER');rich(numbered,'403');
placeText(s,'Операция','Удалили цифры',144,565,1632,42,C.muted,F.body,'CENTER');
addArrow(s,'потеря номера',960,653,960,723);
placeText(s,'Обобщённая ошибка','Ошибка',144,785,1632,136,C.ink,F.body,'CENTER');

s=addSlide(19);
placeText(s,'Определение f','f — сжатие пробелов',144,308,1632,42,C.muted,F.body,'CENTER');
placeText(s,'Идемпотентность','f(f(x)) = f(x)',144,430,1632,124,C.ink,F.title,'CENTER');
const stages=addLayout(s,'Два применения функции',144,703,1632,'HORIZONTAL',138);
for(const [name,value] of [['Вход','··Ошибка··403··'],['После f','Ошибка 403'],['После ещё одного f','Ошибка 403']]){
  const col=addLayout(stages,name,0,0,452,'VERTICAL',24);addText(col,'Этап',name,452,36,C.muted,F.body,'CENTER');addText(col,'Строка',value,452,52,C.ink,F.body,'CENTER');
}
addArrow(s,'первое применение',637,800,695,800);addArrow(s,'второе применение',1227,800,1285,800);
placeText(s,'Обозначение пробела','· обозначает пробел',144,930,1632,30,C.muted,F.body,'RIGHT');
return {createdNodeIds,slides:builtSlides};
