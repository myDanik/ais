import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {Client} from '../.tools/mypoint-mcp/node_modules/@modelcontextprotocol/sdk/dist/esm/client/index.js';
import {StdioClientTransport} from '../.tools/mypoint-mcp/node_modules/@modelcontextprotocol/sdk/dist/esm/client/stdio.js';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const source=path.resolve(process.argv[2]);
const spec=JSON.parse(await fs.readFile(source,'utf8'));
const output=path.resolve(root,spec.output);
if(!output.startsWith(root+path.sep))throw new Error('Output must stay in the course workspace');
const lecture=await fs.readFile(path.resolve(root,spec.lecture),'utf8');
for(const s of spec.slides){
 if(!lecture.includes(s.anchor))throw new Error(`Missing lecture anchor: ${s.id}`);
 const marker=lecture.includes(`<!-- ${s.section} -->`)?`<!-- ${s.section} -->`:`## ${s.section}.`;
 if(!lecture.includes(marker)||!lecture.split(marker,2)[1].split('\n## ',1)[0].includes(s.anchor))throw new Error(`Anchor is outside its declared section: ${s.id}`);
}
await fs.mkdir(path.dirname(output),{recursive:true});
const qa=path.resolve(root,'qa',spec.id);
await fs.mkdir(qa,{recursive:true});
const client=new Client({name:'nlp-course-mcp-client',version:'2.0'});
const transport=new StdioClientTransport({command:process.execPath,args:[path.join(root,'.tools/mypoint-mcp/build/index.js')],cwd:root,stderr:'pipe'});
const log=[];
async function call(name,args) {
 const result=await client.callTool({name,arguments:args});
 log.push({name,arguments:args,result});
 if(result.isError||(result.content??[]).some(c=>c.type==='text'&&c.text.startsWith('❌')))throw new Error(JSON.stringify(result));
 return result;
}
try {
 await client.connect(transport);
 const catalog=await client.listTools();
 const allowed=new Set(catalog.tools.map(t=>t.name));
 await call('create_ppt',{title:spec.title,author:'Курс СИИ · NLP',subject:spec.title,layout:'LAYOUT_WIDE'});
 for(const slide of spec.slides){
  await call('create_slide',{background:slide.background??'FFFFFF'});
  for(const object of slide.objects){
   if(!allowed.has(object.tool))throw new Error('Unknown MCP tool '+object.tool);
   await call(object.tool,object.args);
  }
  await call('add_speaker_notes',{text:`${slide.section}\n${slide.notes}\nФрагмент лекции: ${slide.anchor}`});
 }
 await call('save_ppt',{filePath:output});
 const stat=await fs.stat(output);
 if(stat.size<10000)throw new Error('PPTX was not created');
 await fs.writeFile(path.join(qa,'mcp_calls.json'),JSON.stringify({source:spec.id,server:'lgwanai/mypoint-mcp + documented local extensions',transport:'stdio',slides:spec.slides.length,operations:log},null,2));
 console.log(JSON.stringify({output,slides:spec.slides.length,mcp_calls:log.length,bytes:stat.size}));
} finally {await client.close();}
