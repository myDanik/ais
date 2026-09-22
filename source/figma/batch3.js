let s=addSlide(8);
const counts=addLayout(s,'Число записей и ситуаций',144,333,1632,'HORIZONTAL',100);
const first=addLayout(counts,'Строки',0,0,666,'VERTICAL',0);addText(first,'Число строк','600',666,210,C.ink,F.title,'CENTER');addText(first,'Единица','строк в корпусе',666,52,C.muted,F.body,'CENTER');
const second=addLayout(counts,'Ситуации',0,0,866,'VERTICAL',0);addText(second,'Число ситуаций','120',866,210,C.accent,F.title,'CENTER');addText(second,'Единица','исходных ситуаций',866,52,C.muted,F.body,'CENTER');
const variants=addLayout(s,'Общее происхождение вариантов',144,770,1632,'VERTICAL',24);
addText(variants,'Связь счётчиков','Одна ситуация — пять формулировок',1632,48,C.ink,F.body,'CENTER');
const forms=addLayout(variants,'Пять вариантов',0,0,1632,'HORIZONTAL',18);
for(const word of ['Основа','Приветствие','Просьба','Благодарность','Консультация'])addChip(forms,word,312,38);

s=addSlide(9);
const audit=addLayout(s,'Строки аудита',144,354,1632,'VERTICAL',50);
for(const [label,message,verdict] of [['Пробел','«Не открывается учебный портал·»','ИТ'],['Пустота','«   »','Библиотека'],['Метка','«Когда можно продлить книгу?»','Общежитие']]){
  const rr=addLayout(audit,'Проверка: '+label,0,0,1632,'HORIZONTAL',30);
  addText(rr,'Тип дефекта',label,230,42,C.muted);
  const msg=addText(rr,'Текст записи',message,994,52);if(label==='Пробел')rich(msg,'·');
  addText(rr,'Категория',verdict,348,48,label==='Метка'?C.accent:C.ink);
}
placeText(s,'Обозначение пробела','· обозначает пробел',144,894,1632,32,C.muted,F.body,'RIGHT');

s=addSlide(10);
const payment=addLayout(s,'Обращение об оплате',144,335,1632,'VERTICAL',28);
const p=addText(payment,'Обращение','«Не могу оплатить общежитие\nчерез портал»',1632,72,C.ink,F.body,'CENTER');rich(p,'общежитие');rich(p,'портал',C.source);
const aspects=addLayout(s,'Два аспекта просьбы',144,673,1632,'HORIZONTAL',96);
const subject=addLayout(aspects,'Предмет',0,0,768,'VERTICAL',20);addText(subject,'Вопрос','О чём обращение?',768,40,C.muted);addText(subject,'Предмет','Оплата общежития',768,64,C.accent);
const cause=addLayout(aspects,'Причина',0,0,768,'VERTICAL',20);addText(cause,'Вопрос','Что именно мешает?',768,40,C.muted);addText(cause,'Уточнение','Сбой сайта?',768,64,C.source);

s=addSlide(11);
placeText(s,'Постановка','Одна категория на обращение',144,304,1632,42,C.muted);
const conflict=addLayout(s,'Конфликт двух записей',144,458,1632,'VERTICAL',62);
for(const category of ['Библиотека','Общежитие']){
  const rr=addLayout(conflict,'Запись: '+category,0,0,1632,'HORIZONTAL',52);
  addText(rr,'Одинаковый текст','«Когда можно продлить книгу?»',1090,58);
  addText(rr,'Разная категория',category,490,58,C.accent,F.bold);
}
placeText(s,'Нужное действие','Сверить сообщение и правила разметки',144,848,1632,52,C.ink,F.body,'CENTER');
return {createdNodeIds,slides:builtSlides};
