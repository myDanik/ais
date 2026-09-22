#!/usr/bin/env node

import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { StreamableHTTPServerTransport } from '@modelcontextprotocol/sdk/server/streamableHttp.js';
import { isInitializeRequest } from '@modelcontextprotocol/sdk/types.js';
import { randomUUID } from 'node:crypto';
import { z } from 'zod';
import PptxGenJS from 'pptxgenjs';
import * as fs from 'fs';
import * as path from 'path';
import express, { Request, Response, NextFunction } from 'express';

// 颜色名称到十六进制的映射
const COLOR_MAP: { [key: string]: string } = {
  'black': '000000',
  'white': 'FFFFFF',
  'red': 'FF0000',
  'green': '00FF00',
  'blue': '0000FF',
  'yellow': 'FFFF00',
  'cyan': '00FFFF',
  'magenta': 'FF00FF',
  'gray': '808080',
  'grey': '808080',
  'darkgray': '404040',
  'darkgrey': '404040',
  'lightgray': 'C0C0C0',
  'lightgrey': 'C0C0C0',
  'orange': 'FFA500',
  'purple': '800080',
  'brown': 'A52A2A',
  'pink': 'FFC0CB'
};

// 颜色转换函数
function convertColor(color: string | undefined): string | undefined {
  if (!color) return undefined;
  
  // 如果已经是十六进制格式（6位数字/字母），直接返回
  if (/^[0-9A-Fa-f]{6}$/.test(color)) {
    return color.toUpperCase();
  }
  
  // 如果是#开头的十六进制，去掉#
  if (/^#[0-9A-Fa-f]{6}$/.test(color)) {
    return color.substring(1).toUpperCase();
  }
  
  // 转换颜色名称
  const lowerColor = color.toLowerCase();
  return COLOR_MAP[lowerColor] || color;
}

// PPT 会话类会话状态管理
class PptSession {
  private ppt: PptxGenJS | null = null;
  private currentSlide: any = null;
  private filePath: string | null = null;

  // 创建新的 PPT
  createPpt(options: any = {}): void {
    this.ppt = new PptxGenJS();
    this.currentSlide = null;
    this.filePath = null;

    // 设置元数据属性
    if (options.title) this.ppt.title = options.title;
    if (options.author) this.ppt.author = options.author;
    if (options.subject) this.ppt.subject = options.subject;
    if (options.company) this.ppt.company = options.company;
    if (options.revision) this.ppt.revision = options.revision;

    // 设置布局
    if (options.customLayout) {
      this.ppt.defineLayout(options.customLayout);
      this.ppt.layout = options.customLayout.name;
    } else if (options.layout) {
      this.ppt.layout = options.layout;
    }

    // 设置 RTL 模式
    if (options.rtlMode !== undefined) {
      this.ppt.rtlMode = options.rtlMode;
    }
  }

  // 创建幻灯片
  createSlide(options: any = {}): void {
    if (!this.ppt) {
      throw new Error('请先创建 PPT');
    }
    const { background, ...slideOptions } = options;
    this.currentSlide = this.ppt.addSlide(slideOptions);
    if (background) this.currentSlide.background = { color: convertColor(background) };
  }

  addNotes(text: string): void {
    if (!this.currentSlide) throw new Error('Create a slide first');
    this.currentSlide.addNotes(text);
  }

  // 添加幻灯片
  addSlide(options: any = {}): void {
    this.createSlide(options);
  }

  // 添加文本
  addText(text: any, options: any = {}): void {
    if (!this.currentSlide) {
      throw new Error('请先创建幻灯片');
    }
    
    // 转换颜色格式
    const processedOptions = { ...options };
    if (processedOptions.color) {
      processedOptions.color = convertColor(processedOptions.color);
    }
    if (typeof processedOptions.fill === 'string') {
      processedOptions.fill = { color: convertColor(processedOptions.fill) };
    }
    
    this.currentSlide.addText(text, processedOptions);
  }

  // 添加图片
  addImage(imageOptions: any): void {
    if (!this.currentSlide) {
      throw new Error('请先创建幻灯片');
    }
    this.currentSlide.addImage(imageOptions);
  }

  // 添加形状
  addShape(shapeType: string, options: any = {}): void {
    if (!this.currentSlide) {
      throw new Error('请先创建幻灯片');
    }
    
    // 转换颜色格式
    const processedOptions = { ...options };
    if (typeof processedOptions.fill === 'string') {
      processedOptions.fill = { color: convertColor(processedOptions.fill) };
    }
    if (typeof processedOptions.line === 'string') {
      processedOptions.line = { color: convertColor(processedOptions.line), width: processedOptions.lineSize ?? 1 };
    }
    
    this.currentSlide.addShape(shapeType, processedOptions);
  }

  // 添加图表
  addChart(chartData: any): void {
    if (!this.currentSlide) {
      throw new Error('请先创建幻灯片');
    }
    this.currentSlide.addChart(chartData.type, chartData.data, chartData.options);
  }

  // 添加媒体
  addMedia(mediaOptions: any): void {
    if (!this.currentSlide) {
      throw new Error('请先创建幻灯片');
    }
    
    // 验证必需参数
    const safeArgs = mediaOptions || {};
    if (!safeArgs.type) {
      throw new Error('Media type is required');
    }
    if (!safeArgs.x) {
      throw new Error('X position is required');
    }
    if (!safeArgs.y) {
      throw new Error('Y position is required');
    }
    if (!safeArgs.w) {
      throw new Error('Width is required');
    }
    if (!safeArgs.h) {
      throw new Error('Height is required');
    }
    
    // 验证媒体源（必须提供 path、data 或 link 中的一个）
    if (!safeArgs.path && !safeArgs.data && !safeArgs.link) {
      throw new Error('Media source is required: provide path, data, or link');
    }
    
    // 构建媒体配置对象
    const mediaConfig: any = {
      type: safeArgs.type,
      x: safeArgs.x,
      y: safeArgs.y,
      w: safeArgs.w,
      h: safeArgs.h
    };
    
    // 添加媒体源
    if (safeArgs.path) {
      mediaConfig.path = safeArgs.path;
    } else if (safeArgs.data) {
      mediaConfig.data = safeArgs.data;
    } else if (safeArgs.link) {
      mediaConfig.link = safeArgs.link;
    }
    
    // 添加可选属性
    if (safeArgs.cover) {
      mediaConfig.cover = safeArgs.cover;
    }
    if (safeArgs.volume !== undefined) {
      mediaConfig.volume = safeArgs.volume;
    }
    if (safeArgs.autoPlay !== undefined) {
      mediaConfig.autoPlay = safeArgs.autoPlay;
    }
    if (safeArgs.loop !== undefined) {
      mediaConfig.loop = safeArgs.loop;
    }
    if (safeArgs.showControls !== undefined) {
      mediaConfig.showControls = safeArgs.showControls;
    }
    
    this.currentSlide.addMedia(mediaConfig);
  }

  // 添加表格
  addTable(tableOptions: any): void {
    if (!this.currentSlide) {
      throw new Error('请先创建幻灯片');
    }
    
    // 验证必需参数
    const safeArgs = tableOptions || {};
    if (!safeArgs.rows || !Array.isArray(safeArgs.rows)) {
      throw new Error('Table rows are required and must be an array');
    }
    
    // 构建表格配置对象
    const tableConfig: any = {
      rows: safeArgs.rows
    };
    
    // 添加位置和尺寸
    if (safeArgs.x !== undefined) tableConfig.x = safeArgs.x;
    if (safeArgs.y !== undefined) tableConfig.y = safeArgs.y;
    if (safeArgs.w !== undefined) tableConfig.w = safeArgs.w;
    if (safeArgs.h !== undefined) tableConfig.h = safeArgs.h;
    
    // 添加列宽和行高
    if (safeArgs.colW && Array.isArray(safeArgs.colW)) {
      tableConfig.colW = safeArgs.colW;
    }
    if (safeArgs.rowH && Array.isArray(safeArgs.rowH)) {
      tableConfig.rowH = safeArgs.rowH;
    }
    
    // 添加表格对齐
    if (safeArgs.align) {
      tableConfig.align = safeArgs.align;
    }
    
    // 添加边框设置 - 支持新的参数结构
    if (safeArgs.border) {
      // 如果传入的是border对象（向后兼容）
      tableConfig.border = {};
      if (safeArgs.border.type) tableConfig.border.type = safeArgs.border.type;
      if (safeArgs.border.pt !== undefined) tableConfig.border.pt = safeArgs.border.pt;
      if (safeArgs.border.color) tableConfig.border.color = safeArgs.border.color;
    }
    
    // 添加默认样式
    if (safeArgs.color) tableConfig.color = safeArgs.color;
    if (safeArgs.fill) tableConfig.fill = safeArgs.fill;
    if (safeArgs.fontFace) tableConfig.fontFace = safeArgs.fontFace;
    if (safeArgs.fontSize !== undefined) tableConfig.fontSize = safeArgs.fontSize;
    if (safeArgs.bold !== undefined) tableConfig.bold = safeArgs.bold;
    if (safeArgs.italic !== undefined) tableConfig.italic = safeArgs.italic;
    if (safeArgs.underline !== undefined) tableConfig.underline = safeArgs.underline;
    if (safeArgs.valign) tableConfig.valign = safeArgs.valign;
    
    // PptxGenJS expects addTable(rows, options) format
    const { rows, ...options } = tableConfig;
    this.currentSlide.addTable(rows, options);
  }

  // 保存 PPT
  async savePpt(filePath: string, options: any = {}): Promise<any> {
    if (!this.ppt) {
      throw new Error('请先创建 PPT');
    }

    this.filePath = filePath;
    
    // 设置默认输出类型
    const outputType = options.outputType || 'stream';
    
    try {
      // 处理文件路径，支持 ~ 符号
      let resolvedPath = filePath;
      if (filePath.startsWith('~/')) {
        resolvedPath = path.join(process.env.HOME || '', filePath.slice(2));
      }
      
      // 确保目录存在
      const dir = path.dirname(resolvedPath);
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
      }
      
      // 如果没有扩展名，添加 .pptx
      if (!path.extname(resolvedPath)) {
        resolvedPath = resolvedPath + '.pptx';
      }
      
      // 在 Node.js 环境中，将 stream 类型转换为 nodebuffer
       let actualOutputType = outputType;
       if (outputType === 'stream') {
         actualOutputType = 'nodebuffer';
       }
       
       if (actualOutputType === 'binarystring' || actualOutputType === 'nodebuffer') {
          // 对于这些类型，我们需要将数据写入文件
          const data = await this.ppt.write({ outputType: actualOutputType });
          
          if (actualOutputType === 'nodebuffer') {
            // Node.js Buffer 可以直接写入
            if (Buffer.isBuffer(data)) {
              fs.writeFileSync(resolvedPath, data);
            } else if (data instanceof ArrayBuffer) {
              fs.writeFileSync(resolvedPath, Buffer.from(data));
            } else if (data instanceof Uint8Array) {
              fs.writeFileSync(resolvedPath, Buffer.from(data));
            } else {
              throw new Error('Unexpected data type for nodebuffer output');
            }
          } else if (actualOutputType === 'binarystring') {
            // 二进制字符串需要转换为 Buffer
            if (typeof data === 'string') {
              fs.writeFileSync(resolvedPath, Buffer.from(data, 'binary'));
            } else {
              throw new Error('Expected string for binarystring output');
            }
          }
         
         return {
           filePath: resolvedPath,
           size: fs.statSync(resolvedPath).size,
           data: options.returnData ? data : undefined
         };
       } else {
        // 对于其他类型（base64, blob, uint8array），返回数据但不写入文件
        const result = await this.ppt.write({
          outputType,
          ...options
        });
        
        return {
          filePath: resolvedPath,
          data: result
        };
      }
    } catch (error) {
      throw new Error(`保存 PPT 失败: ${error instanceof Error ? error.message : String(error)}`);
    }
  }

  // 获取当前状态
  getStatus(): any {
    return {
      hasPpt: !!this.ppt,
      hasCurrentSlide: !!this.currentSlide,
      filePath: this.filePath
    };
  }
}

// 创建全局会话实例
const session = new PptSession();

// 创建 MCP 服务器
const server = new McpServer({
  name: 'pptxgenjs-mcp',
  version: '1.0.0'
});

// 注册工具
server.registerTool('create_ppt', {
  description: '创建新的 PowerPoint 演示文稿',
  inputSchema: {
    title: z.string().optional().describe('演示文稿标题'),
    author: z.string().optional().describe('演示文稿作者'),
    subject: z.string().optional().describe('演示文稿主题'),
    company: z.string().optional().describe('公司名称'),
    revision: z.string().optional().describe('修订版本号'),
    layout: z.enum(['LAYOUT_16x9', 'LAYOUT_16x10', 'LAYOUT_4x3', 'LAYOUT_WIDE']).optional().describe('幻灯片布局'),
    rtlMode: z.boolean().optional().describe('是否启用从右到左模式')
  }
}, async (args) => {
  session.createPpt(args);
  return {
    content: [{
      type: 'text',
      text: '✅ PowerPoint 演示文稿已创建'
    }]
  };
});

server.registerTool('create_slide', {
  description: '创建新的幻灯片',
  inputSchema: {
    background: z.string().optional(),
    masterSlideName: z.string().optional().describe('主幻灯片模板名称'),
    sectionTitle: z.string().optional().describe('节标题'),
    hidden: z.boolean().optional().describe('是否隐藏幻灯片'),
    slideNumber: z.boolean().optional().describe('是否显示幻灯片编号')
  }
}, async (args) => {
  session.createSlide(args);
  return {
    content: [{
      type: 'text',
      text: '✅ 新幻灯片已创建'
    }]
  };
});

server.registerTool('add_text', {
  description: '在当前幻灯片中添加文本',
  inputSchema: {
    text: z.union([z.string(), z.array(z.object({text:z.string(),options:z.record(z.unknown()).optional()}))]).describe('Text or formatted runs'),
    x: z.number().optional().describe('X坐标位置（英寸）'),
    y: z.number().optional().describe('Y坐标位置（英寸）'),
    w: z.number().optional().describe('文本框宽度（英寸）'),
    h: z.number().optional().describe('文本框高度（英寸）'),
    fontSize: z.number().optional().describe('字体大小'),
    bold: z.boolean().optional().describe('是否加粗'),
    italic: z.boolean().optional().describe('是否斜体'),
    underline: z.boolean().optional().describe('是否下划线'),
    color: z.string().optional().describe('文字颜色'),
    align: z.enum(['left', 'center', 'right', 'justify']).optional().describe('文本对齐方式'),
    fontFace: z.string().optional().describe('字体名称'),
    valign: z.enum(['top', 'middle', 'bottom']).optional().describe('垂直对齐方式'),
    margin: z.number().optional().describe('边距'),
    lineSpacing: z.number().optional().describe('行间距'),
    charSpacing: z.number().optional().describe('字符间距'),
    fill: z.string().optional().describe('背景填充颜色'),
    transparency: z.number().optional().describe('透明度(0-100)')
  }
}, async (args) => {
  const { text, ...options } = args;
  session.addText(text, options);
  return {
    content: [{
      type: 'text',
      text: '✅ 文本已添加到幻灯片'
    }]
  };
});

server.registerTool('save_ppt', {
  description: '保存 PowerPoint 演示文稿',
  inputSchema: {
    filePath: z.string().describe('保存文件的路径'),
    outputType: z.enum(['stream', 'base64', 'binarystring', 'blob', 'nodebuffer', 'uint8array']).optional().describe('输出类型'),
    returnData: z.boolean().optional().describe('是否返回文件数据')
  }
}, async (args) => {
  try {
    const result = await session.savePpt(args.filePath, {
      outputType: args.outputType || 'stream',
      returnData: args.returnData || false
    });
    
    return {
      content: [{
        type: 'text',
        text: `✅ PowerPoint 文件已保存到: ${args.filePath}`
      }]
    };
  } catch (error) {
    return {
      content: [{
        type: 'text',
        text: `❌ 保存失败: ${error instanceof Error ? error.message : String(error)}`
      }]
    };
  }
});

server.registerTool('add_image', {
  description: '在当前幻灯片中添加图片',
  inputSchema: {
    path: z.string().optional().describe('图片文件路径'),
    data: z.string().optional().describe('图片的base64数据'),
    hyperlink: z.string().optional().describe('图片超链接'),
    x: z.number().describe('X坐标位置（英寸）'),
    y: z.number().describe('Y坐标位置（英寸）'),
    w: z.number().describe('图片宽度（英寸）'),
    h: z.number().describe('图片高度（英寸）'),
    rotate: z.number().optional().describe('旋转角度'),
    flipH: z.boolean().optional().describe('水平翻转'),
    flipV: z.boolean().optional().describe('垂直翻转'),
    transparency: z.number().optional().describe('透明度(0-100)')
  }
}, async (args) => {
  session.addImage(args);
  return {
    content: [{
      type: 'text',
      text: '✅ 图片已添加到幻灯片'
    }]
  };
});

server.registerTool('add_shape', {
  description: '在当前幻灯片中添加形状',
  inputSchema: {
    options: z.record(z.unknown()).optional(),
    shapeType: z.string().describe('形状类型（如：rect, ellipse, triangle等）'),
    x: z.number().describe('X坐标位置（英寸）'),
    y: z.number().describe('Y坐标位置（英寸）'),
    w: z.number().describe('形状宽度（英寸）'),
    h: z.number().describe('形状高度（英寸）'),
    fill: z.string().optional().describe('填充颜色'),
    line: z.string().optional().describe('边框颜色'),
    lineSize: z.number().optional().describe('边框粗细'),
    rotate: z.number().optional().describe('旋转角度'),
    flipH: z.boolean().optional().describe('水平翻转'),
    flipV: z.boolean().optional().describe('垂直翻转')
  }
}, async (args) => {
  const { shapeType, options = {}, ...placement } = args;
  session.addShape(shapeType, { ...options, ...placement });
  return {
    content: [{
      type: 'text',
      text: '✅ 形状已添加到幻灯片'
    }]
  };
});

server.registerTool('add_chart', {
  description: '在当前幻灯片中添加图表',
  inputSchema: {
    options: z.record(z.unknown()).optional(),
    type: z.enum(['area', 'bar', 'bar3D', 'bubble', 'doughnut', 'line', 'pie', 'radar', 'scatter']).describe('图表类型'),
    data: z.array(z.object({
      name: z.string().describe('数据系列名称'),
      labels: z.array(z.string()).describe('标签数组'),
      values: z.array(z.number()).describe('数值数组')
    })).describe('图表数据'),
    x: z.number().optional().describe('X坐标位置（英寸）'),
    y: z.number().optional().describe('Y坐标位置（英寸）'),
    w: z.number().optional().describe('图表宽度（英寸）'),
    h: z.number().optional().describe('图表高度（英寸）'),
    title: z.string().optional().describe('图表标题'),
    showLegend: z.boolean().optional().describe('是否显示图例'),
    showTitle: z.boolean().optional().describe('是否显示标题')
  }
}, async (args) => {
  const { type, data, options = {}, ...placement } = args;
  session.addChart({ type, data, options: { ...options, ...placement } });
  return {
    content: [{
      type: 'text',
      text: '✅ 图表已添加到幻灯片'
    }]
  };
});

server.registerTool('add_media', {
  description: '在当前幻灯片中添加媒体（音频/视频）',
  inputSchema: {
    type: z.enum(['audio', 'video']).describe('媒体类型'),
    path: z.string().optional().describe('媒体文件路径'),
    data: z.string().optional().describe('媒体的base64数据'),
    link: z.string().optional().describe('媒体链接URL'),
    x: z.number().describe('X坐标位置（英寸）'),
    y: z.number().describe('Y坐标位置（英寸）'),
    w: z.number().describe('媒体宽度（英寸）'),
    h: z.number().describe('媒体高度（英寸）'),
    cover: z.string().optional().describe('封面图片路径'),
    volume: z.number().optional().describe('音量(0-100)'),
    autoPlay: z.boolean().optional().describe('是否自动播放'),
    loop: z.boolean().optional().describe('是否循环播放'),
    showControls: z.boolean().optional().describe('是否显示控制条')
  }
}, async (args) => {
  session.addMedia(args);
  return {
    content: [{
      type: 'text',
      text: '✅ 媒体已添加到幻灯片'
    }]
  };
});

server.registerTool('add_table', {
  description: '在当前幻灯片中添加表格',
  inputSchema: {
    rows: z.array(z.array(z.string())).describe('表格数据（二维数组）'),
    x: z.number().optional().describe('X坐标位置（英寸）'),
    y: z.number().optional().describe('Y坐标位置（英寸）'),
    w: z.number().optional().describe('表格宽度（英寸）'),
    h: z.number().optional().describe('表格高度（英寸）'),
    colW: z.array(z.number()).optional().describe('列宽数组'),
    rowH: z.array(z.number()).optional().describe('行高数组'),
    align: z.enum(['left', 'center', 'right']).optional().describe('表格对齐方式'),
    borderType: z.string().optional().describe('边框类型'),
    borderPt: z.number().optional().describe('边框粗细'),
    borderColor: z.string().optional().describe('边框颜色')
  }
}, async (args) => {
  session.addTable(args);
  return {
    content: [{
      type: 'text',
      text: '✅ 表格已添加到幻灯片'
    }]
  };
});

server.registerTool('add_speaker_notes', {
  description: 'Add presenter notes to the current slide',
  inputSchema: {text:z.string()}
}, async ({text}) => {
  session.addNotes(text);
  return {content:[{type:'text' as const,text:'Speaker notes added'}]};
});

server.registerTool('get_status', {
  description: '获取当前PPT会话状态',
  inputSchema: {}
}, async (args) => {
  const status = session.getStatus();
  return {
    content: [{
      type: 'text',
      text: `📊 当前状态：\n- PPT已创建: ${status.hasPpt ? '是' : '否'}\n- 当前幻灯片: ${status.hasCurrentSlide ? '是' : '否'}\n- 文件路径: ${status.filePath || '未设置'}`
    }]
  };
});

// 启动服务器
async function main() {
  const args = process.argv.slice(2);
  const mode = args.find(arg => arg.startsWith('--mode='))?.split('=')[1] || 'stdio';
  const port = parseInt(args.find(arg => arg.startsWith('--port='))?.split('=')[1] || '3000');

  if (mode === 'streamable' || mode === 'sse') {
    // HTTP 模式 (支持 streamable 和 sse)
    const app = express();
    
    // 启用 CORS
    app.use((req: Request, res: Response, next: NextFunction) => {
      res.header('Access-Control-Allow-Origin', '*');
      res.header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
      res.header('Access-Control-Allow-Headers', 'Content-Type, Accept, x-mcp-session-id');
      if (req.method === 'OPTIONS') {
        res.sendStatus(200);
      } else {
        next();
      }
    });
    
    app.use(express.json());
    
    // Streamable HTTP endpoint - 用于 streaming 模式
    app.post('/mcp', async (req: Request, res: Response) => {
      console.log('Received MCP request (streamable):', req.body);
      
      try {
        const { jsonrpc, id, method, params } = req.body;
        
        // 验证 JSON-RPC 格式
        if (jsonrpc !== '2.0' || !method) {
          return res.status(400).json({
            jsonrpc: '2.0',
            error: {
              code: -32600,
              message: 'Invalid Request'
            },
            id: id || null
          });
        }
        
        let result;
        
        // 处理不同的 MCP 方法
        switch (method) {
          case 'initialize':
            result = {
              protocolVersion: '2024-11-05',
              capabilities: {
                tools: {}
              },
              serverInfo: {
                name: 'pptxgenjs-mcp',
                version: '1.0.0'
              }
            };
            break;
            
          case 'notifications/initialized':
            // 这是一个通知，不需要返回响应
            console.log('MCP client initialized');
            res.status(200).end();
            return;
            
          case 'tools/list':
            // 获取所有注册的工具
            const tools = [];
            
            // 手动构建工具列表（因为无法直接从 McpServer 获取）
            tools.push({
              name: 'create_ppt',
              description: '创建新的 PowerPoint 演示文稿',
              inputSchema: {
                type: 'object',
                properties: {
                  title: { type: 'string', description: '演示文稿标题' },
                  author: { type: 'string', description: '演示文稿作者' },
                  subject: { type: 'string', description: '演示文稿主题' },
                  company: { type: 'string', description: '公司名称' },
                  revision: { type: 'string', description: '修订版本号' },
                  layout: { type: 'string', enum: ['LAYOUT_16x9', 'LAYOUT_16x10', 'LAYOUT_4x3', 'LAYOUT_WIDE'], description: '幻灯片布局' },
                  rtlMode: { type: 'boolean', description: '是否启用从右到左模式' }
                }
              }
            });
            
            tools.push({
              name: 'create_slide',
              description: '创建新的幻灯片',
              inputSchema: {
                type: 'object',
                properties: {
                  masterSlideName: { type: 'string', description: '主幻灯片模板名称' },
                  sectionTitle: { type: 'string', description: '节标题' },
                  hidden: { type: 'boolean', description: '是否隐藏幻灯片' },
                  slideNumber: { type: 'boolean', description: '是否显示幻灯片编号' }
                }
              }
            });
            
            tools.push({
              name: 'add_text',
              description: '在当前幻灯片中添加文本',
              inputSchema: {
                type: 'object',
                properties: {
                  text: { type: 'string', description: '要添加的文本内容' },
                  x: { type: 'number', description: 'X坐标位置（英寸）' },
                  y: { type: 'number', description: 'Y坐标位置（英寸）' },
                  w: { type: 'number', description: '文本框宽度（英寸）' },
                  h: { type: 'number', description: '文本框高度（英寸）' },
                  fontSize: { type: 'number', description: '字体大小' },
                  bold: { type: 'boolean', description: '是否加粗' },
                  italic: { type: 'boolean', description: '是否斜体' },
                  underline: { type: 'boolean', description: '是否下划线' },
                  color: { type: 'string', description: '文字颜色' },
                  align: { type: 'string', enum: ['left', 'center', 'right', 'justify'], description: '文本对齐方式' },
                  fontFace: { type: 'string', description: '字体名称' },
                  valign: { type: 'string', enum: ['top', 'middle', 'bottom'], description: '垂直对齐方式' },
                  margin: { type: 'number', description: '边距' },
                  lineSpacing: { type: 'number', description: '行间距' },
                  charSpacing: { type: 'number', description: '字符间距' },
                  fill: { type: 'string', description: '背景填充颜色' },
                  transparency: { type: 'number', description: '透明度(0-100)' }
                },
                required: ['text']
              }
            });
            
            tools.push({
              name: 'save_ppt',
              description: '保存 PowerPoint 演示文稿',
              inputSchema: {
                type: 'object',
                properties: {
                  filePath: { type: 'string', description: '保存文件的路径' },
                  outputType: { type: 'string', enum: ['stream', 'base64', 'binarystring', 'blob', 'nodebuffer', 'uint8array'], description: '输出类型' },
                  returnData: { type: 'boolean', description: '是否返回文件数据' }
                },
                required: ['filePath']
              }
            });
            
            tools.push({
              name: 'add_image',
              description: '在当前幻灯片中添加图片',
              inputSchema: {
                type: 'object',
                properties: {
                  path: { type: 'string', description: '图片文件路径' },
                  data: { type: 'string', description: '图片的base64数据' },
                  hyperlink: { type: 'string', description: '图片超链接' },
                  x: { type: 'number', description: 'X坐标位置（英寸）' },
                  y: { type: 'number', description: 'Y坐标位置（英寸）' },
                  w: { type: 'number', description: '图片宽度（英寸）' },
                  h: { type: 'number', description: '图片高度（英寸）' },
                  rotate: { type: 'number', description: '旋转角度' },
                  flipH: { type: 'boolean', description: '水平翻转' },
                  flipV: { type: 'boolean', description: '垂直翻转' },
                  transparency: { type: 'number', description: '透明度(0-100)' }
                },
                required: ['x', 'y', 'w', 'h']
              }
            });
            
            tools.push({
              name: 'add_shape',
              description: '在当前幻灯片中添加形状',
              inputSchema: {
                type: 'object',
                properties: {
                  shapeType: { type: 'string', description: '形状类型（如：rect, ellipse, triangle等）' },
                  x: { type: 'number', description: 'X坐标位置（英寸）' },
                  y: { type: 'number', description: 'Y坐标位置（英寸）' },
                  w: { type: 'number', description: '形状宽度（英寸）' },
                  h: { type: 'number', description: '形状高度（英寸）' },
                  fill: { type: 'string', description: '填充颜色' },
                  line: { type: 'string', description: '边框颜色' },
                  lineSize: { type: 'number', description: '边框粗细' },
                  rotate: { type: 'number', description: '旋转角度' },
                  flipH: { type: 'boolean', description: '水平翻转' },
                  flipV: { type: 'boolean', description: '垂直翻转' }
                },
                required: ['shapeType', 'x', 'y', 'w', 'h']
              }
            });
            
            tools.push({
              name: 'add_chart',
              description: '在当前幻灯片中添加图表',
              inputSchema: {
                type: 'object',
                properties: {
                  type: { type: 'string', enum: ['area', 'bar', 'bar3D', 'bubble', 'doughnut', 'line', 'pie', 'radar', 'scatter'], description: '图表类型' },
                  data: {
                    type: 'array',
                    items: {
                      type: 'object',
                      properties: {
                        name: { type: 'string', description: '数据系列名称' },
                        labels: { type: 'array', items: { type: 'string' }, description: '标签数组' },
                        values: { type: 'array', items: { type: 'number' }, description: '数值数组' }
                      },
                      required: ['name', 'labels', 'values']
                    },
                    description: '图表数据'
                  },
                  x: { type: 'number', description: 'X坐标位置（英寸）' },
                  y: { type: 'number', description: 'Y坐标位置（英寸）' },
                  w: { type: 'number', description: '图表宽度（英寸）' },
                  h: { type: 'number', description: '图表高度（英寸）' },
                  title: { type: 'string', description: '图表标题' },
                  showLegend: { type: 'boolean', description: '是否显示图例' },
                  showTitle: { type: 'boolean', description: '是否显示标题' }
                },
                required: ['type', 'data']
              }
            });
            
            tools.push({
              name: 'add_media',
              description: '在当前幻灯片中添加媒体（音频/视频）',
              inputSchema: {
                type: 'object',
                properties: {
                  type: { type: 'string', enum: ['audio', 'video'], description: '媒体类型' },
                  path: { type: 'string', description: '媒体文件路径' },
                  data: { type: 'string', description: '媒体的base64数据' },
                  link: { type: 'string', description: '媒体链接URL' },
                  x: { type: 'number', description: 'X坐标位置（英寸）' },
                  y: { type: 'number', description: 'Y坐标位置（英寸）' },
                  w: { type: 'number', description: '媒体宽度（英寸）' },
                  h: { type: 'number', description: '媒体高度（英寸）' },
                  cover: { type: 'string', description: '封面图片路径' },
                  volume: { type: 'number', description: '音量(0-100)' },
                  autoPlay: { type: 'boolean', description: '是否自动播放' },
                  loop: { type: 'boolean', description: '是否循环播放' },
                  showControls: { type: 'boolean', description: '是否显示控制条' }
                },
                required: ['type', 'x', 'y', 'w', 'h']
              }
            });
            
            tools.push({
              name: 'add_table',
              description: '在当前幻灯片中添加表格',
              inputSchema: {
                type: 'object',
                properties: {
                  rows: { type: 'array', items: { type: 'array', items: { type: 'string' } }, description: '表格数据（二维数组）' },
                  x: { type: 'number', description: 'X坐标位置（英寸）' },
                  y: { type: 'number', description: 'Y坐标位置（英寸）' },
                  w: { type: 'number', description: '表格宽度（英寸）' },
                  h: { type: 'number', description: '表格高度（英寸）' },
                  colW: { type: 'array', items: { type: 'number' }, description: '列宽数组' },
                  rowH: { type: 'array', items: { type: 'number' }, description: '行高数组' },
                  align: { type: 'string', enum: ['left', 'center', 'right'], description: '表格对齐方式' },
                  borderType: { type: 'string', description: '边框类型' },
                  borderPt: { type: 'number', description: '边框粗细' },
                  borderColor: { type: 'string', description: '边框颜色' }
                },
                required: ['rows']
              }
            });
            
            tools.push({
              name: 'get_status',
              description: '获取当前PPT会话状态',
              inputSchema: {
                type: 'object',
                properties: {}
              }
            });
            
            result = { tools };
            break;
            
          case 'tools/call':
            const { name: toolName, arguments: toolArgs } = params;
            
            // 调用相应的工具方法
            switch (toolName) {
              case 'create_ppt':
                session.createPpt(toolArgs);
                result = {
                  content: [{
                    type: 'text',
                    text: '✅ PowerPoint 演示文稿已创建'
                  }]
                };
                break;
                
              case 'create_slide':
                session.createSlide(toolArgs);
                result = {
                  content: [{
                    type: 'text',
                    text: '✅ 新幻灯片已创建'
                  }]
                };
                break;
                
              case 'add_text':
                const { text, ...textOptions } = toolArgs;
                session.addText(text, textOptions);
                result = {
                  content: [{
                    type: 'text',
                    text: '✅ 文本已添加到幻灯片'
                  }]
                };
                break;
                
              case 'save_ppt':
                const saveResult = await session.savePpt(toolArgs.filePath, toolArgs);
                result = {
                  content: [{
                    type: 'text',
                    text: `✅ PowerPoint 演示文稿已保存到: ${toolArgs.filePath}`
                  }]
                };
                break;
                
              case 'add_image':
                session.addImage(toolArgs);
                result = {
                  content: [{
                    type: 'text',
                    text: '✅ 图片已添加到幻灯片'
                  }]
                };
                break;
                
              case 'add_shape':
                const { shapeType, ...shapeOptions } = toolArgs;
                session.addShape(shapeType, shapeOptions);
                result = {
                  content: [{
                    type: 'text',
                    text: '✅ 形状已添加到幻灯片'
                  }]
                };
                break;
                
              case 'add_chart':
                session.addChart(toolArgs);
                result = {
                  content: [{
                    type: 'text',
                    text: '✅ 图表已添加到幻灯片'
                  }]
                };
                break;
                
              case 'add_media':
                session.addMedia(toolArgs);
                result = {
                  content: [{
                    type: 'text',
                    text: '✅ 媒体已添加到幻灯片'
                  }]
                };
                break;
                
              case 'add_table':
                const { rows, x, y, w, h, colW, rowH, align, borderType, borderPt, borderColor, ...otherTableOptions } = toolArgs;
                const tableOptions = {
                  rows,
                  x,
                  y,
                  w,
                  h,
                  colW,
                  rowH,
                  align,
                  border: borderType || borderPt || borderColor ? {
                    type: borderType,
                    pt: borderPt,
                    color: borderColor
                  } : undefined,
                  ...otherTableOptions
                };
                session.addTable(tableOptions);
                result = {
                  content: [{
                    type: 'text',
                    text: '✅ 表格已添加到幻灯片'
                  }]
                };
                break;
                
              case 'get_status':
                const status = session.getStatus();
                result = {
                  content: [{
                    type: 'text',
                    text: `当前状态: ${JSON.stringify(status, null, 2)}`
                  }]
                };
                break;
                
              default:
                throw new Error(`Unknown tool: ${toolName}`);
            }
            break;
            
          default:
            throw new Error(`Unknown method: ${method}`);
        }
        
        // 返回成功响应
        res.json({
          jsonrpc: '2.0',
          result,
          id
        });
        
      } catch (error) {
        console.error('Error handling MCP request:', error);
        if (!res.headersSent) {
          res.status(500).json({
            jsonrpc: '2.0',
            error: {
              code: -32603,
              message: error instanceof Error ? error.message : 'Internal server error',
            },
            id: req.body?.id || null,
          });
        }
      }
    });
    
    // SSE endpoint - 真正的 Server-Sent Events 模式
    app.get('/sse', (req: Request, res: Response) => {
      console.log('SSE connection established');
      
      // 设置 SSE 响应头
      res.writeHead(200, {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Cache-Control'
      });
      
      // 发送初始连接事件
      res.write('data: {"type": "connection", "message": "SSE connection established"}\n\n');
      
      // 定期发送心跳
      const heartbeat = setInterval(() => {
        res.write('data: {"type": "heartbeat", "timestamp": "' + new Date().toISOString() + '"}\n\n');
      }, 30000);
      
      // 处理连接关闭
      req.on('close', () => {
        console.log('SSE connection closed');
        clearInterval(heartbeat);
      });
    });
    
    // SSE 消息发送端点
    app.post('/sse/send', async (req: Request, res: Response) => {
      console.log('Received SSE message request:', req.body);
      
      try {
        // 这里可以处理 MCP 请求并通过 SSE 发送响应
        // 目前返回简单的确认
        res.json({
          success: true,
          message: 'Message queued for SSE delivery'
        });
      } catch (error) {
         console.error('Error handling SSE message:', error);
         res.status(500).json({
           success: false,
           error: error instanceof Error ? error.message : 'Unknown error'
         });
      }
    });
    
    app.listen(port, () => {
      console.error(`PptxGenJS MCP 服务器已启动 (${mode === 'sse' ? 'SSE' : 'Streamable HTTP'} 模式，端口: ${port})`);
      console.error(`Streamable endpoint: http://localhost:${port}/mcp`);
      console.error(`SSE endpoint: http://localhost:${port}/sse`);
    });
  } else {
    // STDIO 模式
    const transport = new StdioServerTransport();
    await server.connect(transport);
    console.error('PptxGenJS MCP 服务器已启动 (STDIO 模式)');
  }
}

main().catch((error) => {
  console.error('服务器启动失败:', error);
  process.exit(1);
});
