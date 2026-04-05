#!/usr/bin/env python3
"""
每日AI新闻获取脚本

功能：
1. 支持多数据源爬取（Anthropic、OpenAI等）
2. 统一的数据结构输出
3. 将结果保存为JSON文件到指定路径

使用方式：
    python daily_ai_news.py --output <json文件路径>

示例：
    python daily_ai_news.py --output ./output/ai_news.json
    python daily_ai_news.py -o ./output/ai_news.json
"""

import argparse
import json
import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import List


# ==================== 数据类型定义 ====================

@dataclass
class NewsArticle:
    """单篇文章的数据结构"""
    title: str
    url: str
    source: str
    type: str
    date: str = ""
    content: str = ""


@dataclass
class NewsData:
    """新闻数据的整体结构"""
    date: str
    total_count: int
    articles: List[NewsArticle]

    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            "date": self.date,
            "total_count": self.total_count,
            "articles": [asdict(article) for article in self.articles]
        }


# ==================== 通用工具函数 ====================

def fetch_page(url: str) -> str:
    """
    获取页面HTML内容

    Args:
        url: 页面URL

    Returns:
        str: 页面HTML内容
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"  获取页面失败 {url}: {e}")
        return ""


def is_today(date_str: str) -> bool:
    """
    检查日期是否为今天

    Args:
        date_str: 日期字符串，如 "Mar 25, 2026"

    Returns:
        bool: 是否为今天
    """
    today = datetime.now()

    try:
        date_obj = datetime.strptime(date_str, "%b %d, %Y")
        return date_obj.date() == today.date()
    except ValueError:
        pass

    try:
        date_obj = datetime.strptime(date_str, "%B %d, %Y")
        return date_obj.date() == today.date()
    except ValueError:
        pass

    return False


def clean_text(element) -> str:
    """从BeautifulSoup元素中提取纯文本"""
    if not element:
        return ""
    return element.get_text(strip=True)


# ==================== Anthropic 数据源 ====================

class AnthropicCrawler:
    """Anthropic官网信息爬取器"""

    URLS = {
        "engineering": "https://www.anthropic.com/engineering",
        "research": "https://www.anthropic.com/research",
        "news": "https://www.anthropic.com/news",
    }

    @classmethod
    def _fetch_article_content(cls, url: str) -> str:
        """
        获取Anthropic文章详情页内容

        这是Anthropic特有的文章解析逻辑

        Args:
            url: 文章URL

        Returns:
            str: 文章正文内容
        """
        html = fetch_page(url)
        if not html:
            return ""

        soup = BeautifulSoup(html, "html.parser")

        for selector in ["article", "main", ".content", ".post-content"]:
            content_elem = soup.select_one(selector)
            if content_elem:
                text = content_elem.get_text(separator=" ", strip=True)
                if len(text) > 1000:
                    return text[:5000]

        return ""

    @classmethod
    def crawl(cls) -> List[NewsArticle]:
        """
        爬取Anthropic所有内容

        Returns:
            List[NewsArticle]: 文章列表
        """
        all_articles = []

        print("  [Anthropic] 正在获取 Engineering 文章...")
        eng_articles = cls._crawl_engineering()
        print(f"    找到 {len(eng_articles)} 篇文章")
        all_articles.extend(eng_articles)

        print("  [Anthropic] 正在获取 Research Publications...")
        research_articles = cls._crawl_research()
        print(f"    找到 {len(research_articles)} 篇文章")
        all_articles.extend(research_articles)

        print("  [Anthropic] 正在获取 News...")
        news_articles = cls._crawl_news()
        print(f"    找到 {len(news_articles)} 篇文章")
        all_articles.extend(news_articles)

        return all_articles

    @classmethod
    def _crawl_engineering(cls) -> List[NewsArticle]:
        """爬取Engineering页面 - 只返回今日文章"""
        html = fetch_page(cls.URLS["engineering"])
        if not html:
            return []

        soup = BeautifulSoup(html, "html.parser")
        articles = []

        for article in soup.select("article"):
            link = article.select_one("a")
            if not link:
                continue

            href = link.get("href", "")
            if not href or not href.startswith("/engineering/"):
                continue

            title_elem = article.select_one("h1, h2, h3, h4, h5, h6")
            title = clean_text(title_elem)

            date_elem = article.select_one(".date, [class*='date']")
            date = clean_text(date_elem)

            if date and is_today(date):
                print(f"    发现今日文章: {title}")
                content = cls._fetch_article_content(f"https://www.anthropic.com{href}")

                articles.append(NewsArticle(
                    title=title,
                    url=f"https://www.anthropic.com{href}",
                    date=date,
                    source="Anthropic Engineering",
                    type="engineering",
                    content=content
                ))

        return articles

    @classmethod
    def _crawl_research(cls) -> List[NewsArticle]:
        """爬取Research页面Publications - 只返回今日文章"""
        html = fetch_page(cls.URLS["research"])
        if not html:
            return []

        soup = BeautifulSoup(html, "html.parser")
        articles = []

        # Publications列表使用time元素显示日期
        for time_elem in soup.select('time[class*="date"]'):
            date = time_elem.get_text(strip=True)

            # 向上找到包含整行的a标签
            row = time_elem.parent
            while row and row.name != 'a':
                row = row.parent

            if not row or row.name != 'a':
                continue

            href = row.get("href", "")
            if not href or not href.startswith("/research/"):
                continue

            # 查找标题
            title_elem = row.select_one('.headline-5, [class*="title"]')
            title = title_elem.get_text(strip=True) if title_elem else ""

            # 只处理今日文章
            if date and is_today(date):
                print(f"    发现今日文章: {title}")
                content = cls._fetch_article_content(f"https://www.anthropic.com{href}")

                articles.append(NewsArticle(
                    title=title,
                    url=f"https://www.anthropic.com{href}",
                    date=date,
                    source="Anthropic Research",
                    type="research",
                    content=content
                ))

        return articles

    @classmethod
    def _crawl_news(cls) -> List[NewsArticle]:
        """爬取News页面 - 只返回今日文章"""
        html = fetch_page(cls.URLS["news"])
        if not html:
            return []

        soup = BeautifulSoup(html, "html.parser")
        articles = []

        # News页面使用time元素显示日期，和Research页面类似
        for time_elem in soup.select('time[class*="date"]'):
            date = time_elem.get_text(strip=True)

            # 向上找到包含整行的a标签
            row = time_elem.parent
            while row and row.name != 'a':
                row = row.parent

            if not row or row.name != 'a':
                continue

            href = row.get("href", "")
            if not href or not href.startswith("/news/"):
                continue

            # 查找标题
            title_elem = row.select_one('.headline-5, [class*="title"]')
            title = title_elem.get_text(strip=True) if title_elem else ""

            # 只处理今日文章
            if date and is_today(date):
                print(f"    发现今日文章: {title}")
                content = cls._fetch_article_content(f"https://www.anthropic.com{href}")

                articles.append(NewsArticle(
                    title=title,
                    url=f"https://www.anthropic.com{href}",
                    date=date,
                    source="Anthropic News",
                    type="news",
                    content=content
                ))

        return articles


# ==================== 其他数据源（预留） ====================

class OpenAICrawler:
    """OpenAI官网信息爬取器（预留）"""

    @classmethod
    def crawl(cls) -> List[NewsArticle]:
        """
        爬取OpenAI内容

        Returns:
            List[NewsArticle]: 文章列表
        """
        return []


# ==================== 主程序 ====================

def get_daily_ai_news() -> NewsData:
    """
    获取每日AI新闻

    Returns:
        NewsData: 新闻数据
    """
    all_articles = []

    print("\n[1/2] 爬取 Anthropic...")
    anthropic_articles = AnthropicCrawler.crawl()
    all_articles.extend(anthropic_articles)

    print("\n[2/2] 爬取 OpenAI...")
    openai_articles = OpenAICrawler.crawl()
    all_articles.extend(openai_articles)

    news_data = NewsData(
        date=datetime.now().strftime("%Y-%m-%d"),
        total_count=len(all_articles),
        articles=all_articles
    )

    return news_data


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="每日AI新闻获取脚本")
    parser.add_argument("-o", "--output", required=True, help="输出JSON文件路径")

    args = parser.parse_args()

    print("=" * 60)
    print("开始获取每日AI新闻")
    print("=" * 60)

    news_data = get_daily_ai_news()

    print("\n" + "=" * 60)
    print(f"总计获取 {news_data.total_count} 篇文章")
    print("=" * 60)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(news_data.to_dict(), f, ensure_ascii=False, indent=2)

    print(f"\n新闻数据已保存至: {args.output}")


if __name__ == "__main__":
    main()
