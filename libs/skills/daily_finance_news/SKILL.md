---
name: "daily_finance_news"
description: "获取每日金融新闻资讯并生成飞书文档格式的md文件。当用户说'获取今日金融资讯'或类似请求时触发此skill。"
---

# Daily Finance News

## 功能描述

此 skill 用于自动获取每日金融新闻资讯（过去24小时内），通过 browser-operator 获取金融数据源的 HTML 数据，提取内容后由 Agent 进行阅读理解和概括，最终生成飞书文档格式的 Markdown 报告。

**支持的数据源类型**：
- **Twitter 金融 KOL**（当前已实现）
- **金融新闻网站**（预留扩展：如 Bloomberg、WSJ、财新等）
- **财经数据平台**（预留扩展：如 Yahoo Finance、东方财富等）

## 触发条件

当用户输入以下或类似表达时触发：
- "获取今日金融资讯"
- "今天有什么金融新闻"
- "金融每日资讯"
- "获取金融新闻"
- "今日股市资讯"

## 执行流程

> **重要提示**：本 Skill 已提供完整的 Python 脚本，位于 `scripts/` 目录下。**严禁新建脚本**，请直接使用以下已有脚本：
> - `twitter_stage1.py`
> - `merge_results.py`
> - `common.py` (通用工具函数)

### Step 1: 使用 browser-operator 获取列表页 HTML

使用 browser-operator skill 访问以下数据源，获取列表页 HTML 并保存到本地文件。

```bash
# 设置输出目录（带时间戳）
OUTPUT_DIR="./output_finance_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$OUTPUT_DIR/html"
mkdir -p "$OUTPUT_DIR/stage1"
mkdir -p "$OUTPUT_DIR/stage2"
mkdir -p "$OUTPUT_DIR/articles"
```

#### Twitter 数据源

**X (Twitter) - Matt Levine (彭博专栏作家，以幽默风格解读金融新闻著称):**
- 访问: https://x.com/matt_levine
- 保存: `$OUTPUT_DIR/html/twitter_matt_levine.html`

**X (Twitter) - IBD Investors (Investor's Business Daily，提供股市分析和投资建议):**
- 访问: https://x.com/IBDinvestors
- 保存: `$OUTPUT_DIR/html/twitter_ibd_investors.html`

**X (Twitter) - Peter L Brandt (资深期货交易员，技术分析专家):**
- 访问: https://x.com/PeterLBrandt
- 保存: `$OUTPUT_DIR/html/twitter_peter_brandt.html`

**X (Twitter) - Nick Timiraos (华尔街日报首席经济记者，美联储报道权威):**
- 访问: https://x.com/NickTimiraos
- 保存: `$OUTPUT_DIR/html/twitter_nick_timiraos.html`

**X (Twitter) - Thomas Lee (Fundstrat Global Advisors 联合创始人，华尔街策略师):**
- 访问: https://x.com/fundstrat
- 保存: `$OUTPUT_DIR/html/twitter_thomas_lee.html`

#### 预留：其他金融新闻网站（未来扩展）

**Bloomberg Markets:**
- 访问: https://www.bloomberg.com/markets
- 保存: `$OUTPUT_DIR/html/bloomberg_markets.html`

**WSJ Markets:**
- 访问: https://www.wsj.com/market-data
- 保存: `$OUTPUT_DIR/html/wsj_markets.html`

### Step 2: Stage 1 - 解析列表页，提取今日内容

每个数据源使用独立的 Stage 1 脚本解析列表页 HTML，提取过去24小时内发布的内容。

```bash
source .venv/bin/activate

# ==================== Twitter 数据源 ====================

# Matt Levine
python scripts/twitter_stage1.py \
  --html "$OUTPUT_DIR/html/twitter_matt_levine.html" \
  --output "$OUTPUT_DIR/stage1/twitter_matt_levine.json" \
  --username matt_levine \
  --display-name "Matt Levine"

# IBD Investors
python scripts/twitter_stage1.py \
  --html "$OUTPUT_DIR/html/twitter_ibd_investors.html" \
  --output "$OUTPUT_DIR/stage1/twitter_ibd_investors.json" \
  --username IBDinvestors \
  --display-name "IBD Investors"

# Peter L Brandt
python scripts/twitter_stage1.py \
  --html "$OUTPUT_DIR/html/twitter_peter_brandt.html" \
  --output "$OUTPUT_DIR/stage1/twitter_peter_brandt.json" \
  --username PeterLBrandt \
  --display-name "Peter L Brandt"

# Nick Timiraos
python scripts/twitter_stage1.py \
  --html "$OUTPUT_DIR/html/twitter_nick_timiraos.html" \
  --output "$OUTPUT_DIR/stage1/twitter_nick_timiraos.json" \
  --username NickTimiraos \
  --display-name "Nick Timiraos"

# Thomas Lee
python scripts/twitter_stage1.py \
  --html "$OUTPUT_DIR/html/twitter_thomas_lee.html" \
  --output "$OUTPUT_DIR/stage1/twitter_thomas_lee.json" \
  --username fundstrat \
  --display-name "Thomas Lee"

# ==================== 预留：其他数据源（未来扩展） ====================

# Bloomberg Stage 1（预留）
# python scripts/bloomberg_stage1.py \
#   --html "$OUTPUT_DIR/html/bloomberg_markets.html" \
#   --output "$OUTPUT_DIR/stage1/bloomberg.json"

# WSJ Stage 1（预留）
# python scripts/wsj_stage1.py \
#   --html "$OUTPUT_DIR/html/wsj_markets.html" \
#   --output "$OUTPUT_DIR/stage1/wsj.json"
```

**Stage 1 输出示例** (`$OUTPUT_DIR/stage1/twitter_matt_levine.json`):
```json
{
  "source": "twitter",
  "username": "matt_levine",
  "display_name": "Matt Levine",
  "date": "2026-04-07",
  "today_count": 3,
  "articles": [
    {
      "title": "推文内容摘要...",
      "url": "https://x.com/matt_levine/status/...",
      "source": "Matt Levine (Twitter)",
      "type": "twitter",
      "date": "Apr 7, 2026",
      "content": "完整推文内容..."
    }
  ]
}
```

### Step 3: 根据 Stage 1 结果，获取详情页 HTML（如需要）

对于需要详情页的数据源（如新闻网站），读取 Stage 1 的输出，如果有今日文章，使用 browser-operator 获取详情页 HTML。

```bash
# ==================== Twitter 数据源 ====================
# Twitter 推文内容已在 Stage 1 获取完整，不需要详情页

# ==================== 预留：新闻网站数据源（未来扩展） ====================
# 根据 stage1 结果，获取每篇文章的详情页
# 例如，如果 bloomberg.json 中有今日文章，则：
# 访问 https://www.bloomberg.com/news/articles/xxx
# 保存到 $OUTPUT_DIR/articles/https_www_bloomberg_com_news_articles_xxx.html
```

**详情页文件名生成规则**:
- 将 URL 中的非字母数字字符替换为下划线
- 例如: `https://www.bloomberg.com/news/articles/xxx`
- 保存为: `https_www_bloomberg_com_news_articles_xxx.html`

### Step 4: Stage 2 - 解析详情页，获取完整内容

对需要详情页的数据源，执行 Stage 2 脚本解析详情页 HTML。

```bash
# ==================== Twitter 数据源 ====================
# Twitter 不需要 Stage 2（内容已在 Stage 1 获取完整）
# 直接复制所有 Twitter stage1 结果到 stage2
cp "$OUTPUT_DIR/stage1/twitter_matt_levine.json" "$OUTPUT_DIR/stage2/twitter_matt_levine.json"
cp "$OUTPUT_DIR/stage1/twitter_ibd_investors.json" "$OUTPUT_DIR/stage2/twitter_ibd_investors.json"
cp "$OUTPUT_DIR/stage1/twitter_peter_brandt.json" "$OUTPUT_DIR/stage2/twitter_peter_brandt.json"
cp "$OUTPUT_DIR/stage1/twitter_nick_timiraos.json" "$OUTPUT_DIR/stage2/twitter_nick_timiraos.json"
cp "$OUTPUT_DIR/stage1/twitter_thomas_lee.json" "$OUTPUT_DIR/stage2/twitter_thomas_lee.json"

# ==================== 预留：新闻网站数据源（未来扩展） ====================
# Bloomberg Stage 2（预留）
# python scripts/bloomberg_stage2.py \
#   --stage1 "$OUTPUT_DIR/stage1/bloomberg.json" \
#   --articles-dir "$OUTPUT_DIR/articles" \
#   --output "$OUTPUT_DIR/stage2/bloomberg.json"

# WSJ Stage 2（预留）
# python scripts/wsj_stage2.py \
#   --stage1 "$OUTPUT_DIR/stage1/wsj.json" \
#   --articles-dir "$OUTPUT_DIR/articles" \
#   --output "$OUTPUT_DIR/stage2/wsj.json"
```

### Step 5: 合并所有结果

合并所有数据源的 Stage 2 结果，生成最终的 JSON 数据文件。

```bash
python scripts/merge_results.py \
  --input-dir "$OUTPUT_DIR/stage2" \
  --output "$OUTPUT_DIR/finance_news_raw.json"
```

**合并后输出示例** (`$OUTPUT_DIR/finance_news_raw.json`):
```json
{
  "date": "2026-04-07",
  "total_count": 8,
  "sources": {
    "Matt Levine": {"count": 3, "username": "matt_levine", "source": "twitter"},
    "IBD Investors": {"count": 3, "username": "IBDinvestors", "source": "twitter"},
    "Peter L Brandt": {"count": 2, "username": "PeterLBrandt", "source": "twitter"}
  },
  "articles": [
    {
      "title": "推文内容摘要...",
      "url": "https://x.com/matt_levine/status/...",
      "source": "Matt Levine (Twitter)",
      "type": "twitter",
      "date": "Apr 7, 2026",
      "content": "完整推文内容..."
    }
  ]
}
```

### Step 6: Agent 阅读理解和概括

读取 Step 5 生成的 JSON 文件，对每条内容的 `content` 进行阅读理解和概括。

**概括要求**：
- 提取核心观点和关键信息
- 总结主要内容和结论
- 保持客观准确，不添加个人见解
- 对于推文：概括长度控制在 50-100 字
- 对于长文章：概括长度控制在 100-200 字

**输出格式**：
将概括结果添加到每条内容的 `summary` 字段中，生成新的 JSON 文件。

**示例**：
```json
{
  "title": "推文内容摘要...",
  "url": "https://x.com/matt_levine/status/...",
  "source": "Matt Levine (Twitter)",
  "type": "twitter",
  "date": "Apr 7, 2026",
  "content": "完整推文内容...",
  "summary": "Matt Levine 讨论了当前华尔街的并购趋势，指出..."
}
```

### Step 7: 生成飞书文档格式的 Markdown 报告

根据处理后的 JSON 数据，生成飞书文档格式的 Markdown 报告。

### Step 8: 生成小红书格式的 HTML 报告

根据处理后的 JSON 数据，生成小红书格式的 HTML 报告，保存到 `$OUTPUT_DIR/xiaohongshu_YYYY-MM-DD.html`。

**HTML报告包含三个部分：**

1. **小红书标题**
   - 生成吸引眼球的标题（20字以内）
   - 标题格式：`💰 24小时内金融圈发生了什么 | YYYY-MM-DD`

2. **图片部分（重要设计规范）**
   
   **设计原则：**
   - 使用 **HTML/CSS** 设计图片样式，**禁止使用 Canvas**
   - Canvas 难以控制排版和审美，HTML/CSS 更灵活、更美观
   - 图片通过浏览器截图获取（Cmd+Shift+4 或浏览器开发者工具）
   
   **图片主题：**
   - 主题统一为 **"24小时内金融圈发生了什么"**
   - 整合所有渠道（Twitter 金融 KOL、新闻网站等）
   - 根据资讯内容提炼主题，而不是根据来源渠道
   
   **图片数量和内容组织：**
   - 不要每条资讯一张图，需要**根据主题合并**
   - 精选重要、有价值的资讯进行展示
   - 相同主题的多个资讯可以合并到一张图中
   - 通常生成 3-4 张图：1张封面 + 2-3张内容图
   
   **图片来源适配：**
   - **Twitter 推文**：显示作者名、Twitter账号、原文引用、原文链接
   - **新闻网站文章**：显示文章标题、来源（Bloomberg/WSJ等）、核心观点摘要、原文链接
   - **混合展示**：同一主题下可以同时展示Twitter观点和新闻文章
   
   **图片内容要求：**
   - **必须包含完整来源信息**：根据来源类型显示（媒体名/作者名 + 账号/链接）
   - **必须包含原文引用**：保留英文原文，不要只写中文概括
   - **必须包含详细内容**：不只是简短标题，要有具体信息
   - 使用渐变背景、卡片式布局、引用框等设计元素
   - 配色要符合小红书审美：深色科技风、渐变色彩、高对比度
   
   **图片结构示例：**
   ```html
   <!-- 封面 -->
   <div class="xhs-image cover-bg">
     <div class="cover-title">24小时内<br>金融圈发生了什么</div>
     <div class="cover-date">2026.04.10</div>
     <div class="cover-highlights">
       <div class="cover-item">美联储利率决议</div>
       <div class="cover-item">科技股大涨</div>
       <div class="cover-item">并购交易活跃</div>
     </div>
   </div>
   
   <!-- 内容图 - Twitter来源示例 -->
   <div class="xhs-image news-bg-1">
     <div class="news-header">
       <div class="news-title">📈 美股科技股强势反弹</div>
     </div>
     <div class="news-source">
       <div class="source-badge">Twitter</div>
       <div class="source-info">
         <div class="source-name">Matt Levine</div>
         <div class="source-handle">@matt_levine</div>
       </div>
     </div>
     <div class="quote-box">
       <div class="quote-text">"The tech sector is seeing unprecedented consolidation..."</div>
     </div>
     <div class="news-footer">
       <div class="news-link">🔗 x.com/...</div>
     </div>
   </div>
   
   <!-- 内容图 - 新闻网站示例 -->
   <div class="xhs-image news-bg-2">
     <div class="news-header">
       <div class="news-title">🏦 美联储释放降息信号</div>
     </div>
     <div class="news-source">
       <div class="source-badge">Bloomberg</div>
       <div class="source-info">
         <div class="source-name">Bloomberg Markets</div>
       </div>
     </div>
     <div class="article-summary">
       核心观点摘要...
     </div>
     <div class="news-footer">
       <div class="news-link">🔗 bloomberg.com/...</div>
     </div>
   </div>
   ```

3. **文案及Tag**
   - **文案**：从当日资讯中精选重要内容，包含完整来源和原文引用
   - **格式示例**：
     ```
     📌 24小时内金融圈热点：
     
     1️⃣ [主题标题]
     [来源]：Bloomberg / @作者
     [英文原文/核心观点]
     [中文解读]
     🔗 [原文链接]
     
     2️⃣ [主题标题]
     [来源]：Twitter @作者
     [英文原文引用]
     [中文解读]
     🔗 [原文链接]
     
     ...
     
     💡 关注我每天追踪金融圈最新动态
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
7. ❌ 标题不统一（统一使用"24小时内金融圈发生了什么"）
8. ❌ 图片尺寸过大导致需要缩放才能截图
9. ❌ 留白过多，内容稀疏
10. ❌ 文案排版错乱（换行不生效）

**输出文件：**
- 文件路径：`$OUTPUT_DIR/xiaohongshu_YYYY-MM-DD.html`
- 包含完整的HTML和CSS样式代码
- 可直接在浏览器中打开，截图保存为图片

**报告格式示例** (`./output_finance/finance_news_2026-04-07.md`):

```markdown
# 每日金融资讯 - 2026年4月7日

## 📊 今日概览

- **日期**: 2026年4月7日
- **来源**: Twitter 金融 KOL
- **总条数**: 8 条

---

## � Matt Levine (彭博专栏作家)

> Matt Levine 是彭博社《Money Stuff》专栏作家，以幽默风趣的笔触解读复杂的金融新闻和华尔街动态。

### 推文 1
- **时间**: 2小时前
- **链接**: [查看原文](https://x.com/matt_levine/status/...)
- **内容摘要**: Matt Levine 讨论了当前华尔街的并购趋势，指出...
- **原文**: 完整推文内容...

### 推文 2
...

---

## 📈 IBD Investors (Investor's Business Daily)

> IBD 是知名的投资研究媒体，提供股市分析、股票筛选工具和投资教育内容。

...

---

## 📉 Peter L Brandt (资深交易员)

> Peter Brandt 是拥有40多年经验的资深期货交易员，专注于技术分析和图表模式交易。

...

---

*报告生成时间: 2026-04-07 XX:XX*
```

## 输出文件

1. **原始数据**: `$OUTPUT_DIR/finance_news_raw.json`
2. **Markdown报告**: `$OUTPUT_DIR/finance_news_YYYY-MM-DD.md`
3. **小红书HTML报告**: `$OUTPUT_DIR/xiaohongshu_YYYY-MM-DD.html`

## 数据源处理说明

| 数据源 | 类型 | Stage 1 | Stage 2 | Agent概括 | 日期判断逻辑 |
|--------|------|---------|---------|-----------|-------------|
| Matt Levine | Twitter | 从列表页提取推文 | 不需要（内容已完整） | 是 | ISO datetime 属性 |
| IBD Investors | Twitter | 从列表页提取推文 | 不需要（内容已完整） | 是 | ISO datetime 属性 |
| Peter L Brandt | Twitter | 从列表页提取推文 | 不需要（内容已完整） | 是 | ISO datetime 属性 |
| Bloomberg Markets | 新闻网站 | 预留 | 预留 | 预留 | 预留 |
| WSJ Markets | 新闻网站 | 预留 | 预留 | 预留 | 预留 |

## 数据来源详情

| 账号/网站 | 身份 | 内容特点 |
|----------|------|----------|
| [@matt_levine](https://x.com/matt_levine) | 彭博社《Money Stuff》专栏作家 | 幽默解读金融新闻、华尔街动态、并购交易 |
| [@IBDinvestors](https://x.com/IBDinvestors) | Investor's Business Daily 官方账号 | 股市分析、股票推荐、市场趋势、投资教育 |
| [@PeterLBrandt](https://x.com/PeterLBrandt) | 资深期货交易员、Factor LLC 创始人 | 技术分析、图表模式、加密货币、大宗商品 |

## 扩展指南

如需添加新的数据源，请按以下步骤操作：

1. **创建 Stage 1 脚本**: `scripts/{source_name}_stage1.py`
   - 解析列表页 HTML
   - 提取今日内容的标题、URL、日期

2. **创建 Stage 2 脚本**（如需要）: `scripts/{source_name}_stage2.py`
   - 解析详情页 HTML
   - 获取完整内容

3. **更新 SKILL.md**: 
   - 在 Step 1 添加数据源访问信息
   - 在 Step 2-4 添加执行命令
   - 在数据源处理说明表格中添加新行

4. **更新 merge_results.py**:
   - 添加新数据源的显示信息（如需要）
