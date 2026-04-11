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

### Step 8: 生成小红书格式的 HTML 报告

根据处理后的JSON数据，生成小红书格式的HTML报告，保存到 `./output/xiaohongshu_YYYY-MM-DD.html`。

**HTML报告包含三个部分：**

1. **小红书标题**
   - 生成吸引眼球的标题（20字以内）
   - 标题格式：`🔥 24小时内AI圈发生了什么 | YYYY-MM-DD`

2. **图片部分（重要设计规范）**
   
   **设计原则：**
   - 使用 **HTML/CSS** 设计图片样式，**禁止使用 Canvas**
   - Canvas 难以控制排版和审美，HTML/CSS 更灵活、更美观
   - 图片通过浏览器截图获取（Cmd+Shift+4 或浏览器开发者工具）
   
   **图片主题：**
   - 主题统一为 **"24小时内AI圈发生了什么"**
   - 不要只关注Twitter内容，要整合所有渠道（Anthropic Engineering/Research/News、Twitter等）
   - 根据资讯内容提炼主题，而不是根据来源渠道
   
   **图片数量和内容组织：**
   - 不要每条资讯一张图，需要**根据主题合并**
   - 精选重要、有价值的资讯进行展示
   - 相同主题的多个资讯可以合并到一张图中
   - 通常生成 3-4 张图：1张封面 + 2-3张内容图
   
   **图片来源适配：**
   - **Anthropic 文章**：显示文章标题、来源（Anthropic Engineering/Research/News）、核心观点摘要、原文链接
   - **Twitter 推文**：显示作者名、Twitter账号、原文引用、原文链接
   - **混合展示**：同一主题下可以同时展示Anthropic文章和Twitter观点
   
   **图片内容要求：**
   - **必须包含完整来源信息**：根据来源类型显示（公司博客/作者名 + 账号/链接）
   - **必须包含原文引用**：保留英文原文，不要只写中文概括
   - **必须包含详细内容**：不只是简短标题，要有具体信息
   - 使用渐变背景、卡片式布局、引用框等设计元素
   - 配色要符合小红书审美：深色科技风、渐变色彩、高对比度
   
   **图片结构示例：**
   ```html
   <!-- 封面 -->
   <div class="xhs-image cover-bg">
     <div class="cover-title">24小时内<br>AI圈发生了什么</div>
     <div class="cover-date">2026.04.10</div>
     <div class="cover-highlights">
       <div class="cover-item">中国AI占领硅谷</div>
       <div class="cover-item">Replit助力创业</div>
       <div class="cover-item">Waymo澄清事件</div>
     </div>
   </div>
   
   <!-- 内容图 - 混合来源示例 -->
   <div class="xhs-image news-bg-1">
     <div class="news-header">
       <div class="news-title">🇨🇳 中国开源AI占领硅谷</div>
     </div>
     <!-- Twitter来源 -->
     <div class="news-source">
       <div class="source-badge">Twitter</div>
       <div class="source-info">
         <div class="source-name">Peter Yang</div>
         <div class="source-handle">@petergyang</div>
       </div>
     </div>
     <div class="quote-box">
       <div class="quote-text">"Silicon Valley is quietly running on Chinese open source AI models..."</div>
     </div>
     <!-- 详细内容列表 -->
     <div class="news-footer">
       <div class="news-link">🔗 x.com/...</div>
     </div>
   </div>
   
   <!-- 内容图 - Anthropic文章示例 -->
   <div class="xhs-image news-bg-2">
     <div class="news-header">
       <div class="news-title">🤖 Claude新功能发布</div>
     </div>
     <div class="news-source">
       <div class="source-badge">Anthropic</div>
       <div class="source-info">
         <div class="source-name">Anthropic Engineering</div>
       </div>
     </div>
     <div class="article-summary">
       核心观点摘要...
     </div>
     <div class="news-footer">
       <div class="news-link">🔗 anthropic.com/...</div>
     </div>
   </div>
   ```

3. **文案及Tag**
   - **文案**：从当日文章中精选重要资讯，包含完整来源和原文引用
   - **格式示例**：
     ```
     📌 24小时内AI圈热点：
     
     1️⃣ [主题标题]
     [来源]：Anthropic Engineering / @作者
     [英文原文/核心观点]
     [中文解读]
     🔗 [原文链接]
     
     2️⃣ [主题标题]
     [来源]：Twitter @作者
     [英文原文引用]
     [中文解读]
     🔗 [原文链接]
     
     ...
     
     💡 关注我每天追踪AI圈最新动态
     ```
   - **Tag**：添加15-20个相关标签，格式为 `#标签名`

**图片尺寸规范：**
- 小红书标准图片尺寸为 **3:4 比例**
- 推荐尺寸：**540×720px** 或 **1080×1440px**
- 尺寸过大（如1080×1440）可能导致浏览器需要缩放才能完整截图
- 尺寸过小会影响文字清晰度
- **最佳实践：使用 540×720px，无需缩放即可直接截图**

**HTML/CSS 设计最佳实践：**

1. **减少留白，内容紧凑**
   - 适当减小 padding 和 margin
   - 内容区域要充实，避免大片空白
   - 使用 `flex: 1` 让内容区自适应填充剩余空间

2. **文案排版**
   - 使用 `white-space: pre-line` 保留换行格式
   - 文案内容直接放在 `<div>` 中，使用实际换行符而非 `<br>`
   - 段落间距通过 line-height 控制

3. **字体大小适配**
   - 标题：36-52px
   - 正文：13-16px
   - 小字（链接、时间）：11-13px
   - 根据图片尺寸等比例缩放

4. **视觉层次**
   - 使用渐变背景增加质感
   - 卡片使用半透明毛玻璃效果（`backdrop-filter: blur`）
   - 重点内容使用高亮色（金色 #ffd700、青色 #00d4ff）

**常见设计错误（避免）：**
1. ❌ 使用 Canvas 绘制图片（难以控制审美）
2. ❌ 每条资讯一张图（应该按主题合并）
3. ❌ 图片内容过于简略（必须包含来源、原文/摘要、链接）
4. ❌ 只写中文概括（必须保留英文原文或核心观点）
5. ❌ 配色单调或不符合小红书风格
6. ❌ 只展示Twitter内容（要整合所有渠道）
7. ❌ 标题不统一（统一使用"24小时内AI圈发生了什么"）
8. ❌ 图片尺寸过大导致需要缩放才能截图
9. ❌ 留白过多，内容稀疏
10. ❌ 文案排版错乱（换行不生效）

**输出文件：**
- 文件路径：`./output/xiaohongshu_YYYY-MM-DD.html`
- 包含完整的HTML和CSS样式代码
- 可直接在浏览器中打开，截图保存为图片

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
