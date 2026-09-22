import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {Client} from '../.tools/mypoint-mcp/node_modules/@modelcontextprotocol/sdk/dist/esm/client/index.js';
import {StdioClientTransport} from '../.tools/mypoint-mcp/node_modules/@modelcontextprotocol/sdk/dist/esm/client/stdio.js';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const out=path.join(root,'qa/mcp');
await fs.mkdir(out,{recursive:true});
const client=new Client({name:'nlp-course-mcp-client',version:'2.0'});
const transport=new StdioClientTransport({command:process.execPath,args:[path.join(root,'.tools/mypoint-mcp/build/index.js')],cwd:root,stderr:'pipe'});
const log=[];
try {
 await client.connect(transport);
 const catalog=await client.listTools();
 await fs.writeFile(path.join(out,'tool_schemas.json'),JSON.stringify(catalog,null,2));
 for(const [name,args] of [
  ['create_ppt',{title:'MCP connection test',layout:'LAYOUT_WIDE'}],
  ['create_slide',{}],
  ['add_text',{text:'Текст → представление → модель',x:1,y:2.1,w:11.3,h:1.2,fontFace:'Arial',fontSize:36,color:'18181B',margin:0}],
  ['add_shape',{shapeType:'rect',x:1,y:3.7,w:2,h:.5,fill:'6D2E46',line:'6D2E46',lineSize:0}],
  ['add_speaker_notes',{text:'Проверка редактируемого текста, фигуры и заметок через MCP.'}],
  ['save_ppt',{filePath:path.join(out,'connection_test.pptx')}]
 ]) {
  const response=await client.callTool({name,arguments:args});
  log.push({name,arguments:args,response});
  if(response.isError)throw new Error(JSON.stringify(response));
 }
 const stat=await fs.stat(path.join(out,'connection_test.pptx'));
 await fs.writeFile(path.join(out,'probe.json'),JSON.stringify({transport:'stdio',server:'lgwanai/mypoint-mcp',revision:'94cba87b91782c9fbf53bda11ca1f50f8d9c34c3',tool_count:catalog.tools.length,bytes:stat.size,calls:log},null,2));
 console.log(JSON.stringify({success:true,tools:catalog.tools.map(t=>t.name),bytes:stat.size}));
} finally {await client.close();}
