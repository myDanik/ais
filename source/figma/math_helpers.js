function source(s,label){return placeText(s,'Источник',label,144,950,1632,26,C.source,F.body,'RIGHT');}
function matrix(parent,name,x,y,widths,rows,size=52,headerSize=40){
 const w=widths.reduce((a,b)=>a+b,0),m=addLayout(parent,name,x,y,w,'VERTICAL',14);
 rows.forEach((cells,i)=>{const r=addLayout(m,name+' · строка '+i,0,0,w,'HORIZONTAL',0);cells.forEach((cell,j)=>addText(r,name+' · '+i+','+j,String(cell),widths[j],i===0?headerSize:size,i===0?C.muted:(cell===0||cell==='0'?C.muted:C.ink),i===0?F.body:F.body,'CENTER'));});
 return m;
}
function fraction(parent,name,x,y,w,num,den,size=72){
 const box=addLayout(parent,name,x,y,w,'VERTICAL',8);addText(box,name+' · числитель',num,w,size,C.ink,F.body,'CENTER');
 const ln=figma.createRectangle();box.appendChild(ln);createdNodeIds.push(ln.id);ln.name='Черта дроби';ln.resize(w,3);ln.fills=[paint(C.accent)];
 addText(box,name+' · знаменатель',den,w,size,C.ink,F.body,'CENTER');return box;
}
function polyline(parent,name,points,color=C.accent,weight=4){
 const minX=Math.min(...points.map(p=>p[0])),minY=Math.min(...points.map(p=>p[1]));
 const v=figma.createVector();parent.appendChild(v);createdNodeIds.push(v.id);v.name=name;
 v.vectorPaths=[{windingRule:'NONZERO',data:points.map((p,i)=>(i?'L':'M')+' '+(p[0]-minX)+' '+(p[1]-minY)).join(' ')}];
 v.fills=[];v.strokes=[paint(color)];v.strokeWeight=weight;v.strokeCap='ROUND';v.strokeJoin='ROUND';v.x=minX;v.y=minY;return v;
}
