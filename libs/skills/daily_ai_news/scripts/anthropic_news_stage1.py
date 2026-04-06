#!/usr/bin/env python3
"""
Anthropic News - Stage 1
从列表页 HTML 提取今日文章的基本信息

Usage:
    python anthropic_news_stage1.py --html ./output/html/anthropic_news.html --output ./output/stage1/news.json
"""

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup
from common import read_html_file, NewsArticle


def is_within_24h_news(date_str: str) -> bool:
    """
    检查日期是否在过去24小时内 - News 页面专用
    日期格式: "Mar 25, 2026"
    """
    from datetime import timedelta
    if not date_str:
        return False
    
    now = datetime.now()
    date_str = date_str.strip()
    
    # News 页面格式
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


def extract_date_from_news_text(text: str) -> str:
    """从 News 页面文本中提取日期"""
    # 匹配日期格式 "Mar 25, 2026"
    match = re.search(r'([A-Z][a-z]{2}\s+\d{1,2},?\s+\d{4})', text)
    if match:
        return match.group(1)
    return ""


def parse_news_list(html: str) -> list:
    """
    解析 News 列表页 HTML
    返回今日文章的列表
    """
    soup = BeautifulSoup(html, 'html.parser')
    articles = []
    seen_urls = set()
    
    # News 页面的文章链接以 /news/ 开头
    for link in soup.find_all('a', href=True):
        href = link.get('href', '')
        
        # 过滤：必须是 /news/ 开头
        if not href.startswith('/news/'):
            continue
        
        # 去重
        if href in seen_urls:
            continue
        seen_urls.add(href)
        
        # 提取链接文本
        link_text = link.get_text(strip=True)
        
        # 提取日期
        date = extract_date_from_news_text(link_text)
        
        # 检查是否在过去24小时内
        if not is_within_24h_news(date):
            continue
        
        # 提取标题（去掉日期和类型前缀）
        title = link_text
        # 移除开头的类型标签
        for prefix in ['Product', 'Announcements', 'Policy', 'Research']:
            if title.startswith(prefix):
                title = title[len(prefix):].strip()
                break
        # 移除日期
        if date in title:
            title = title.replace(date, '').strip()
        
        # 备选标题
        if not title or len(title) < 5:
            slug = href.split('/')[-1].replace('-', ' ').title()
            title = slug
        
        articles.append(NewsArticle(
            title=title,
            url=f"https://www.anthropic.com{href}",
            date=date,
            source="Anthropic News",
            type="news",
            content=""
        ))
    
    return articles


def main():
    parser = argparse.ArgumentParser(description='Anthropic News Stage 1: 从列表页提取今日文章')
    parser.add_argument('--html', type=Path, required=True, help='输入HTML文件路径')
    parser.add_argument('--output', type=Path, required=True, help='输出JSON文件路径')
    args = parser.parse_args()
    
    print(f"[News Stage 1] 处理 {args.html}")
    
    # 读取HTML
    html = read_html_file(args.html)
    if not html:
        print(f"  错误: 无法读取 {args.html}")
        return
    
    # 解析今日文章
    today_articles = parse_news_list(html)
    
    print(f"  找到 {len(today_articles)} 篇今日文章")
    for article in today_articles:
        print(f"    - {article.title[:60]}... ({article.date})")
    
    # 保存结果
    args.output.parent.mkdir(parents=True, exist_ok=True)
    result = {
        'source': 'news',
        'date': datetime.now().strftime('%Y-%m-%d'),
        'today_count': len(today_articles),
        'articles': [a.to_dict() for a in today_articles]
    }
    
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"  结果已保存: {args.output}")


if __name__ == '__main__':
    main()
