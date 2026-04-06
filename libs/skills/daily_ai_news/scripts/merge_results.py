#!/usr/bin/env python3
"""
合并所有数据源的 Stage 2 结果

Usage:
    python merge_results.py --input-dir ./output/stage2 --output ./output/ai_news_raw.json
"""

import argparse
import json
from datetime import datetime
from pathlib import Path
from common import NewsArticle


def main():
    parser = argparse.ArgumentParser(description='合并所有数据源的 Stage 2 结果')
    parser.add_argument('--input-dir', type=Path, required=True, help='Stage 2 结果目录')
    parser.add_argument('--output', type=Path, required=True, help='输出JSON文件路径')
    args = parser.parse_args()
    
    print(f"[合并结果] 从 {args.input_dir} 读取数据")
    
    all_articles = []
    
    # 读取所有 stage2 结果文件
    for json_file in sorted(args.input_dir.glob('*.json')):
        print(f"  读取: {json_file.name}")
        
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        articles = [NewsArticle(**a) for a in data.get('articles', [])]
        all_articles.extend(articles)
        
        print(f"    - {len(articles)} 篇文章")
    
    # 创建最终输出
    result = {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'total_count': len(all_articles),
        'articles': [a.to_dict() for a in all_articles]
    }
    
    # 保存结果
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*60}")
    print(f"总计: {len(all_articles)} 篇文章")
    print(f"输出: {args.output}")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
