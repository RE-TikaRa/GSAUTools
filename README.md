# GSAUTools

一个用于教育相关的工具集合，基于PyQt6开发。

## 功能特点

- MOOC考试分析器
- 现代化的Morandi风格界面
- 多语言支持 (中文、英文、日文)
- 模块化设计

## 项目结构

```
GSAUTool/
├── main.py              # 主程序入口
├── requirements.txt     # 依赖项
├── Style/              # 样式文件
├── Module/             # 功能模块
│   ├── MainGUI/       # 主界面相关
│   ├── MEA/           # MOOC考试分析器
│   └── Setting/       # 设置相关
├── OutPut/            # 输出目录
│   ├── Text/          # 文本输出
│   └── Word/          # Word文档输出
└── translations/      # 多语言支持
```

## 安装和运行

1. 克隆仓库：
```bash
git clone git@github.com:RE-TikaRa/GSAUTools.git
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 运行程序：
```bash
python main.py
```

## 开发

- 主分支：`main`
- 开发分支：`dev`
- 功能分支：`feature/*`
- 修复分支：`fix/*`

## 许可证

[MIT License](LICENSE)
