#!/usr/bin/env python3
"""通用工具函数"""
import json
import re
from datetime import datetime
from pathlib import Path


def read_html_file(file_path: Path) -> str:
    """读取HTML文件内容，支持直接HTML和JSON包装的HTML"""
    try:
        content = file_path.read_text(encoding='utf-8')
        
        # 尝试解析为JSON（browser-control返回的格式）
        try:
            data = json.loads(content)
            if isinstance(data, dict) and 'data' in data and 'content' in data['data']:
                return data['data']['content']
        except json.JSONDecodeError:
            pass
        
        # 直接返回HTML内容
        return content
    except Exception as e:
        print(f"  读取文件失败 {file_path}: {e}")
        return ""


def extract_date_from_text(text: str) -> str:
    """从文本中提取日期"""
    # 匹配常见日期格式
    patterns = [
        r'([A-Z][a-z]{2}\s+\d{1,2},?\s+\d{4})',  # "Mar 25, 2026" or "Mar 25 2026"
        r'([A-Z][a-z]{2,8}\s+\d{1,2},?\s+\d{4})',  # "March 25, 2026"
        r'(\d{4}-\d{2}-\d{2})',  # "2026-03-25"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)
    
    return ""


def is_today(date_str: str) -> bool:
    """检查日期是否为今天"""
    if not date_str:
        return False
    
    today = datetime.now()
    date_str = date_str.strip()
    
    # 尝试多种日期格式
    date_formats = [
        "%b %d, %Y",      # "Mar 25, 2026"
        "%B %d, %Y",      # "March 25, 2026"
        "%b %d %Y",       # "Mar 25 2026"
        "%Y-%m-%d",       # "2026-03-25"
        "%Y/%m/%d",       # "2026/03/25"
        "%d %b %Y",       # "25 Mar 2026"
        "%d %B %Y",       # "25 March 2026"
        "%b %d",          # "Apr 6" (当年)
        "%B %d",          # "April 6"
    ]
    
    for fmt in date_formats:
        try:
            date_obj = datetime.strptime(date_str, fmt)
            # 如果没有年份，假设为今年
            if date_obj.year == 1900:
                date_obj = date_obj.replace(year=today.year)
            return date_obj.date() == today.date()
        except ValueError:
            continue
    
    # 处理 ISO 格式 (2026-04-04T16:45:23.000Z)
    try:
        date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return date_obj.date() == today.date()
    except:
        pass
    
    # 处理中文日期格式 (如 "4月5日" 或 "2023年1月25日")
    chinese_patterns = [
        (r'(\d{4})年(\d{1,2})月(\d{1,2})日', '%Y-%m-%d'),  # "2023年1月25日"
        (r'(\d{1,2})月(\d{1,2})日', '%m-%d'),             # "4月5日"
    ]
    
    for pattern, fmt in chinese_patterns:
        match = re.search(pattern, date_str)
        if match:
            try:
                if fmt == '%Y-%m-%d':
                    year, month, day = match.groups()
                    date_obj = datetime(int(year), int(month), int(day))
                else:  # '%m-%d'
                    month, day = match.groups()
                    date_obj = datetime(today.year, int(month), int(day))
                return date_obj.date() == today.date()
            except:
                continue
    
    return False


from dataclasses import dataclass, asdict


@dataclass
class NewsArticle:
    """单篇文章的数据结构"""
    title: str
    url: str
    source: str
    type: str
    date: str = ""
    content: str = ""

    def to_dict(self) -> dict:
        return asdict(self)
