export const theme = {
  width: 13.333333, height: 7.5,
  background: 'FFFFFF', ink: '000000', accent: '1D9A78', source: '0070C0', muted: '898989',
  pale: 'E9F5F0', inactive: 'E4E7E7',
  headingFont: 'Prata', bodyFont: 'Calibri', mathFont: 'Cambria',
  titleSize: 44, bodySize: 28, labelSize: 23, sourceSize: 16,
  left: .917, right: 12.417,
  titleY: .70, titleH: .82, ruleY: 1.85, bodyY: 2.01,
  footerY: 7.03,
} as const;

export type ToolName = 'add_text'|'add_shape'|'add_chart'|'add_image';
export interface GraphicObject {tool:ToolName;args:Record<string,unknown>}
export interface Slide {
  id:string; section:string; anchor:string; notes:string; background:string; objects:GraphicObject[];title?:string;
}
export interface Deck {
  id:string; title:string; lecture:string; output:string; slides:Slide[];
}
