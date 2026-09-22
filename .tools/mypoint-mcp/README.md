# PptxGenJS MCP Server

基于 PptxGenJS 的 MCP (Model Context Protocol) 服务器，提供 PowerPoint 演示文稿创建和编辑功能。

## 功能特性

- **会话状态管理**: 每个会话维护独立的 PPT 实例
- **创建和管理 PPT**: 创建新的演示文稿（支持详细配置参数）、打开现有文件、保存文件
- **幻灯片操作**: 创建、添加、删除幻灯片
- **内容添加**: 支持添加图表、图片、媒体、表格、文本等内容
- **多种启动模式**: 支持 STDIO 和 SSE 两种模式
- **丰富的配置选项**: 支持元数据、布局、主题、RTL 模式等详细配置

## 安装

```bash
npm install
npm run build
```

## 使用方法

### 启动服务器

#### STDIO 模式（默认）
```bash
npm start
# 或者明确指定
npm start -- --mode=stdio
```

#### SSE 模式（Server-Sent Events）
```bash
npm start -- --mode=sse --port=3000
```

SSE 模式将启动一个 HTTP 服务器，提供以下端点：
- `GET /sse` - 建立 SSE 连接
- `POST /messages` - 接收 MCP 消息

服务器将根据指定的模式启动，可以与支持 MCP 的客户端进行通信。

或者开发模式：

```bash
npm run dev
```

### 可用工具

#### 1. create_ppt
创建新的 PowerPoint 演示文稿

支持丰富的配置参数：

**元数据属性：**
- `title` - 演示文稿标题
- `author` - 作者
- `subject` - 主题
- `company` - 公司
- `revision` - 版本号

**布局选项：**
- `layout` - 预定义布局（如 'LAYOUT_16x9', 'LAYOUT_16x10', 'LAYOUT_4x3', 'LAYOUT_WIDE'）
- `customLayout` - 自定义布局对象：
  - `name` - 布局名称
  - `width` - 宽度（英寸）
  - `height` - 高度（英寸）

**其他选项：**
- `rtlMode` - 启用从右到左文本模式（布尔值）
- `theme` - 主题设置对象：
  - `headFontFace` - 标题字体
  - `bodyFontFace` - 正文字体
  - `lang` - 语言代码

**详细配置示例：**
```json
{
  "name": "create_ppt",
  "arguments": {
    "title": "我的演示文稿",
    "author": "张三",
    "subject": "产品介绍",
    "company": "ABC 公司",
    "revision": "1.0",
    "layout": "LAYOUT_16x9",
    "theme": {
      "headFontFace": "Microsoft YaHei",
      "bodyFontFace": "Microsoft YaHei",
      "lang": "zh-CN"
    }
  }
}
```

**自定义布局示例：**
```json
{
  "name": "create_ppt",
  "arguments": {
    "title": "自定义布局演示",
    "customLayout": {
      "name": "A4_PORTRAIT",
      "width": 8.27,
      "height": 11.69
    },
    "rtlMode": true
  }
}
```

**简单创建示例：**
```json
{
  "name": "create_ppt",
  "arguments": {}
}
```

#### 2. open_ppt
打开现有的 PowerPoint 文件

```json
{
  "name": "open_ppt",
  "arguments": {
    "filePath": "path/to/presentation.pptx"
  }
}
```

#### 3. create_slide
创建新的幻灯片页面

```json
{
  "name": "create_slide",
  "arguments": {
    "options": {
      "masterSlideName": "MASTER_SLIDE",
      "sectionTitle": "Section Title"
    }
  }
}
```

#### 4. add_slide
在指定位置插入幻灯片（支持详细配置参数）

**参数说明：**
- `index`：插入位置索引（必需）
- `background`：幻灯片背景设置
  - `color`：背景颜色（十六进制颜色代码，如 "F1F1F1"）
  - `transparency`：背景透明度（0-100）
  - `data`：背景图片的 base64 数据
  - `path`：背景图片的 URL 或文件路径
- `color`：幻灯片默认文本颜色（十六进制颜色代码）
- `hidden`：是否隐藏幻灯片
- `slideNumber`：幻灯片编号设置
  - `x`, `y`：位置（英寸或百分比）
  - `w`, `h`：尺寸（英寸或百分比）
  - `fontFace`：字体名称
  - `fontSize`：字体大小
  - `color`：字体颜色
  - `align`：对齐方式（left/center/right）
- `masterName`：使用的幻灯片母版名称

**详细配置示例：**
```json
{
  "name": "add_slide",
  "arguments": {
    "index": 2,
    "background": {
      "color": "FF5733",
      "transparency": 20
    },
    "color": "333333",
    "slideNumber": {
      "x": 10,
      "y": 10,
      "fontFace": "Arial",
      "fontSize": 12,
      "color": "FFFFFF",
      "align": "center"
    }
  }
}
```

**背景图片示例：**
```json
{
  "name": "add_slide",
  "arguments": {
    "index": 3,
    "background": {
      "path": "/path/to/background.jpg"
    },
    "hidden": true,
    "masterName": "Custom Master"
  }
}
```

**简单插入示例：**
```json
{
  "name": "add_slide",
  "arguments": {
    "index": 1
  }
}
```

#### 5. delete_slide
删除指定的幻灯片

```json
{
  "name": "delete_slide",
  "arguments": {
    "index": 1
  }
}
```

#### 6. add_text
向当前幻灯片添加文本

**参数说明：**
- **文本内容：**
  - `text`: 文本内容（支持字符串或文本对象数组）
    - 字符串：简单文本
    - 数组：支持逐词/逐行格式化的文本对象数组
- **位置和尺寸：**
  - `x`: 水平位置（英寸数值或百分比字符串，如 1.5 或 "50%"，默认：1.0）
  - `y`: 垂直位置（英寸数值或百分比字符串，如 1.0 或 "25%"，默认：1.0）
  - `w`: 宽度（英寸数值或百分比字符串，如 4.0 或 "50%"，默认：1.0）
  - `h`: 高度（英寸数值或百分比字符串，如 3.0 或 "40%"，默认：1.0）
- **字体和格式：**
  - `fontSize`: 默认字体大小（磅，默认：12）
  - `fontFace`: 默认字体名称（如 "Arial", "Times New Roman"）
  - `color`: 默认字体颜色（十六进制，不含#，如 "FF0000"）
  - `bold`: 是否加粗（默认：false）
  - `italic`: 是否斜体（默认：false）
  - `underline`: 是否下划线（默认：false）
- **对齐方式：**
  - `align`: 水平对齐方式（left/center/right/justify，默认：left）
  - `valign`: 垂直对齐方式（top/middle/bottom，默认：top）
- **背景和边框：**
  - `fill`: 文本框背景填充
    - `color`: 背景颜色（十六进制，不含#）
    - `transparency`: 背景透明度（0-100）
- **内边距和间距：**
  - `margin`: 内边距（数值或 [上,右,下,左] 数组）
  - `paraSpaceBefore`: 段落前间距（磅，默认：0）
  - `paraSpaceAfter`: 段落后间距（磅，默认：0）
- **项目符号：**
  - `bullet`: 项目符号配置
    - 布尔值：是否使用默认项目符号
    - 对象：自定义项目符号配置
      - `type`: 项目符号类型（bullet/number）
      - `code`: 自定义 Unicode 代码（如 "2605" 为星号）
      - `style`: 编号样式
      - `startAt`: 编号起始值（默认：1）
- **超链接：**
  - `hyperlink`: 超链接配置
    - `url`: 链接 URL
    - `slide`: 链接到的幻灯片编号
    - `tooltip`: 鼠标悬停提示文本
- **特殊效果：**
  - `shadow`: 文字阴影效果
    - `type`: 阴影类型（outer/inner/none，默认：none）
    - `angle`: 阴影角度（度，默认：45）
    - `blur`: 阴影模糊度（磅，默认：3）
    - `color`: 阴影颜色（十六进制，不含#，默认："696969"）
    - `offset`: 阴影偏移距离（磅，默认：3）
    - `opacity`: 阴影透明度（0-1，默认：0.75）
  - `outline`: 文字轮廓效果
    - `size`: 轮廓粗细（磅，默认：1）
    - `color`: 轮廓颜色（十六进制，不含#）
- **文本框属性：**
  - `isTextBox`: 是否创建为文本框（默认：false）
  - `rotate`: 旋转角度（0-359 度，默认：0）
  - `flipH`: 是否水平翻转（默认：false）
  - `flipV`: 是否垂直翻转（默认：false）

**使用示例：**

1. **基础文本：**
```json
{
  "name": "add_text",
  "arguments": {
    "text": "Hello World",
    "x": 1,
    "y": 1,
    "w": 5,
    "h": 1,
    "fontSize": 18,
    "color": "363636",
    "bold": true,
    "align": "center"
  }
}
```

2. **带样式的文本：**
```json
{
  "name": "add_text",
  "arguments": {
    "text": "重要通知",
    "x": 2,
    "y": 2,
    "w": 4,
    "h": 2,
    "fontSize": 24,
    "fontFace": "Arial",
    "color": "FFFFFF",
    "bold": true,
    "align": "center",
    "valign": "middle",
    "fill": {
      "color": "FF6B6B",
      "transparency": 20
    },
    "shadow": {
      "type": "outer",
      "color": "000000",
      "blur": 5,
      "offset": 3,
      "opacity": 0.5
    },
    "margin": 10
  }
}
```

3. **多格式文本数组：**
```json
{
  "name": "add_text",
  "arguments": {
    "text": [
      {
        "text": "标题：",
        "options": {
          "fontSize": 20,
          "bold": true,
          "color": "0066CC"
        }
      },
      {
        "text": "这是正文内容，",
        "options": {
          "fontSize": 14,
          "color": "333333"
        }
      },
      {
        "text": "这是重点强调的部分。",
        "options": {
          "fontSize": 14,
          "bold": true,
          "color": "FF0000",
          "underline": true
        }
      }
    ],
    "x": 1,
    "y": 3,
    "w": 6,
    "h": 2
  }
}
```

4. **项目符号列表：**
```json
{
  "name": "add_text",
  "arguments": {
    "text": "第一项\n第二项\n第三项",
    "x": 1,
    "y": 1,
    "w": 5,
    "h": 3,
    "fontSize": 16,
    "bullet": {
      "type": "bullet",
      "code": "2022"
    }
  }
}
```

5. **超链接文本：**
```json
{
  "name": "add_text",
  "arguments": {
    "text": "点击访问官网",
    "x": 2,
    "y": 4,
    "w": 3,
    "h": 1,
    "fontSize": 14,
    "color": "0066CC",
    "underline": true,
    "hyperlink": {
      "url": "https://www.example.com",
      "tooltip": "访问官方网站"
    }
  }
}
```

#### 7. add_image
向当前幻灯片添加图片

**参数说明：**
- **数据源（二选一）：**
  - `path`: 图片文件路径或 URL（支持相对路径、绝对路径、网络 URL）
  - `data`: 图片的 base64 编码数据（格式："image/png;base64,iVBORw0KGgoAAAANSUhEUgAA..."）
- **位置和尺寸：**
  - `x`: 水平位置（英寸数值或百分比字符串，如 1.5 或 "50%"，默认：1.0）
  - `y`: 垂直位置（英寸数值或百分比字符串，如 1.0 或 "25%"，默认：1.0）
  - `w`: 宽度（英寸数值或百分比字符串，如 4.0 或 "50%"，默认：1.0）
  - `h`: 高度（英寸数值或百分比字符串，如 3.0 或 "40%"，默认：1.0）
- **图片属性：**
  - `altText`: 图片的替代文本（用于无障碍访问）
  - `flipH`: 是否水平翻转图片（默认：false）
  - `flipV`: 是否垂直翻转图片（默认：false）
  - `rotate`: 旋转角度（0-359 度，默认：0）
  - `rounding`: 是否将图片裁剪为圆形（默认：false）
  - `transparency`: 透明度（0-100，0 表示完全不透明，100 表示完全透明，默认：0）
- **超链接：**
  - `hyperlink`: 为图片添加超链接
    - `url`: 链接 URL
    - `slide`: 链接到的幻灯片编号（内部链接）
    - `tooltip`: 鼠标悬停时显示的提示文本
- **占位符：**
  - `placeholder`: 占位符位置（如 "title", "body", "content" 等）
- **图片尺寸调整：**
  - `sizing`: 图片尺寸调整和裁剪设置
    - `type`: 尺寸调整类型（"crop", "contain", "cover"）
    - `w`: 调整区域宽度（英寸）
    - `h`: 调整区域高度（英寸）
    - `x`: 裁剪起始 X 坐标（仅 crop 类型有效，默认：0）
    - `y`: 裁剪起始 Y 坐标（仅 crop 类型有效，默认：0）
- **阴影效果：**
  - `shadow`: 图片阴影效果设置
    - `type`: 阴影类型（"outer", "inner", "none"，默认："outer"）
    - `angle`: 阴影角度（度，默认：45）
    - `blur`: 阴影模糊度（磅，默认：3）
    - `color`: 阴影颜色（十六进制，如 "808080"，默认："808080"）
    - `offset`: 阴影偏移距离（磅，默认：3）
    - `opacity`: 阴影透明度（0-1，默认：0.75）

**使用示例：**

1. **详细配置的图片：**
```json
{
  "name": "add_image",
  "arguments": {
    "path": "https://example.com/image.jpg",
    "x": 1.0,
    "y": 1.0,
    "w": 4.0,
    "h": 3.0,
    "altText": "示例图片",
    "rotate": 15,
    "transparency": 10,
    "hyperlink": {
      "url": "https://example.com",
      "tooltip": "点击访问网站"
    },
    "shadow": {
      "type": "outer",
      "angle": 45,
      "blur": 5,
      "color": "808080",
      "offset": 4,
      "opacity": 0.8
    }
  }
}
```

2. **圆形头像图片：**
```json
{
  "name": "add_image",
  "arguments": {
    "path": "./avatar.png",
    "x": 6.0,
    "y": 1.0,
    "w": 2.0,
    "h": 2.0,
    "rounding": true,
    "altText": "用户头像"
  }
}
```

3. **Base64 编码图片：**
```json
{
  "name": "add_image",
  "arguments": {
    "data": "image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
    "x": "25%",
    "y": "50%",
    "w": "50%",
    "h": "30%"
  }
}
```

4. **带裁剪的图片：**
```json
{
  "name": "add_image",
  "arguments": {
    "path": "./large-image.jpg",
    "x": 1.0,
    "y": 4.0,
    "w": 3.0,
    "h": 2.0,
    "sizing": {
      "type": "crop",
      "w": 3.0,
      "h": 2.0,
      "x": 100,
      "y": 50
    }
  }
}
```

#### 8. add_chart
向当前幻灯片添加图表

**参数说明：**
- `type`: 图表类型（必需）
  - 支持的类型：`area`, `bar`, `bar3D`, `bubble`, `doughnut`, `line`, `pie`, `pie3D`, `radar`, `scatter`
- `data`: 图表数据数组（必需）
  - `name`: 数据系列名称
  - `labels`: 数据标签数组
  - `values`: 数据值数组
- `options`: 图表配置选项（可选）
  - **位置和尺寸：**
    - `x`, `y`: 图表位置（英寸）
    - `w`, `h`: 图表宽度和高度（英寸）
  - **标题配置：**
    - `title`: 图表标题
    - `showTitle`: 是否显示标题
    - `titleFontFace`, `titleFontSize`, `titleColor`: 标题字体样式
  - **图例配置：**
    - `showLegend`: 是否显示图例
    - `legendPos`: 图例位置（`t`, `b`, `l`, `r`）
  - **颜色和样式：**
    - `chartColors`: 自定义颜色数组
    - `chartColorsOpacity`: 颜色透明度（0-100）
  - **柱状图特有：**
    - `barDir`: 方向（`bar` 或 `col`）
    - `barGrouping`: 分组方式（`clustered`, `stacked`, `percentStacked`）
    - `barGapWidthPct`: 柱间距百分比
  - **饼图特有：**
    - `showPercent`: 显示百分比
    - `holeSize`: 环形图内径百分比
  - **数据标签：**
    - `showDataLabels`: 显示数据标签
    - `dataLabelColor`, `dataLabelFontSize`: 数据标签样式
  - **坐标轴：**
    - `catAxisTitle`, `valAxisTitle`: 坐标轴标题
    - `showCatAxisTitle`, `showValAxisTitle`: 是否显示坐标轴标题
  - **图表区域：**
    - `chartArea`: 图表区域样式（`fill`, `border`）
    - `plotArea`: 绘图区域样式

**使用示例：**

1. **详细配置的柱状图：**
```json
{
  "name": "add_chart",
  "arguments": {
    "type": "bar",
    "data": [
      {
        "name": "实际销售",
        "labels": ["Q1", "Q2", "Q3", "Q4"],
        "values": [1500, 2300, 1800, 2800]
      },
      {
        "name": "预期销售",
        "labels": ["Q1", "Q2", "Q3", "Q4"],
        "values": [1200, 2000, 2200, 2500]
      }
    ],
    "options": {
      "x": 1,
      "y": 1,
      "w": 8,
      "h": 5,
      "title": "季度销售对比",
      "showTitle": true,
      "titleFontSize": 18,
      "titleColor": "0066CC",
      "showLegend": true,
      "legendPos": "b",
      "chartColors": ["0088CC", "FF6600"],
      "barDir": "col",
      "barGrouping": "clustered",
      "showDataLabels": true,
      "catAxisTitle": "季度",
      "valAxisTitle": "销售额（万元）"
    }
  }
}
```

2. **简单饼图：**
```json
{
  "name": "add_chart",
  "arguments": {
    "type": "pie",
    "data": [
      {
        "name": "市场份额",
        "labels": ["产品A", "产品B", "产品C", "其他"],
        "values": [35, 25, 20, 20]
      }
    ],
    "options": {
      "x": 1,
      "y": 1,
      "w": 6,
      "h": 4,
      "showPercent": true,
      "showLegend": true,
      "chartColors": ["FF6B6B", "4ECDC4", "FFE66D", "A8E6CF"]
    }
  }
}
```

3. **基础折线图：**
```json
{
  "name": "add_chart",
  "arguments": {
    "type": "line",
    "data": [
      {
        "name": "趋势数据",
        "labels": ["1月", "2月", "3月", "4月", "5月"],
        "values": [10, 25, 18, 32, 28]
      }
    ],
    "options": {
      "x": 1,
      "y": 1,
      "w": 7,
      "h": 4
    }
  }
}
```

#### 9. add_table
向当前幻灯片添加表格

**参数配置：**

**表格数据（必需）：**
- `rows`: 表格行数据数组，每行包含单元格数据（字符串或对象）

**位置和尺寸：**
- `x`: 水平位置（英寸，从幻灯片左边缘开始）
- `y`: 垂直位置（英寸，从幻灯片顶部开始）
- `w`: 表格宽度（英寸）
- `h`: 表格高度（英寸）

**列宽和行高：**
- `colW`: 各列宽度数组（英寸）
- `rowH`: 各行高度数组（英寸）

**表格样式：**
- `align`: 表格对齐方式（"left", "center", "right"）
- `border`: 边框设置（type, pt, color）
- `color`: 默认文字颜色（十六进制，不含#）
- `fill`: 默认背景色（十六进制，不含#）
- `fontFace`: 默认字体名称
- `fontSize`: 默认字体大小（磅）
- `margin`: 默认单元格内边距（磅）
- `valign`: 默认垂直对齐方式（"top", "middle", "bottom"）

**单元格对象格式：**
- `text`: 单元格文本内容
- `options`: 单元格样式选项（align, valign, bold, italic, underline, fontSize, fontFace, color, fill, margin, colspan, rowspan）

**使用示例：**

1. **基础表格：**
```json
{
  "name": "add_table",
  "arguments": {
    "rows": [
      ["产品", "Q1销售", "Q2销售", "增长率"],
      ["产品A", "100万", "120万", "20%"],
      ["产品B", "80万", "95万", "18.75%"],
      ["产品C", "60万", "75万", "25%"]
    ],
    "x": 1,
    "y": 1,
    "w": 8,
    "h": 3
  }
}
```

2. **带样式的表格：**
```json
{
  "name": "add_table",
  "arguments": {
    "rows": [
      ["季度", "销售额", "利润"],
      ["Q1", "500万", "50万"],
      ["Q2", "600万", "65万"],
      ["Q3", "550万", "58万"]
    ],
    "x": 1,
    "y": 2,
    "w": 6,
    "h": 2.5,
    "colW": [1.5, 2, 2.5],
    "border": {
      "type": "solid",
      "pt": 1,
      "color": "333333"
    },
    "fontFace": "Arial",
    "fontSize": 12,
    "align": "center",
    "valign": "middle"
  }
}
```

3. **复杂单元格表格：**
```json
{
  "name": "add_table",
  "arguments": {
    "rows": [
      [
        {
          "text": "产品名称",
          "options": {
            "bold": true,
            "fill": "4472C4",
            "color": "FFFFFF",
            "align": "center"
          }
        },
        {
          "text": "销售数据",
          "options": {
            "bold": true,
            "fill": "4472C4",
            "color": "FFFFFF",
            "align": "center",
            "colspan": 2
          }
        }
      ],
      [
        "产品A",
        {
          "text": "150万",
          "options": {
            "align": "right",
            "color": "0066CC"
          }
        },
        {
          "text": "↑15%",
          "options": {
            "align": "center",
            "color": "00AA00",
            "bold": true
          }
        }
      ]
    ],
    "x": 1,
    "y": 1,
    "w": 6,
    "h": 2
  }
}
```

#### 10. add_media
向当前幻灯片添加媒体内容（音频/视频/在线视频） <mcreference link="https://gitbrent.github.io/PptxGenJS/docs/api-media/" index="1">1</mcreference>

**参数配置：**

**媒体源（必须提供其中之一）：**
- `type`: 媒体类型（"audio", "video", "online"）
- `path`: 媒体文件路径（本地路径或网络 URL）
- `data`: 媒体的 base64 编码数据（格式："audio/mp3;base64,iVtDafDrBF..."）
- `link`: YouTube 嵌入 URL（用于在线视频，格式："https://www.youtube.com/embed/VIDEO_ID"）

**位置和尺寸（必需）：**
- `x`: 水平位置（英寸，从幻灯片左边缘开始）
- `y`: 垂直位置（英寸，从幻灯片顶部开始）
- `w`: 宽度（英寸）
- `h`: 高度（英寸）

**媒体选项（可选）：**
- `cover`: 封面图片路径或 base64 数据（用于媒体预览）
- `volume`: 音量级别（0-100，适用于音频/视频）
- `autoPlay`: 是否在显示幻灯片时自动播放媒体（默认：false）
- `loop`: 是否循环播放媒体（默认：false）
- `showControls`: 是否显示媒体播放器控件（默认：true）

**使用示例：**

1. **添加视频文件（带完整配置）：**
```json
{
  "name": "add_media",
  "arguments": {
    "type": "video",
    "path": "https://example.com/sample.mp4",
    "x": 1.0,
    "y": 1.0,
    "w": 6.0,
    "h": 4.0,
    "cover": "https://example.com/cover.jpg",
    "volume": 75,
    "autoPlay": false,
    "loop": true,
    "showControls": true
  }
}
```

2. **添加音频文件（Base64 编码）：**
```json
{
  "name": "add_media",
  "arguments": {
    "type": "audio",
    "data": "audio/mp3;base64,iVtDafDrBF[...]",
    "x": 8.0,
    "y": 1.0,
    "w": 3.0,
    "h": 2.0,
    "volume": 50,
    "autoPlay": true
  }
}
```

3. **添加 YouTube 在线视频：**
```json
{
  "name": "add_media",
  "arguments": {
    "type": "online",
    "link": "https://www.youtube.com/embed/Dph6ynRVyUc",
    "x": 1.0,
    "y": 5.5,
    "w": 8.0,
    "h": 4.5,
    "showControls": false
  }
}
```

4. **添加本地音频文件（简单配置）：**
```json
{
  "name": "add_media",
  "arguments": {
    "type": "audio",
    "path": "../media/background.mp3",
    "x": 0.5,
    "y": 0.5,
    "w": 2.0,
    "h": 1.0
  }
}
```

#### 11. add_shape
向当前幻灯片添加形状 <mcreference link="https://gitbrent.github.io/PptxGenJS/docs/api-shapes/" index="2">2</mcreference>

**参数配置：**

**形状类型和位置（必需）：**
- `shapeType`: 形状类型（如 "rect"、"ellipse"、"line"、"triangle"、"diamond"、"pentagon"、"hexagon"、"star"、"arrow" 等）
- `x`: 水平位置（英寸，从幻灯片左边缘开始）
- `y`: 垂直位置（英寸，从幻灯片顶部开始）
- `w`: 宽度（英寸）
- `h`: 高度（英寸）

**填充样式（可选）：**
- `fill`: 形状填充样式
  - `type`: 填充类型（"solid" 或 "none"，默认："solid"）
  - `color`: 填充颜色（十六进制颜色代码，如 "FF0000"）
  - `transparency`: 填充透明度（0-100）

**线条样式（可选）：**
- `line`: 形状边框线条样式
  - `color`: 线条颜色（十六进制颜色代码，如 "000000"）
  - `width`: 线条宽度（磅，默认：1）
  - `dashType`: 线条样式类型（"solid"、"dash"、"dashDot" 等，默认："solid"）
  - `beginArrowType`: 线条起始箭头类型（"none"、"triangle"、"stealth"、"diamond"、"oval"，默认："none"）
  - `endArrowType`: 线条结束箭头类型（"none"、"triangle"、"stealth"、"diamond"、"oval"，默认："none"）

**阴影效果（可选）：**
- `shadow`: 形状阴影效果
  - `type`: 阴影类型（"outer"、"inner"、"none"，默认："none"）
  - `angle`: 阴影角度（度，默认：45）
  - `blur`: 阴影模糊度（磅，默认：3）
  - `color`: 阴影颜色（十六进制颜色代码，如 "808080"，默认："808080"）
  - `offset`: 阴影偏移距离（磅，默认：3）
  - `opacity`: 阴影透明度（0-1，默认：0.75）

**变换效果（可选）：**
- `rotate`: 旋转角度（度，0-360）
- `flipH`: 是否水平翻转（默认：false）
- `flipV`: 是否垂直翻转（默认：false）

**使用示例：**

1. **添加带样式的矩形：**
```json
{
  "name": "add_shape",
  "arguments": {
    "shapeType": "rect",
    "x": 1.0,
    "y": 1.0,
    "w": 4.0,
    "h": 2.0,
    "fill": {
      "type": "solid",
      "color": "4472C4",
      "transparency": 20
    },
    "line": {
      "color": "2F5597",
      "width": 2,
      "dashType": "solid"
    },
    "shadow": {
      "type": "outer",
      "angle": 45,
      "blur": 4,
      "color": "808080",
      "offset": 3,
      "opacity": 0.6
    }
  }
}
```

2. **添加圆形（椭圆）：**
```json
{
  "name": "add_shape",
  "arguments": {
    "shapeType": "ellipse",
    "x": 6.0,
    "y": 1.0,
    "w": 2.0,
    "h": 2.0,
    "fill": {
      "type": "solid",
      "color": "FF6B6B"
    },
    "line": {
      "color": "E55555",
      "width": 3
    }
  }
}
```

3. **添加带箭头的直线：**
```json
{
  "name": "add_shape",
  "arguments": {
    "shapeType": "line",
    "x": 1.0,
    "y": 4.0,
    "w": 6.0,
    "h": 0.1,
    "line": {
      "color": "000000",
      "width": 2,
      "endArrowType": "triangle"
    }
  }
}
```

4. **添加旋转的星形：**
```json
{
  "name": "add_shape",
  "arguments": {
    "shapeType": "star",
    "x": 3.0,
    "y": 5.0,
    "w": 2.0,
    "h": 2.0,
    "fill": {
      "type": "solid",
      "color": "FFD700"
    },
    "rotate": 30,
    "shadow": {
      "type": "outer",
      "color": "FFA500",
      "opacity": 0.8
    }
  }
}
```

5. **添加无填充的三角形：**
```json
{
  "name": "add_shape",
  "arguments": {
    "shapeType": "triangle",
    "x": 7.0,
    "y": 4.0,
    "w": 2.0,
    "h": 2.0,
    "fill": {
      "type": "none"
    },
    "line": {
      "color": "0066CC",
      "width": 3,
      "dashType": "dash"
    }
  }
}
```

#### 12. save_ppt
保存 PowerPoint 文件，支持多种输出格式和配置选项

**参数配置：**

**基本保存选项：**
- `fileName` (string): 输出文件名（包含扩展名），默认 "Presentation.pptx"
- `filePath` (string): 完整文件路径（优先级高于 fileName）

**压缩选项：**
- `compression` (boolean): 是否应用 ZIP 压缩，默认 false（导出时间更长但节省空间）

**输出格式选项：**
- `outputType` (string): 输出格式类型，默认 "file"
  - `file`: 保存为文件
  - `arraybuffer`: 返回 ArrayBuffer
  - `base64`: 返回 Base64 字符串
  - `binarystring`: 返回二进制字符串
  - `blob`: 返回 Blob 对象
  - `nodebuffer`: 返回 Node.js Buffer
  - `uint8array`: 返回 Uint8Array
  - `stream`: 流式输出（仅 Node.js）

**流式输出选项（仅 Node.js 环境）：**
- `streamOptions` (object): 流式输出配置
  - `port` (number): HTTP 服务器端口，默认 3000
  - `endpoint` (string): HTTP 端点路径，默认 "/"
  - `contentDisposition` (string): Content-Disposition 头部值，默认 "attachment"

**返回选项：**
- `returnData` (boolean): 是否在响应中返回文件数据，默认 false
- `dataPreviewLength` (number): 返回数据预览的字符长度，默认 100（0 表示不预览）

**使用示例：**

```json
// 1. 基本文件保存
{
  "name": "save_ppt",
  "arguments": {
    "fileName": "my-presentation.pptx"
  }
}

// 2. 指定完整路径保存
{
  "name": "save_ppt",
  "arguments": {
    "filePath": "/Users/username/Documents/presentation.pptx",
    "compression": true
  }
}

// 3. 导出为 Base64 格式
{
  "name": "save_ppt",
  "arguments": {
    "outputType": "base64",
    "compression": true,
    "returnData": true,
    "dataPreviewLength": 200
  }
}

// 4. 导出为 ArrayBuffer
{
  "name": "save_ppt",
  "arguments": {
    "outputType": "arraybuffer",
    "returnData": false
  }
}

// 5. 流式输出（Node.js）
{
  "name": "save_ppt",
  "arguments": {
    "outputType": "stream",
    "streamOptions": {
      "port": 8080,
      "endpoint": "/download",
      "contentDisposition": "attachment; filename=presentation.pptx"
    }
  }
}
```

## 工作流程示例

```json
// 1. 创建新的 PPT
{"name": "create_ppt", "arguments": {}}

// 2. 创建第一张幻灯片
{"name": "create_slide", "arguments": {}}

// 3. 添加标题文本
{
  "name": "add_text",
  "arguments": {
    "text": "我的演示文稿",
    "options": {
      "x": 1, "y": 1, "w": 8, "h": 1,
      "fontSize": 24, "bold": true, "align": "center"
    }
  }
}

// 4. 添加内容文本
{
  "name": "add_text",
  "arguments": {
    "text": "这是演示文稿的内容",
    "options": {
      "x": 1, "y": 3, "w": 8, "h": 2,
      "fontSize": 16
    }
  }
}

// 5. 保存文件
{"name": "save_ppt", "arguments": {"filePath": "my-presentation.pptx"}}
```

## 注意事项

1. **会话状态**：服务器维护当前 PPT 和幻灯片的状态，所有操作都作用于当前活动的 PPT 和幻灯片。

2. **幻灯片切换**：调用 `create_slide` 或 `add_slide` 会切换到新的幻灯片，后续的内容添加操作都会作用于这张幻灯片。

3. **文件路径**：确保提供的文件路径是有效的，图片和媒体文件需要存在于指定路径。

4. **坐标系统**：PptxGenJS 使用英寸作为单位，坐标原点在左上角。

5. **限制**：由于 PptxGenJS 的限制，某些功能（如删除幻灯片、读取现有文件内容）可能不完全支持。

## 配置示例

### STDIO 模式配置
在你的 MCP 客户端配置中添加：

```json
{
  "mcpServers": {
    "pptxgenjs": {
      "command": "node",
      "args": ["/path/to/your/pptxgenjs-mcp/dist/index.js"],
      "cwd": "/path/to/your/pptxgenjs-mcp",
      "env": {}
    }
  }
}
```

### SSE 模式配置
在你的 MCP 客户端配置中添加：

```json
{
  "mcpServers": {
    "pptxgenjs": {
      "command": "node",
      "args": ["/path/to/your/pptxgenjs-mcp/dist/index.js", "--mode=sse", "--port=3000"],
      "cwd": "/path/to/your/pptxgenjs-mcp",
      "env": {}
    }
  }
}
```

或者直接通过 HTTP 连接到 `http://localhost:3000/sse`

## 依赖项

- `@modelcontextprotocol/sdk`: MCP SDK
- `pptxgenjs`: PowerPoint 生成库
- `typescript`: TypeScript 支持

## 许可证

MIT