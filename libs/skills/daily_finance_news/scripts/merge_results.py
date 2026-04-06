#!/usr/bin/env python3
"""
合并所有数据源的 Stage 1 结果，生成 JSON 原始数据和 Markdown 报告

Usage:
    python merge_results.py --input-dir ./output_finance/stage1 --output ./output_finance/finance_news_raw.json
"""

import argparse
import json
from datetime import datetime
from pathlib import Path
from common import NewsArticle


def generate_markdown_report(data: dict) -> str:
    """生成飞书文档格式的 Markdown 报告"""
    lines = []
    lines.append(f"# 每日金融资讯 - {data['date']}\n")
    lines.append("## 📊 今日概览\n")
    lines.append(f"- **日期**: {data['date']}")
    lines.append(f"- **来源**: Twitter 金融 KOL")
    lines.append(f"- **总条数**: {data['total_count']} 条")
    lines.append("\n---\n")

    # 按来源分组
    sources = {}
    for article in data['articles']:
        source = article['source']
        if source not in sources:
            sources[source] = []
        sources[source].append(article)

    # 定义人物介绍
    source_info = {
        'matt_levine (Twitter)': {
            'name': 'Matt Levine',
            'title': '彭博专栏作家',
            'description': '彭博社《Money Stuff》专栏作家，以幽默风趣的笔触解读复杂的金融新闻和华尔街动态。'
        },
        'IBDinvestors (Twitter)': {
            'name': 'IBD Investors',
            'title': "Investor's Business Daily",
            'description': 'IBD 是知名的投资研究媒体，提供股市分析、股票筛选工具和投资教育内容。'
        },
        'PeterLBrandt (Twitter)': {
            'name': 'Peter L Brandt',
            'title': '资深交易员',
            'description': 'Peter Brandt 是拥有40多年经验的资深期货交易员，专注于技术分析和图表模式交易。'
        }
    }

    # 生成每个来源的详细内容
    for source_name, articles in sources.items():
        source_key = source_name.replace(' (Twitter)', '')
        info = source_info.get(source_name, {'name': source_name, 'title': '', 'description': ''})

        lines.append(f"## 💰 {info['name']} ({info['title']})\n")
        lines.append(f">{info['description']}\n")

        for idx, article in enumerate(articles, 1):
            lines.append(f"### 推文 {idx}")
            lines.append(f"- **时间**: {article['date']}")
            lines.append(f"- **链接**: [查看原文]({article['url']})")
            lines.append(f"- **内容**: {article['content']}\n")

        lines.append("---\n")

    # 添加生成时间
    lines.append(f"\n*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}*")

    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description='合并所有数据源的 Stage 1 结果，生成 JSON 原始数据和 Markdown 报告')
    parser.add_argument('--input-dir', type=Path, required=True, help='Stage 1 结果目录')
    parser.add_argument('--output', type=Path, required=True, help='输出 JSON 文件路径')
    args = parser.parse_args()

    print(f"[合并结果] 从 {args.input_dir} 读取数据")

    all_articles = []
    sources_info = {}

    # 读取所有 stage1 结果文件
    for json_file in sorted(args.input_dir.glob('*.json')):
        print(f"  读取: {json_file.name}")

        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        articles = [NewsArticle(**a) for a in data.get('articles', [])]
        all_articles.extend(articles)

        sources_info[data.get('display_name', json_file.stem)] = {
            'count': len(articles),
            'username': data.get('username', ''),
            'source': data.get('source', '')
        }

        print(f"    - {len(articles)} 条推文")

    # 按日期排序
    all_articles.sort(key=lambda x: x.date, reverse=True)

    # 创建最终输出
    result = {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'total_count': len(all_articles),
        'sources': sources_info,
        'articles': [a.to_dict() for a in all_articles]
    }

    # 保存 JSON 结果
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\n  JSON 输出: {args.output}")

    # 生成 Markdown 报告
    md_output = args.output.parent / f"finance_news_{result['date']}.md"
    md_content = generate_markdown_report(result)
    with open(md_output, 'w', encoding='utf-8') as f:
        f.write(md_content)
    print(f"  Markdown 输出: {md_output}")

    print(f"\n{'='*60}")
    print(f"总计: {len(all_articles)} 条推文")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
