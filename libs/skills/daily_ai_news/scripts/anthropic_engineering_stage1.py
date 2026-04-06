#!/usr/bin/env python3
"""
Anthropic Engineering - Stage 1
从列表页 HTML 提取今日文章的基本信息

Usage:
    python anthropic_engineering_stage1.py --html ./output/html/anthropic_engineering.html --output ./output/stage1/engineering.json
"""

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup
from common import read_html_file, NewsArticle


def is_within_24h_engineering(date_str: str) -> bool:
    """
    检查日期是否在过去24小时内 - Engineering 页面专用
    日期格式: "Mar 25, 2026" 或 "Mar 25 2026"
    """
    from datetime import timedelta
    if not date_str:
        return False
    
    now = datetime.now()
    date_str = date_str.strip()
    
    # Engineering 页面格式
    formats = [
        "%b %d, %Y",  # "Mar 25, 2026"
        "%b %d %Y",   # "Mar 25 2026"
    ]
    
    for fmt in formats:
        try:
            date_obj = datetime.strptime(date_str, fmt)
            # 检查是否在过去24小时内
            time_diff = now - date_obj
            return time_diff <= timedelta(hours=24)
        except ValueError:
            continue
    
    return False


def extract_date_from_article(article_elem) -> str:
    """从 article 元素中提取日期"""
    # 获取整个 article 的文本
    article_text = article_elem.get_text(strip=True)
    
    # 匹配日期格式 "Mar 25, 2026"
    match = re.search(r'([A-Z][a-z]{2}\s+\d{1,2},?\s+\d{4})', article_text)
    if match:
        return match.group(1)
    
    return ""


def parse_engineering_list(html: str) -> list:
    """
    解析 Engineering 列表页 HTML
    返回今日文章的列表
    """
    soup = BeautifulSoup(html, 'html.parser')
    articles = []
    
    # Engineering 页面使用 article 标签
    for article_elem in soup.find_all('article'):
        link = article_elem.find('a', href=True)
        if not link:
            continue
        
        href = link.get('href', '')
        if not href.startswith('/engineering/'):
            continue
        
        # 提取标题
        title_elem = article_elem.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        title = title_elem.get_text(strip=True) if title_elem else ""
        
        # 提取日期
        date = extract_date_from_article(article_elem)
        
        # 检查是否在过去24小时内
        if title and href and is_within_24h_engineering(date):
            articles.append(NewsArticle(
                title=title,
                url=f"https://www.anthropic.com{href}",
                date=date,
                source="Anthropic Engineering",
                type="engineering",
                content=""
            ))
    
    return articles


def main():
    parser = argparse.ArgumentParser(description='Anthropic Engineering Stage 1: 从列表页提取今日文章')
    parser.add_argument('--html', type=Path, required=True, help='输入HTML文件路径')
    parser.add_argument('--output', type=Path, required=True, help='输出JSON文件路径')
    args = parser.parse_args()
    
    print(f"[Engineering Stage 1] 处理 {args.html}")
    
    # 读取HTML
    html = read_html_file(args.html)
    if not html:
        print(f"  错误: 无法读取 {args.html}")
        return
    
    # 解析今日文章
    today_articles = parse_engineering_list(html)
    
    print(f"  找到 {len(today_articles)} 篇今日文章")
    for article in today_articles:
        print(f"    - {article.title[:60]}... ({article.date})")
    
    # 保存结果
    args.output.parent.mkdir(parents=True, exist_ok=True)
    result = {
        'source': 'engineering',
        'date': datetime.now().strftime('%Y-%m-%d'),
        'today_count': len(today_articles),
        'articles': [a.to_dict() for a in today_articles]
    }
    
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"  结果已保存: {args.output}")


if __name__ == '__main__':
    main()
