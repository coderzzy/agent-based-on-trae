# Agent Based On TRAE | 基于 TRAE 的 Agent 任务
```
思路：
1、使用 TRAE 里 LLM 的 Agent 能力
2、配置好通用的 rules、MCP、Skills
3、完成主要基于代码能力的各种 Agent 任务（如数据分析、图文视频剪辑、新闻资讯等）

使用：
1、在 TRAE 里打开项目
2、使用 uv 配置基础 python 环境，并设置 TRAE 的开发环境为 .venv/bin/python
3、把 输入文件 放到 input/ 目录下，指定输出到 output_*/ 目录下
4、TRAE 调整到 Build / SOLO 模式，输入 prompt 指令
5、等待 TRAE 完成，生成产物
6、让 Agent 总结本次任务为 prompt_templates / skills 等，放到libs目录下
```

## 环境与启动

### python环境
```
# 安装uv，方法一
curl -Ls https://astral.sh/uv/install.sh | bash
uv --version

# 创建虚拟环境
uv venv         
# 激活虚拟环境
source .venv/bin/activate  
# 安装依赖
uv pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 运行脚本
python xxx.py

# uv 依赖 跟 requirements.txt 保持一致
uv pip list --format=freeze > requirements.txt
```

### Node 环境
```
# 安装 nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash

# 创建 node 环境
nvm install 23
# 激活 node 环境
nvm use 23
# 安装依赖
npm install
# 启动服务
npm run dev
```


## 案例

### 每日AI资讯

自动获取每日AI新闻资讯（Anthropic Engineering/Research/News + Twitter AI KOL），生成飞书文档格式的 Markdown 报告。

#### 前置依赖

1. **browser-operator** - 用于使用本地浏览器进行网页信息获取 Skill
   - 仓库：https://github.com/coderzzy/agent-browser-operator-skill
   - 安装 Chrome 浏览器插件
   - 启动本地服务：
     ```bash
     cd server && npm run dev
     ```
   - Chrome 浏览器插件，连接服务

2. **daily_ai_news** - AI资讯获取 Skill
   ```bash
   rsync -av --delete libs/skills/daily_ai_news/ .trae/skills/daily_ai_news/
   ```

#### 使用方式

在 TRAE 中输入指令：

```
获取今日AI资讯
```

#### 输出

- Markdown 报告：`output/ai_news_YYYY-MM-DD.md`
- 原始数据：`output/ai_news_raw.json`


### 每日金融资讯

自动获取每日金融新闻资讯（Twitter 金融 KOL），生成飞书文档格式的 Markdown 报告。

#### 前置依赖

1. **browser-operator** - 用于使用本地浏览器进行网页信息获取 Skill
   - 仓库：https://github.com/coderzzy/agent-browser-operator-skill
   - 安装 Chrome 浏览器插件
   - 启动本地服务：
     ```bash
     cd server && npm run dev
     ```
   - Chrome 浏览器插件，连接服务

2. **daily_finance_news** - 金融资讯获取 Skill
   ```bash
   rsync -av --delete libs/skills/daily_finance_news/ .trae/skills/daily_finance_news/
   ```

#### 使用方式

在 TRAE 中输入指令：

```
获取今日金融资讯
```

#### 输出

- Markdown 报告：`output_finance/finance_news_YYYY-MM-DD.md`
- 原始数据：`output_finance/finance_news_raw.json`


## TODO:
- skills里的python脚本，直接用 scripts/xxx 会报错找不到，暂时先使用 .trae/skills/xxx
