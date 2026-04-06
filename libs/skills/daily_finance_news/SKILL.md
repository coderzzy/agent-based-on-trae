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

### Step 1: 使用 browser-operator 获取列表页 HTML

使用 browser-operator skill 访问以下数据源，获取列表页 HTML 并保存到本地文件。

```bash
mkdir -p ./output_finance/html
mkdir -p ./output_finance/stage1
mkdir -p ./output_finance/stage2
mkdir -p ./output_finance/articles
```

#### Twitter 数据源

**X (Twitter) - Matt Levine (彭博专栏作家，以幽默风格解读金融新闻著称):**
- 访问: https://x.com/matt_levine
- 保存: `./output_finance/html/twitter_matt_levine.html`

**X (Twitter) - IBD Investors (Investor's Business Daily，提供股市分析和投资建议):**
- 访问: https://x.com/IBDinvestors
- 保存: `./output_finance/html/twitter_ibd_investors.html`

**X (Twitter) - Peter L Brandt (资深期货交易员，技术分析专家):**
- 访问: https://x.com/PeterLBrandt
- 保存: `./output_finance/html/twitter_peter_brandt.html`

#### 预留：其他金融新闻网站（未来扩展）

**Bloomberg Markets:**
- 访问: https://www.bloomberg.com/markets
- 保存: `./output_finance/html/bloomberg_markets.html`

**WSJ Markets:**
- 访问: https://www.wsj.com/market-data
- 保存: `./output_finance/html/wsj_markets.html`

### Step 2: Stage 1 - 解析列表页，提取今日内容

每个数据源使用独立的 Stage 1 脚本解析列表页 HTML，提取过去24小时内发布的内容。

```bash
source .venv/bin/activate

# ==================== Twitter 数据源 ====================

# Matt Levine
python .trae/skills/daily_finance_news/scripts/twitter_stage1.py \
  --html ./output_finance/html/twitter_matt_levine.html \
  --output ./output_finance/stage1/twitter_matt_levine.json \
  --username matt_levine \
  --display-name "Matt Levine"

# IBD Investors
python .trae/skills/daily_finance_news/scripts/twitter_stage1.py \
  --html ./output_finance/html/twitter_ibd_investors.html \
  --output ./output_finance/stage1/twitter_ibd_investors.json \
  --username IBDinvestors \
  --display-name "IBD Investors"

# Peter L Brandt
python .trae/skills/daily_finance_news/scripts/twitter_stage1.py \
  --html ./output_finance/html/twitter_peter_brandt.html \
  --output ./output_finance/stage1/twitter_peter_brandt.json \
  --username PeterLBrandt \
  --display-name "Peter L Brandt"

# ==================== 预留：其他数据源（未来扩展） ====================

# Bloomberg Stage 1（预留）
# python .trae/skills/daily_finance_news/scripts/bloomberg_stage1.py \
#   --html ./output_finance/html/bloomberg_markets.html \
#   --output ./output_finance/stage1/bloomberg.json

# WSJ Stage 1（预留）
# python .trae/skills/daily_finance_news/scripts/wsj_stage1.py \
#   --html ./output_finance/html/wsj_markets.html \
#   --output ./output_finance/stage1/wsj.json
```

**Stage 1 输出示例** (`./output_finance/stage1/twitter_matt_levine.json`):
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
# 保存到 ./output_finance/articles/https_www_bloomberg_com_news_articles_xxx.html
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
cp ./output_finance/stage1/twitter_matt_levine.json ./output_finance/stage2/twitter_matt_levine.json
cp ./output_finance/stage1/twitter_ibd_investors.json ./output_finance/stage2/twitter_ibd_investors.json
cp ./output_finance/stage1/twitter_peter_brandt.json ./output_finance/stage2/twitter_peter_brandt.json

# ==================== 预留：新闻网站数据源（未来扩展） ====================
# Bloomberg Stage 2（预留）
# python .trae/skills/daily_finance_news/scripts/bloomberg_stage2.py \
#   --stage1 ./output_finance/stage1/bloomberg.json \
#   --articles-dir ./output_finance/articles \
#   --output ./output_finance/stage2/bloomberg.json

# WSJ Stage 2（预留）
# python .trae/skills/daily_finance_news/scripts/wsj_stage2.py \
#   --stage1 ./output_finance/stage1/wsj.json \
#   --articles-dir ./output_finance/articles \
#   --output ./output_finance/stage2/wsj.json
```

### Step 5: 合并所有结果

合并所有数据源的 Stage 2 结果，生成最终的 JSON 数据文件。

```bash
python .trae/skills/daily_finance_news/scripts/merge_results.py \
  --input-dir ./output_finance/stage2 \
  --output ./output_finance/finance_news_raw.json
```

**合并后输出示例** (`./output_finance/finance_news_raw.json`):
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

1. **原始数据**: `output_finance/finance_news_raw.json`
2. **Markdown报告**: `output_finance/finance_news_YYYY-MM-DD.md`

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
