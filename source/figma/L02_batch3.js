let s=addSlide(9);
placeText(s,'Определение softmax','p(c) = exp(s_c) / Σ exp(s_j)',144,284,1632,64,C.ink,F.body,'CENTER');
const probs=addLayout(s,'Вероятности двух классов',144,453,1632,'VERTICAL',60);
for(const [name,score,prob,w,col] of [['Библиотека','s = 1,5','89,1%',1016,C.accent],['ИТ','s = −0,6','10,9%',124,C.source]]){
 const b=addLayout(probs,'Вероятность '+name,0,0,1632,'VERTICAL',18);
 const caption=addLayout(b,'Класс и оценка',0,0,1632,'HORIZONTAL',42);addText(caption,'Класс',name,560,52,col);addText(caption,'Оценка',score,400,44,C.muted);addText(caption,'Вероятность',prob,588,64,col,F.bold,'RIGHT');
 const bar=figma.createRectangle();b.appendChild(bar);createdNodeIds.push(bar.id);bar.name='Вероятность '+prob;bar.resize(w,30);bar.fills=[paint(col)];
}
placeText(s,'Сумма вероятностей','0,891 + 0,109 = 1',144,870,1632,48,C.ink,F.body,'CENTER');

s=addSlide(10);
placeText(s,'Потеря примера','L = −ln(p_y)',600,280,720,70,C.ink,F.body,'CENTER');
placeText(s,'Ось потери: подпись','Потеря L',144,312,300,38,C.muted);
const x0=300,y0=846,pw=1360,ph=435;
polyline(s,'Ось вероятности',[[x0,y0],[x0+pw,y0]],C.muted,2);polyline(s,'Ось потери',[[x0,395],[x0,y0]],C.muted,2);
for(const p of [0,.5,1])placeText(s,'Отметка p='+p,p.toString().replace('.',','),x0+p*pw-35,y0+22,70,32,C.muted,F.body,'CENTER');
for(const loss of [1,2,3])placeText(s,'Отметка L='+loss,String(loss),204,y0-loss*ph/3-20,64,32,C.muted,F.body,'RIGHT');
const points=Array.from({length:96},(_,i)=>{const p=.05+i*.01;return [x0+p*pw,y0+Math.log(p)*ph/3];});
polyline(s,'График логарифмической потери',points,C.accent,5);
for(const p of [.1,.9]){const x=x0+p*pw,y=y0+Math.log(p)*ph/3;addRect(s,'Точка p='+p,x-7,y-7,14,14,C.accent);}
placeText(s,'Большая потеря','p_y = 0,1\nL ≈ 2,303',535,433,580,52,C.ink);
placeText(s,'Малая потеря','p_y = 0,9\nL ≈ 0,105',1250,656,450,52,C.ink);
placeText(s,'Что по оси x','Вероятность правильного класса p_y',144,916,1632,38,C.muted,F.body,'CENTER');

s=addSlide(11);
placeText(s,'Верная метка','Правильный класс — библиотека',144,290,1632,48,C.muted,F.body,'CENTER');
const changes=addLayout(s,'Изменение одного коэффициента',144,442,1632,'VERTICAL',50);
for(const [label,from,to] of [['Вес «книги»','2','2,1'],['Оценка','1,5','1,58'],['Вероятность','0,891','0,898']]){
 const rr=addLayout(changes,label,0,0,1632,'HORIZONTAL',60);addText(rr,'Показатель',label,590,56);addText(rr,'До',from,340,78,C.ink,F.body,'CENTER');addText(rr,'Стрелка','→',120,70,C.accent,F.body,'CENTER');addText(rr,'После',to,402,78,C.accent,F.body,'CENTER');
}
source(s,'Учебный шаг · изменён один вес; остальные параметры прежние');

s=addSlide(12);
placeText(s,'Критерий обучения','При обучении учитываем',144,302,1632,46,C.muted,F.body,'CENTER');
const objective=addLayout(s,'Слагаемые критерия',144,437,1632,'HORIZONTAL',70);
addText(objective,'Потеря','Логарифмическую\nпотерю на train',680,66,C.ink,F.body,'CENTER');
addText(objective,'Плюс','+',92,96,C.accent,F.body,'CENTER');
addText(objective,'Регуляризация','Штраф за большие\nкоэффициенты',720,66,C.ink,F.body,'CENTER');
const effect=addLayout(s,'Сила ограничения',220,745,1480,'HORIZONTAL',100);
addText(effect,'Меньше C','C ↓',290,104,C.accent,F.body,'CENTER');addText(effect,'Следствие','→',140,86,C.accent,F.body,'CENTER');addText(effect,'Больше регуляризация','Более сильная\nрегуляризация',850,64,C.ink);
source(s,'scikit-learn · LogisticRegression: C — обратная сила регуляризации');
return {createdNodeIds,slides:builtSlides};
