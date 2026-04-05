---
name: "daily_ai_news"
description: "获取每日AI新闻资讯并生成飞书文档格式的md文件。当用户说'获取今日AI资讯'或类似请求时触发此skill。"
---

# Daily AI News

## 功能描述

此 skill 用于自动获取每日AI新闻资讯，执行Python脚本爬取AI行业新闻，Agent对文章内容进行阅读理解和概括，将结果保存为JSON文件，并生成飞书文档格式的Markdown文件。

## 触发条件

当用户输入以下或类似表达时触发：
- "获取今日AI资讯"
- "今天有什么AI新闻"
- "AI每日资讯"
- "获取AI新闻"

## 执行流程

### Step 1: 执行 Python 脚本获取原始数据

执行位于 `libs/skills/daily_ai_news/daily_ai_news.py` 的Python脚本获取AI新闻原始数据。

**命令格式**：
```bash
source .venv/bin/activate
python libs/skills/daily_ai_news/daily_ai_news.py --output <json文件路径>
```

**参数说明**：
- `--output` 或 `-o`: 必选参数，指定输出的JSON文件路径

**示例**：
```bash
python libs/skills/daily_ai_news/daily_ai_news.py --output ./output/ai_news_raw.json
```

**Python脚本功能**：
- 爬取多个数据源（Anthropic Engineering、Research、News等）
- 只获取今日发布的文章
- 每篇文章包含：标题、URL、来源、类型、日期、正文内容(content)
- 使用 BeautifulSoup 进行HTML解析

### Step 2: Agent 阅读理解和概括

读取 Step 1 生成的 JSON 文件，对每篇文章的 `content` 进行阅读理解和概括。

**概括要求**：
- 提取文章核心观点和关键信息
- 总结文章的主要内容和结论
- 保持客观准确，不添加个人见解
- 概括长度控制在 100-200 字

**输出格式**：
将概括结果添加到每篇文章的 `summary` 字段中：

```json
{
  "date": "2026-03-31",
  "total_count": 3,
  "articles": [
    {
      "title": "文章标题",
      "url": "https://www.anthropic.com/...",
      "source": "Anthropic Engineering",
      "type": "engineering",
      "date": "Mar 31, 2026",
      "content": "文章原始正文内容...",
      "summary": "Agent生成的文章概括..."
    }
  ]
}
```

### Step 3: 生成飞书文档格式的 Markdown 文件

根据处理后的JSON数据，生成飞书文档格式的Markdown文件，保存到与JSON文件相同的目录下，文件名为 `ai_news_${date}.md`。

**Markdown 文件格式示例**：

```markdown
# 📰 每日AI资讯 - 2026年3月31日

> 数据来源：Anthropic | 生成时间：2026-03-31

---

## 热门资讯

### 1. 文章标题
- **来源**：Anthropic Engineering
- **发布时间**：Mar 31, 2026
- **类型**：Engineering
- **摘要**：Agent生成的文章概括内容...

[阅读原文](https://www.anthropic.com/...)

---

## 更多资讯

### 2. 文章标题
- **来源**：Anthropic News
- **发布时间**：Mar 31, 2026
- **类型**：news
- **摘要**：Agent生成的文章概括内容...

[阅读原文](https://www.anthropic.com/...)
```

## 数据源说明

当前支持的数据源：

### Anthropic
- **Engineering**: https://www.anthropic.com/engineering
  - 工程实践文章
  - 技术实现细节
- **Research**: https://www.anthropic.com/research
  - 研究论文和出版物
  - AI安全和对齐研究
- **News**: https://www.anthropic.com/news
  - 公司新闻和公告
  - 产品更新

### 预留数据源
- **OpenAI**: 待实现
- **其他AI公司**: 可扩展

## 数据结构

### 原始JSON结构（Step 1输出）

```json
{
  "date": "2026-03-31",
  "total_count": 3,
  "articles": [
    {
      "title": "文章标题",
      "url": "https://www.anthropic.com/...",
      "source": "Anthropic Engineering",
      "type": "engineering",
      "date": "Mar 31, 2026",
      "content": "文章原始正文内容..."
    }
  ]
}
```

### 处理后JSON结构（Step 2输出）

```json
{
  "date": "2026-03-31",
  "total_count": 3,
  "articles": [
    {
      "title": "文章标题",
      "url": "https://www.anthropic.com/...",
      "source": "Anthropic Engineering",
      "type": "engineering",
      "date": "Mar 31, 2026",
      "content": "文章原始正文内容...",
      "summary": "Agent生成的文章概括..."
    }
  ]
}
```

## 注意事项

1. **Python脚本依赖**：确保已安装 `beautifulsoup4` 和 `requests`
2. **虚拟环境**：执行前确保 `.venv` 虚拟环境已激活
3. **网络连接**：脚本需要访问 Anthropic 官网，确保网络畅通
4. **日期匹配**：脚本只获取当天发布的文章（根据系统时间）
5. **Agent概括**：Step 2 需要Agent对每篇文章进行阅读理解和概括
6. **输出目录**：确保输出目录存在或脚本会自动创建
