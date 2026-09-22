import fs from 'node:fs/promises';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
import type {Deck} from './theme.js';

/** L01 is designed in Figma. Rebuild from its reviewed SVG snapshot. */
export async function buildLecture1():Promise<Deck>{
 const root=process.cwd();
 const result=spawnSync(path.join(root,'.venv/Scripts/python.exe'),[
  '-X','utf8','scripts/figma_to_pptx_spec.py','--output','dist/teacher/L01/presentation.pptx'
 ],{cwd:root,stdio:'inherit',windowsHide:true});
 if(result.status!==0)throw new Error('Figma snapshot conversion failed');
 return JSON.parse(await fs.readFile('source/slides/L01.json','utf8')) as Deck;
}
