import fs from 'node:fs/promises';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
import type {Deck} from './theme.js';
export async function buildLecture5():Promise<Deck>{
 const r=spawnSync(path.join(process.cwd(),'.venv/Scripts/python.exe'),['-X','utf8','scripts/figma_to_pptx_spec.py','--lesson','L05'],{cwd:process.cwd(),stdio:'inherit',windowsHide:true});
 if(r.status!==0)throw new Error('Figma snapshot conversion failed');
 return JSON.parse(await fs.readFile('source/slides/L05.json','utf8')) as Deck;
}
