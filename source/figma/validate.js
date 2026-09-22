// Validate the current slides after layout has settled. Arrows intentionally connect regions.
const slides=await Promise.all(SLIDE_IDS.map(id=>figma.getNodeByIdAsync(id)));
const issues=[];const summary=[];
for(const slide of slides){
  const sb=slide.absoluteBoundingBox;
  const elements=slide.findAllWithCriteria({types:['TEXT','FRAME','VECTOR','RECTANGLE','ELLIPSE']});
  for(const n of elements){
    if(!n.visible)continue;
    const b=n.absoluteBoundingBox;if(!b)continue;
    if(b.x<sb.x-1||b.y<sb.y-1||b.x+b.width>sb.x+sb.width+1||b.y+b.height>sb.y+sb.height+1)issues.push({slide:slide.id,type:'outside',id:n.id,name:n.name,box:b});
    if(n.type==='TEXT'){
      const p=n.parent.absoluteBoundingBox;
      if(p&&(b.x<p.x-1||b.y<p.y-1||b.x+b.width>p.x+p.width+1||b.y+b.height>p.y+p.height+1))issues.push({slide:slide.id,type:'textOutsideParent',id:n.id,name:n.name});
      if(n.name==='Главная мысль'&&n.height>145)issues.push({slide:slide.id,type:'titleWrap',id:n.id,height:n.height});
    }
  }
  for(const parent of [slide,...elements.filter(n=>n.type==='FRAME')]){
    const cs=parent.children.filter(n=>n.visible&&n.type!=='VECTOR');
    for(let i=0;i<cs.length;i++)for(let j=i+1;j<cs.length;j++){
      const a=cs[i].absoluteBoundingBox,b=cs[j].absoluteBoundingBox;if(!a||!b)continue;
      const ox=Math.min(a.x+a.width,b.x+b.width)-Math.max(a.x,b.x),oy=Math.min(a.y+a.height,b.y+b.height)-Math.max(a.y,b.y);
      if(ox>4&&oy>4)issues.push({slide:slide.id,type:'siblingsOverlap',a:cs[i].id,b:cs[j].id,names:[cs[i].name,cs[j].name],ox,oy});
    }
  }
  summary.push({id:slide.id,name:slide.name,width:slide.width,height:slide.height,texts:elements.filter(n=>n.type==='TEXT').length});
}
return {clean:issues.length===0,issues,slides:summary};
