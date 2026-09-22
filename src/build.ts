import fs from 'node:fs/promises';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
import {theme as T,type Deck,type Slide} from './theme.js';
import {makeSlide,subtitle,text,line,rect,sourceCitation,expert,paperFigure,equationSvg,imagePlacement,questionSlide} from './components.js';
import {loadStoryboard} from './storyboard.js';
import {buildLecture5} from './lecture5.js';
import {buildLecture1} from './lecture1.js';
import {buildLecture2} from './lecture2.js';
import {buildLecture3} from './lecture3.js';
import {buildLecture4} from './lecture4.js';
import {buildLecture6} from './lecture6.js';
import {buildLecture7} from './lecture7.js';
import {buildLecture8} from './lecture8.js';

const args=process.argv.slice(2);const name=args.includes('--deck')?args[args.indexOf('--deck')+1]:'demo';
const root=process.cwd();
const python=path.join(root,'.venv/Scripts/python.exe');
function run(command:string,parameters:string[]) {
  const result=spawnSync(command,parameters,{cwd:root,stdio:'inherit',windowsHide:true});
  if(result.status!==0)throw new Error('Command failed: '+command);
}
if(args.includes('--input')){
 const input=args[args.indexOf('--input')+1];if(!input)throw new Error('Provide a storyboard path after --input');
 const deck=await loadStoryboard(input);
 await fs.mkdir(path.dirname(deck.output),{recursive:true});
 const objectFile=deck.output.replace(/\.pptx$/,'.objects.json');
 await fs.writeFile(objectFile,JSON.stringify(deck,null,2));
 run(process.execPath,['scripts/mcp_render.mjs',objectFile]);
 run(python,['-X','utf8','scripts/render_presentation.py',deck.output]);
 process.exit(0);
}
const courseBuilders:Record<string,()=>Promise<Deck>>={L01:buildLecture1,L02:buildLecture2,L03:buildLecture3,L04:buildLecture4,L05:buildLecture5,L06:buildLecture6,L07:buildLecture7,L08:buildLecture8};
if(courseBuilders[name]){
 const deck=await courseBuilders[name]();
 run(process.execPath,['scripts/mcp_render.mjs',`source/slides/${name}.json`]);
 run(python,['-X','utf8','scripts/render_presentation.py',deck.output]);
 process.exit(0);
}
if(name!=='demo')throw new Error('Use --input for a new storyboard, or --deck demo for the example');
await fs.mkdir('output',{recursive:true});
await fs.mkdir('papers',{recursive:true});
await fs.readFile('papers/demo_storyboard.json','utf8');
run(python,['-X','utf8','scripts/prepare_demo_assets.py']);
const slides:Slide[]=[];
let s=makeSlide('moe-intro','DEMO-S01','В обычном блоке Transformer все токены проходят через одну и ту же feed-forward сеть.',
  'Сравнить один общий FFN и набор экспертных FFN. Роутер выбирает путь для конкретного токена; названия E₁–E₄ не задают заранее предметную специализацию.',1,'Mixture of Experts');slides.push(s);
subtitle(s,'Для одного токена вычисляется часть экспертных сетей');
sourceCitation(s,'Shazeer et al., 2017','https://arxiv.org/abs/1701.06538');
rect(s,1.15,3.85,1.35,.76,'EAF2F7');text(s,'токен x',1.22,3.96,1.21,.48,{fontSize:25,align:'center'});
line(s,2.63,4.23,1.18,0,T.ink,1.8,true);rect(s,4.02,3.65,2.07,1.15,T.pale);text(s,'Роутер',4.15,3.93,1.81,.56,{align:'center'});
for(let i=0;i<4;i++){
 const y=2.83+i*.98;expert(s,`E${'₁₂₃₄'[i]}`,7.35,y,i<2,1.5,.68);
 line(s,6.17,4.23,1.00,y+.34-4.23,i<2?T.accent:'D1D6D4',i<2?2:1.1,true,i>=2);
 if(i<2)line(s,9.0,y+.34,1.12,4.23-(y+.34),T.accent,2,true);
}
text(s,'Σ',10.27,3.88,.55,.68,{fontFace:T.mathFont,fontSize:35,align:'center'});line(s,11.0,4.23,1.0,0,T.ink,1.8,true);
text(s,'y',12.08,3.87,.38,.65,{fontFace:T.mathFont,fontSize:35});
text(s,'Взвешенная\nсумма',9.65,5.0,2.65,.86,{fontSize:22,color:'555555',align:'center'});

s=makeSlide('moe-gates','DEMO-S02','Для top-2 оставим первых двух и перенормируем их веса по оставшейся сумме 0,8.',
  'На четырёх авторских вероятностях выбрать top-2. Разделить 0,55 и 0,25 на 0,8: веса 0,6875 и 0,3125. Эта нормировка относится к показанному примеру; не смешивать её с gate scaling Switch top-1.',2,'Роутер выбирает экспертов');slides.push(s);
subtitle(s,'Top-2: оставляем две оценки и делим их на 0,8');
for(let i=0;i<4;i++){
 const x=1.13+i*2.99;expert(s,`E${'₁₂₃₄'[i]}`,x,3.05,i<2,2.04,.7);
 text(s,['0,55','0,25','0,15','0,05'][i],x,4.03,2.04,.66,{fontSize:34,align:'center',color:i<2?T.accent:T.muted});
 if(i<2)text(s,['÷ 0,8 = 0,6875','÷ 0,8 = 0,3125'][i],x,4.85,2.04,.4,{fontSize:22,color:T.accent,align:'center'});
}
const equation=await equationSvg(String.raw`y = 0.6875\,E_1(x) + 0.3125\,E_2(x)`,'moe_top2');
await imagePlacement(s,equation,2.0,5.54,9.33,.83,'Взвешенная сумма выбранных экспертов');
sourceCitation(s,'Числа — учебный пример; идея sparse gating: Shazeer et al., 2017','https://arxiv.org/abs/1701.06538','bottom');

s=makeSlide('switch-figure','DEMO-S03','Switch Transformer использует маршрутизацию top-1: для каждого токена выбирается один эксперт.',
  'Слева собственная упрощённая схема места Switch FFN в блоке; справа увеличенный фрагмент Figure 2 из статьи, один токен. В исходной схеме gate probability также масштабирует выбранный выход.',3,'Switch Transformer: top-1');slides.push(s);
subtitle(s,'Каждый токен проходит через один выбранный FFN');
for(const [label,y,fill] of [['Self-attention',5.8,'F4F4F4'],['Add + Norm',4.8,'F4F4F4'],['Switch FFN',3.8,T.pale],['Add + Norm',2.8,'F4F4F4']] as const){
 rect(s,1.55,y,3.18,.68,fill);text(s,label,1.64,y+.07,3,.53,{fontSize:25,align:'center'});
 if(y>2.8)line(s,3.14,y-.11,0,-.22,T.ink,1.5,true);
}
line(s,3.14,6.72,0,-.13,T.ink,1.5,true);
for(const [from,to] of [[6.66,5.14],[4.66,3.14]]){
 line(s,3.14,from,-2.06,0,T.ink,1.25);
 line(s,1.08,from,0,to-from,T.ink,1.25);
 line(s,1.08,to,.33,0,T.ink,1.25,true);
}
line(s,4.92,4.14,1.55,0,T.accent,1.7,true);
await paperFigure(s,'assets/generated/switch_router_detail.png',[6.85,2.85,5.12,3.55],
  'Fedus, Zoph, Shazeer · JMLR 2022 · фрагмент рис. 2','https://jmlr.org/papers/v23/21-0998.html');

s=questionSlide('load-question','DEMO-S04','На рисунке сравним два распределения восьми токенов между четырьмя экспертами:',
  'Сначала предложить объяснить проблему распределения (8;0;0;0). Все токены выбирают E₁, остальные простаивают. Следующий слайд показывает сравнение с равномерной загрузкой.',4,'Достаточно ли добавить экспертов?');slides.push(s);
text(s,'Восемь токенов выбрали одного эксперта',1.06,2.33,11.2,.58,{fontSize:28});
for(let i=0;i<4;i++){
 const x=1.13+i*2.99;expert(s,`E${'₁₂₃₄'[i]}`,x,5.47,i===0,2.04,.73);
 if(i===0)for(let t=0;t<8;t++)rect(s,x+.31+(t%2)*.75,4.85-Math.floor(t/2)*.51,.65,.37,T.accent);
 else text(s,'0',x,4.57,2.04,.55,{fontSize:32,color:T.muted,align:'center'});
}

s=makeSlide('load-answer','DEMO-S05','В реальных MoE используются ограничения вместимости эксперта и методы балансировки загрузки.',
  'Сравнить два авторских распределения одних и тех же восьми токенов. Число экспертов одинаково, использование различается. Обсудить, зачем при обучении роутера учитывать загрузку.',5,'Балансировка загрузки');slides.push(s);
subtitle(s,'Одинаковое число экспертов — разные маршруты токенов');
await imagePlacement(s,'assets/generated/expert_load.png',1.07,2.82,11.15,3.65,'Учебное сравнение распределения восьми токенов между четырьмя экспертами');
sourceCitation(s,'Учебная иллюстрация. Методы балансировки: Fedus et al., 2022','https://jmlr.org/papers/v23/21-0998.html','bottom');

const deck:Deck={id:'moe-reference-demo',title:'Mixture of Experts',lecture:'papers/demo_lecture.md',output:'output/demo.pptx',slides};
await fs.writeFile('output/demo.objects.json',JSON.stringify(deck,null,2));
run(process.execPath,['scripts/mcp_render.mjs','output/demo.objects.json']);
run(python,['-X','utf8','scripts/render_presentation.py','output/demo.pptx']);
