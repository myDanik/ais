import {spawnSync} from 'node:child_process';
import path from 'node:path';
const root=process.cwd();
function run(args){const r=spawnSync(process.execPath,args,{cwd:root,stdio:'inherit',windowsHide:true});if(r.status!==0)process.exit(r.status??1);}
run([path.join(root,'node_modules/typescript/bin/tsc'),'--noEmit','false','--outDir','.cache/slide-build']);
run([path.join(root,'.cache/slide-build/build.js'),...process.argv.slice(2)]);
