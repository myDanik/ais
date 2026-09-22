import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const server=path.join(root,'.tools/mypoint-mcp');
if(!fs.existsSync(path.join(server,'src/index.ts')))throw new Error('Local MCP sources are missing from .tools/mypoint-mcp');
function run(cmd,args){const r=spawnSync(cmd,args,{cwd:root,stdio:'inherit',windowsHide:true});if(r.status!==0)throw new Error('MCP setup failed: '+(r.error?.message??r.status));}
if(!fs.existsSync(path.join(server,'node_modules/typescript/bin/tsc'))){
 const npm=path.join(path.dirname(process.execPath),'node_modules/npm/bin/npm-cli.js');
 if(!fs.existsSync(npm))throw new Error('Run npm ci --ignore-scripts --prefix .tools/mypoint-mcp, then retry this script');
 run(process.execPath,[npm,'ci','--ignore-scripts','--prefix',server]);
}
run(process.execPath,[path.join(server,'node_modules/typescript/bin/tsc'),'--project',path.join(server,'tsconfig.json'),'--outDir',path.join(server,'build')]);
process.stdout.write('Local MCP server is ready.\n');
