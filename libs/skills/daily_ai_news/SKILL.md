---
name: "daily_ai_news"
description: "获取每日AI新闻资讯并生成飞书文档格式的md文件。当用户说'获取今日AI资讯'或类似请求时触发此skill。"
---

# Daily AI News

## 功能描述

此 skill 用于自动获取每日AI新闻资讯（过去24小时内），通过 browser-operator 获取网页 HTML 数据，各数据源使用独立的 Python 脚本分阶段处理，Agent对文章内容进行阅读理解和概括，将结果保存为JSON文件，并生成飞书文档格式的Markdown文件。

## 触发条件

当用户输入以下或类似表达时触发：
- "获取今日AI资讯"
- "今天有什么AI新闻"
- "AI每日资讯"
- "获取AI新闻"

## 执行流程

### Step 1: 使用 browser-operator 获取列表页 HTML

使用 browser-operator skill 访问以下数据源，获取列表页 HTML 并保存到本地文件。

```bash
mkdir -p ./output/html/articles
```

**Anthropic Engineering:**
- 访问: https://www.anthropic.com/engineering
- 保存: `./output/html/anthropic_engineering.html`

**Anthropic Research:**
- 访问: https://www.anthropic.com/research
- 保存: `./output/html/anthropic_research.html`

**Anthropic News:**
- 访问: https://www.anthropic.com/news
- 保存: `./output/html/anthropic_news.html`

**X (Twitter) - Karpathy (前 Tesla AI 总监、OpenAI 联合创始人):**
- 访问: https://x.com/karpathy
- 保存: `./output/html/twitter_karpathy.html`

**X (Twitter) - Sam Altman (OpenAI CEO):**
- 访问: https://x.com/sama
- 保存: `./output/html/twitter_samaltman.html`

**X (Twitter) - Guillermo Rauch (Vercel CEO):**
- 访问: https://x.com/rauchg
- 保存: `./output/html/twitter_rauchg.html`

**X (Twitter) - Garry Tan (YC CEO):**
- 访问: https://x.com/garrytan
- 保存: `./output/html/twitter_garrytan.html`

**X (Twitter) - Amjad Masad (Replit CEO):**
- 访问: https://x.com/amasad
- 保存: `./output/html/twitter_amasad.html`

**X (Twitter) - Peter Yang (Roblox PM、AI 教程创作者):**
- 访问: https://x.com/petergyang
- 保存: `./output/html/twitter_peteryang.html`

**X (Twitter) - Zara Zhang (Builder、GitHub 13k+ stars):
- 访问: https://x.com/zarazhangrui
- 保存: `./output/html/twitter_zarazhang.html`

### Step 2: Stage 1 - 解析列表页，提取今日文章

每个数据源使用独立的 Stage 1 脚本解析列表页 HTML，提取今日发布的文章（标题、URL、日期）。

```bash
source .venv/bin/activate

# Engineering Stage 1
python .trae/skills/daily_ai_news/scripts/anthropic_engineering_stage1.py \
  --html ./output/html/anthropic_engineering.html \
  --output ./output/stage1/engineering.json

# Research Stage 1
python .trae/skills/daily_ai_news/scripts/anthropic_research_stage1.py \
  --html ./output/html/anthropic_research.html \
  --output ./output/stage1/research.json

# News Stage 1
python .trae/skills/daily_ai_news/scripts/anthropic_news_stage1.py \
  --html ./output/html/anthropic_news.html \
  --output ./output/stage1/news.json

# Twitter Stage 1 (推文内容已在列表页获取完整)
# 使用通用脚本处理所有Twitter账号

# Karpathy
python .trae/skills/daily_ai_news/scripts/twitter_stage1.py \
  --html ./output/html/twitter_karpathy.html \
  --output ./output/stage1/twitter_karpathy.json \
  --username karpathy \
  --display-name "Andrej Karpathy"

# Sam Altman
python .trae/skills/daily_ai_news/scripts/twitter_stage1.py \
  --html ./output/html/twitter_samaltman.html \
  --output ./output/stage1/twitter_samaltman.json \
  --username sama \
  --display-name "Sam Altman"

# Guillermo Rauch
python .trae/skills/daily_ai_news/scripts/twitter_stage1.py \
  --html ./output/html/twitter_rauchg.html \
  --output ./output/stage1/twitter_rauchg.json \
  --username rauchg \
  --display-name "Guillermo Rauch"

# Garry Tan
python .trae/skills/daily_ai_news/scripts/twitter_stage1.py \
  --html ./output/html/twitter_garrytan.html \
  --output ./output/stage1/twitter_garrytan.json \
  --username garrytan \
  --display-name "Garry Tan"

# Amjad Masad
python .trae/skills/daily_ai_news/scripts/twitter_stage1.py \
  --html ./output/html/twitter_amasad.html \
  --output ./output/stage1/twitter_amasad.json \
  --username amasad \
  --display-name "Amjad Masad"

# Peter Yang
python .trae/skills/daily_ai_news/scripts/twitter_stage1.py \
  --html ./output/html/twitter_peteryang.html \
  --output ./output/stage1/twitter_peteryang.json \
  --username petergyang \
  --display-name "Peter Yang"

# Zara Zhang
python .trae/skills/daily_ai_news/scripts/twitter_stage1.py \
  --html ./output/html/twitter_zarazhang.html \
  --output ./output/stage1/twitter_zarazhang.json \
  --username zarazhangrui \
  --display-name "Zara Zhang"
```

**Stage 1 输出示例** (`./output/stage1/engineering.json`):
```json
{
  "source": "engineering",
  "date": "2026-04-06",
  "today_count": 2,
  "articles": [
    {
      "title": "文章标题",
      "url": "https://www.anthropic.com/engineering/...",
      "source": "Anthropic Engineering",
      "type": "engineering",
      "date": "Apr 6, 2026",
      "content": ""
    }
  ]
}
```

### Step 3: 根据 Stage 1 结果，获取详情页 HTML

读取 Stage 1 的输出，如果有今日文章，使用 browser-operator 获取详情页 HTML。

```bash
# 根据 stage1 结果，获取每篇文章的详情页
# 例如，如果 engineering.json 中有今日文章，则：
# 访问 https://www.anthropic.com/engineering/xxx
# 保存到 ./output/html/articles/https_www_anthropic_com_engineering_xxx.html
```

**详情页文件名生成规则**:
- 将 URL 中的非字母数字字符替换为下划线
- 例如: `https://www.anthropic.com/engineering/building-efficient-agents`
- 保存为: `https_www_anthropic_com_engineering_building_efficient_agents.html`

### Step 4: Stage 2 - 解析详情页，获取文章内容

对需要详情页的数据源（Engineering、Research、News），执行 Stage 2 脚本解析详情页 HTML。

```bash
# Engineering Stage 2
python .trae/skills/daily_ai_news/scripts/anthropic_engineering_stage2.py \
  --stage1 ./output/stage1/engineering.json \
  --articles-dir ./output/html/articles \
  --output ./output/stage2/engineering.json

# Research Stage 2
python .trae/skills/daily_ai_news/scripts/anthropic_research_stage2.py \
  --stage1 ./output/stage1/research.json \
  --articles-dir ./output/html/articles \
  --output ./output/stage2/research.json

# News Stage 2
python .trae/skills/daily_ai_news/scripts/anthropic_news_stage2.py \
  --stage1 ./output/stage1/news.json \
  --articles-dir ./output/html/articles \
  --output ./output/stage2/news.json

# Twitter 不需要 Stage 2（内容已在 Stage 1 获取完整）
# 直接复制所有 Twitter stage1 结果到 stage2
cp ./output/stage1/twitter_karpathy.json ./output/stage2/twitter_karpathy.json
cp ./output/stage1/twitter_samaltman.json ./output/stage2/twitter_samaltman.json
cp ./output/stage1/twitter_rauchg.json ./output/stage2/twitter_rauchg.json
cp ./output/stage1/twitter_garrytan.json ./output/stage2/twitter_garrytan.json
cp ./output/stage1/twitter_amasad.json ./output/stage2/twitter_amasad.json
cp ./output/stage1/twitter_peteryang.json ./output/stage2/twitter_peteryang.json
cp ./output/stage1/twitter_zarazhang.json ./output/stage2/twitter_zarazhang.json
```

### Step 5: 合并所有结果

合并所有数据源的 Stage 2 结果，生成最终的 JSON 文件。

```bash
python scripts/merge_results.py \
  --input-dir ./output/stage2 \
  --output ./output/ai_news_raw.json
```

**最终输出** (`./output/ai_news_raw.json`):
```json
{
  "date": "2026-04-06",
  "total_count": 5,
  "articles": [
    {
      "title": "文章标题",
      "url": "https://www.anthropic.com/...",
      "source": "Anthropic Engineering",
      "type": "engineering",
      "date": "Apr 6, 2026",
      "content": "文章原始正文内容..."
    }
  ]
}
```

### Step 6: Agent 阅读理解和概括

读取 Step 5 生成的 JSON 文件，对每篇文章的 `content` 进行阅读理解和概括。

**概括要求**：
- 提取文章核心观点和关键信息
- 总结文章的主要内容和结论
- 保持客观准确，不添加个人见解
- 概括长度控制在 100-200 字

**输出格式**：
将概括结果添加到每篇文章的 `summary` 字段中。

### Step 7: 生成飞书文档格式的 Markdown 文件

根据处理后的JSON数据，生成飞书文档格式的Markdown文件，保存到 `./output/ai_news_YYYY-MM-DD.md`。

## 数据源处理说明

| 数据源 | Stage 1 | Stage 2 | 日期判断逻辑 |
|--------|---------|---------|-------------|
| Engineering | 从列表页提取今日文章 | 从详情页获取内容 | 从 article 文本提取 "Mar 25, 2026" |
| Research | 从列表页提取今日文章 | 从详情页获取内容 | 从链接文本提取 "Mar 25, 2026" |
| News | 从列表页提取今日文章 | 从详情页获取内容 | 从链接文本提取 "Mar 25, 2026" |
| Twitter - Karpathy | 从列表页提取今日推文 | 不需要（内容已完整） | 使用 ISO datetime 属性 |
| Twitter - Sam Altman | 从列表页提取今日推文 | 不需要（内容已完整） | 使用 ISO datetime 属性 |
| Twitter - Guillermo Rauch | 从列表页提取今日推文 | 不需要（内容已完整） | 使用 ISO datetime 属性 |
| Twitter - Garry Tan | 从列表页提取今日推文 | 不需要（内容已完整） | 使用 ISO datetime 属性 |
| Twitter - Amjad Masad | 从列表页提取今日推文 | 不需要（内容已完整） | 使用 ISO datetime 属性 |
| Twitter - Peter Yang | 从列表页提取今日推文 | 不需要（内容已完整） | 使用 ISO datetime 属性 |
| Twitter - Zara Zhang | 从列表页提取今日推文 | 不需要（内容已完整） | 使用 ISO datetime 属性 |
