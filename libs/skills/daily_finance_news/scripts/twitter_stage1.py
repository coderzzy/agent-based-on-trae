#!/usr/bin/env python3
"""
Twitter Stage 1 - 通用脚本
从列表页 HTML 提取过去24小时内的推文

Usage:
    python twitter_stage1.py --html ./output_finance/html/twitter_matt_levine.html --output ./output_finance/stage1/twitter_matt_levine.json --username matt_levine --display-name "Matt Levine"
"""

import argparse
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from bs4 import BeautifulSoup
from common import read_html_file, NewsArticle


def is_within_24h_twitter(datetime_attr: str, date_display: str) -> bool:
    """
    检查日期是否在过去24小时内 - Twitter 页面专用
    支持多种时间格式：
    1. ISO datetime 属性 (2026-04-04T16:45:23.000Z)
    2. 相对时间格式 (2h, 2m, 30s)
    3. 中文日期格式 (4月5日, 2023年1月25日)
    """
    now = datetime.now()
    
    # 优先使用 datetime 属性 (2026-04-04T16:45:23.000Z)
    if datetime_attr:
        try:
            date_obj = datetime.fromisoformat(datetime_attr.replace('Z', '+00:00'))
            # 检查是否在过去24小时内
            time_diff = now - date_obj.replace(tzinfo=None)
            return time_diff <= timedelta(hours=24)
        except:
            pass
    
    # 解析相对时间格式 (2h, 2m, 30s) 或中文格式 (10小时, 5分钟)
    if date_display:
        # 处理英文格式 "2h" (2小时前), "2m" (2分钟前), "30s" (30秒前)
        relative_match = re.match(r'^(\d+)([hms])$', date_display.strip())
        if relative_match:
            try:
                value, unit = relative_match.groups()
                value = int(value)
                
                if unit == 's':  # 秒
                    delta = value
                elif unit == 'm':  # 分钟
                    delta = value * 60
                elif unit == 'h':  # 小时
                    delta = value * 3600
                else:
                    return False
                
                # 如果小于24小时，则认为是今天
                if delta < 24 * 3600:
                    return True
            except:
                pass
        
        # 处理中文格式 "10小时" (10小时前), "5分钟" (5分钟前), "30秒" (30秒前)
        chinese_match = re.match(r'^(\d+)(小时|分钟|秒|分|时)$', date_display.strip())
        if chinese_match:
            try:
                value, unit = chinese_match.groups()
                value = int(value)
                
                if unit in ('秒',):  # 秒
                    delta = value
                elif unit in ('分钟', '分'):  # 分钟
                    delta = value * 60
                elif unit in ('小时', '时'):  # 小时
                    delta = value * 3600
                else:
                    return False
                
                # 如果小于24小时，则认为是今天
                if delta < 24 * 3600:
                    return True
            except:
                pass
        
        # 处理 "4月5日" 格式 - 检查是否在过去24小时内
        match = re.search(r'(\d{1,2})月(\d{1,2})日', date_display)
        if match:
            try:
                month, day = match.groups()
                date_obj = datetime(now.year, int(month), int(day))
                time_diff = now - date_obj
                return time_diff <= timedelta(hours=24)
            except:
                pass
        
        # 处理 "2023年1月25日" 格式 - 检查是否在过去24小时内
        match = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日', date_display)
        if match:
            try:
                year, month, day = match.groups()
                date_obj = datetime(int(year), int(month), int(day))
                time_diff = now - date_obj
                return time_diff <= timedelta(hours=24)
            except:
                pass
    
    return False


def parse_twitter_list(html: str, username: str) -> list:
    """
    解析 Twitter 列表页 HTML
    返回过去24小时内推文的列表
    """
    soup = BeautifulSoup(html, 'html.parser')
    articles = []
    
    # Twitter 使用 article[data-testid="tweet"]
    tweets = soup.select('article[data-testid="tweet"]')
    
    for tweet in tweets:
        # 获取时间
        time_elem = tweet.find('time')
        if not time_elem:
            continue
        
        datetime_attr = time_elem.get('datetime', '')
        date_display = time_elem.get_text(strip=True)
        
        # 检查是否在过去24小时内
        if not is_within_24h_twitter(datetime_attr, date_display):
            continue
        
        # 获取推文内容
        text_elem = tweet.select_one('[data-testid="tweetText"]')
        if not text_elem:
            continue
        
        content = text_elem.get_text(strip=True)
        
        # 获取推文链接
        link_elem = tweet.select_one('a[href*="/status/"]')
        tweet_url = f"https://x.com/{username}"
        if link_elem:
            href = link_elem.get('href', '')
            if href.startswith('/'):
                tweet_url = f"https://x.com{href}"
            else:
                tweet_url = href
        
        # 生成标题（推文前100字符）
        title = content[:100] + "..." if len(content) > 100 else content
        
        # 格式化日期显示
        if datetime_attr:
            try:
                date_obj = datetime.fromisoformat(datetime_attr.replace('Z', '+00:00'))
                formatted_date = date_obj.strftime('%b %d, %Y')
            except:
                formatted_date = date_display
        else:
            formatted_date = date_display
        
        articles.append(NewsArticle(
            title=title,
            url=tweet_url,
            source=f"{username} (Twitter)",
            type="twitter",
            date=formatted_date,
            content=content
        ))
    
    return articles


def main():
    parser = argparse.ArgumentParser(description='解析 Twitter 列表页 HTML，提取过去24小时内的推文')
    parser.add_argument('--html', type=Path, required=True, help='HTML 文件路径')
    parser.add_argument('--output', type=Path, required=True, help='输出 JSON 文件路径')
    parser.add_argument('--username', type=str, required=True, help='Twitter 用户名')
    parser.add_argument('--display-name', type=str, required=True, help='显示名称')
    args = parser.parse_args()
    
    print(f"[Twitter Stage 1] 处理 {args.display_name}")
    print(f"  读取: {args.html}")
    
    # 读取 HTML
    html = read_html_file(args.html)
    if not html:
        print(f"  错误: 无法读取 HTML 文件")
        # 创建空结果
        result = {
            'source': 'twitter',
            'username': args.username,
            'display_name': args.display_name,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'today_count': 0,
            'articles': []
        }
    else:
        # 解析推文
        articles = parse_twitter_list(html, args.username)
        
        print(f"  找到 {len(articles)} 条过去24小时内的推文")
        
        # 创建输出
        result = {
            'source': 'twitter',
            'username': args.username,
            'display_name': args.display_name,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'today_count': len(articles),
            'articles': [a.to_dict() for a in articles]
        }
    
    # 保存结果
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"  输出: {args.output}")
    print(f"  完成!")


if __name__ == '__main__':
    main()
