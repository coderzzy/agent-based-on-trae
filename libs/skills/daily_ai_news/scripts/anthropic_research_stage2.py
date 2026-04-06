#!/usr/bin/env python3
"""
Anthropic Research - Stage 2
从详情页 HTML 提取文章内容

Usage:
    python anthropic_research_stage2.py --stage1 ./output/stage1/research.json --articles-dir ./output/html/articles --output ./output/stage2/research.json
"""

import argparse
import json
import re
from pathlib import Path
from bs4 import BeautifulSoup
from common import read_html_file, NewsArticle


def parse_article_content(html: str) -> str:
    """从详情页 HTML 提取正文内容"""
    soup = BeautifulSoup(html, 'html.parser')
    
    # 尝试多种选择器
    selectors = [
        'article',
        'main',
        '[class*="content"]',
        '[class*="article"]',
    ]
    
    for selector in selectors:
        try:
            elem = soup.select_one(selector)
            if elem:
                text = elem.get_text(separator=" ", strip=True)
                if len(text) > 500:
                    return text[:8000]
        except:
            continue
    
    # 备选：返回body文本
    body = soup.find('body')
    if body:
        return body.get_text(separator=" ", strip=True)[:8000]
    
    return ""


def main():
    parser = argparse.ArgumentParser(description='Anthropic Research Stage 2: 从详情页提取内容')
    parser.add_argument('--stage1', type=Path, required=True, help='Stage 1 输出的JSON文件')
    parser.add_argument('--articles-dir', type=Path, required=True, help='详情页HTML目录')
    parser.add_argument('--output', type=Path, required=True, help='输出JSON文件路径')
    args = parser.parse_args()
    
    print(f"[Research Stage 2] 处理 {args.stage1}")
    
    # 读取 stage1 结果
    with open(args.stage1, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    articles = [NewsArticle(**a) for a in data.get('articles', [])]
    
    print(f"  需要处理 {len(articles)} 篇文章的详情页")
    
    # 处理每篇文章的详情页
    for article in articles:
        # 从 URL 生成文件名
        url_hash = re.sub(r'[^\w]', '_', article.url)
        article_html_path = args.articles_dir / f"{url_hash}.html"
        
        if article_html_path.exists():
            html = read_html_file(article_html_path)
            article.content = parse_article_content(html)
            print(f"    ✓ {article.title[:50]}... ({len(article.content)} 字符)")
        else:
            print(f"    ✗ 未找到详情页: {article_html_path.name}")
    
    # 保存结果
    args.output.parent.mkdir(parents=True, exist_ok=True)
    result = {
        'source': 'research',
        'articles': [a.to_dict() for a in articles]
    }
    
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"  结果已保存: {args.output}")


if __name__ == '__main__':
    main()
