import fs from 'node:fs/promises';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
import type {Deck} from './theme.js';

/** The Figma file is the design source; SVG retains the reviewed geometry. */
export async function buildLecture2():Promise<Deck>{
 const root=process.cwd();
 const result=spawnSync(path.join(root,'.venv/Scripts/python.exe'),[
  '-X','utf8','scripts/figma_to_pptx_spec.py','--lesson','L02'
 ],{cwd:root,stdio:'inherit',windowsHide:true});
 if(result.status!==0)throw new Error('Figma snapshot conversion failed');
 return JSON.parse(await fs.readFile('source/slides/L02.json','utf8')) as Deck;
}
