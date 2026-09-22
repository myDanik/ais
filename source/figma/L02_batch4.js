let s=addSlide(13);
const baselines=addLayout(s,'Два состава выборки',144,352,1632,'HORIZONTAL',96);
for(const [label,value,rule] of [['Шесть равных классов','16,7%','Всегда одна категория'],['90% писем — ИТ','90%','Всегда ИТ']]){
 const b=addLayout(baselines,label,0,0,768,'VERTICAL',46);addText(b,'Распределение',label,768,48,C.muted,F.body,'CENTER');addText(b,'Accuracy',value,768,158,C.accent,F.title,'CENTER');addText(b,'Правило',rule,768,50,C.ink,F.body,'CENTER');
}
placeText(s,'Общее свойство','Обе стратегии обходятся без чтения текста',144,854,1632,52,C.ink,F.body,'CENTER');
source(s,'Учебные распределения · доля правильных ответов');

s=addSlide(14);
placeText(s,'Постоянный классификатор','Модель всегда отвечает A',144,282,1632,48,C.ink,F.body,'CENTER');
placeText(s,'Ось предсказаний','Предсказанный класс',850,385,760,42,C.muted,F.body,'CENTER');
placeText(s,'Ось истины','Истинный\nкласс',272,554,290,44,C.muted);
const cm=matrix(s,'Матрица ошибок',640,465,[210,440,440],[['','A','B'],['A',90,0],['B',10,0]],100,50);
placeText(s,'Точность','Accuracy = 90 / 100 = 0,9',144,862,950,56,C.ink);
placeText(s,'Пропуск B','B: найдено 0 из 10',1120,866,656,52,C.accent,F.body,'RIGHT');

s=addSlide(15);
placeText(s,'Для какого класса','Для A: TP = 90, FP = 10, FN = 0',144,292,1632,52,C.muted,F.body,'CENTER');
placeText(s,'Precision','Precision',144,406,768,76,C.ink,F.title,'CENTER');
placeText(s,'Recall','Recall',1008,406,768,76,C.ink,F.title,'CENTER');
fraction(s,'Precision A',264,538,340,'90','100',80);placeText(s,'Значение precision','= 0,9',658,600,300,76,C.accent);
fraction(s,'Recall A',1128,538,340,'90','90',80);placeText(s,'Значение recall','= 1',1520,600,256,76,C.accent);
placeText(s,'Знаменатель precision','Среди предсказанных A',144,834,768,46,C.muted,F.body,'CENTER');
placeText(s,'Знаменатель recall','Среди всех настоящих A',1008,834,768,46,C.muted,F.body,'CENTER');

s=addSlide(16);
placeText(s,'Определение F1','F1 = 2TP / (2TP + FP + FN)',144,291,1632,60,C.ink,F.body,'CENTER');
const f1=addLayout(s,'F1 каждого класса',144,445,1632,'HORIZONTAL',96);
for(const [label,value] of [['F1(A)','0,9474'],['F1(B)','0']]){
 const b=addLayout(f1,label,0,0,768,'VERTICAL',24);addText(b,'Класс',label,768,50,C.muted,F.body,'CENTER');addText(b,'F1',value,768,114,C.accent,F.title,'CENTER');
}
addArrow(s,'среднее A',600,660,878,709);addArrow(s,'среднее B',1350,660,1042,709);
placeText(s,'Усреднение','(0,9474 + 0) / 2 ≈ 0,4737',144,751,1632,82,C.ink,F.body,'CENTER');
placeText(s,'Другая метрика','У тех же ответов accuracy = 0,9',144,892,1632,48,C.muted,F.body,'CENTER');
return {createdNodeIds,slides:builtSlides};
