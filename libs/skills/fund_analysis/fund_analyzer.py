#!/usr/bin/env python3
"""
基金数据分析脚本
用于解析天天基金网数据并生成HTML分析报告
"""

import re
import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Tuple, Any
import numpy as np


class FundDataParser:
    """基金数据解析器"""
    
    def __init__(self, js_content: str):
        self.js_content = js_content
        self.data = {}
        
    def parse(self) -> Dict:
        """解析JS内容提取关键数据"""
        # 提取基金基本信息
        self.data['name'] = self._extract_string('fS_name')
        self.data['code'] = self._extract_string('fS_code')
        self.data['source_rate'] = self._extract_string('fund_sourceRate')
        self.data['rate'] = self._extract_string('fund_Rate')
        self.data['min_amount'] = self._extract_string('fund_minsg')
        
        # 提取收益率
        self.data['return_1y'] = self._extract_float('syl_1y')
        self.data['return_6m'] = self._extract_float('syl_6y')
        self.data['return_3m'] = self._extract_float('syl_3y')
        self.data['return_1m'] = self._extract_float('syl_1y')
        
        # 提取净值走势数据
        self.data['net_worth_trend'] = self._extract_json('Data_netWorthTrend')
        self.data['ac_worth_trend'] = self._extract_array('Data_acWorthTrend')
        
        return self.data
    
    def _extract_string(self, var_name: str) -> str:
        """提取字符串变量"""
        pattern = rf'var {var_name}\s*=\s*"([^"]*)"'
        match = re.search(pattern, self.js_content)
        return match.group(1) if match else ''
    
    def _extract_float(self, var_name: str) -> float:
        """提取浮点数变量"""
        pattern = rf'var {var_name}\s*=\s*"([^"]*)"'
        match = re.search(pattern, self.js_content)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                return 0.0
        return 0.0
    
    def _extract_json(self, var_name: str) -> List[Dict]:
        """提取JSON数组"""
        pattern = rf'var {var_name}\s*=\s*(\[.*?\]);'
        match = re.search(pattern, self.js_content, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                return []
        return []
    
    def _extract_array(self, var_name: str) -> List[List]:
        """提取二维数组"""
        pattern = rf'var {var_name}\s*=\s*(\[\[.*?\]\]);'
        match = re.search(pattern, self.js_content, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                return []
        return []


class FundAnalyzer:
    """基金数据分析器"""
    
    def __init__(self, data: Dict):
        self.data = data
        self.df = self._prepare_dataframe()
        
    def _prepare_dataframe(self) -> List[Dict]:
        """准备数据列表"""
        net_worth = self.data.get('net_worth_trend', [])
        records = []
        for item in net_worth:
            records.append({
                'date': datetime.fromtimestamp(item['x'] / 1000),
                'net_worth': item['y'],
                'daily_return': item.get('equityReturn', 0)
            })
        return records
    
    def analyze_monthly_returns(self) -> Dict:
        """按月分析收益，涨幅和跌幅分开统计"""
        # 按月份分组计算月收益率
        monthly_data = {}
        for record in self.df:
            month_key = record['date'].strftime('%Y-%m')
            if month_key not in monthly_data:
                monthly_data[month_key] = {'values': [], 'date': record['date']}
            monthly_data[month_key]['values'].append(record['net_worth'])
        
        # 计算每个月的收益率
        monthly_returns = {}
        for month, data in monthly_data.items():
            values = data['values']
            if len(values) > 1:
                ret = (values[-1] - values[0]) / values[0] * 100
                monthly_returns[month] = {
                    'return': ret,
                    'start_date': data['date'].strftime('%Y-%m-%d')
                }
        
        # 分开统计涨幅和跌幅
        positive_returns = [v['return'] for v in monthly_returns.values() if v['return'] > 0]
        negative_returns = [v['return'] for v in monthly_returns.values() if v['return'] < 0]
        
        result = {
            'monthly_details': monthly_returns,
            'positive': {
                'count': len(positive_returns),
                'mean': float(np.mean(positive_returns)) if positive_returns else 0,
                'median': float(np.median(positive_returns)) if positive_returns else 0,
                'max': float(np.max(positive_returns)) if positive_returns else 0,
                'returns': positive_returns
            },
            'negative': {
                'count': len(negative_returns),
                'mean': float(np.mean(negative_returns)) if negative_returns else 0,
                'median': float(np.median(negative_returns)) if negative_returns else 0,
                'min': float(np.min(negative_returns)) if negative_returns else 0,
                'returns': negative_returns
            }
        }
        
        return result
    
    def analyze_multi_period_returns(self) -> Dict:
        """
        按不同持有周期分析涨跌幅（使用不重叠滑动窗口）
        周期：1天、3天、1周(7天)、1月(30天)、半年(180天)、一年(365天)
        
        算法：使用不重叠的滑动窗口，例如1年周期，从第0天开始，然后是第365天、第730天...
        这样4年历史只有4个1年样本，更符合实际投资场景。
        """
        periods = {
            '1天': 1,
            '3天': 3,
            '1周': 7,
            '1月': 30,
            '半年': 180,
            '1年': 365
        }
        
        result = {}
        
        for period_name, days in periods.items():
            returns = []
            
            # 使用不重叠窗口：从0开始，每次跳跃days天
            i = 0
            while i + days < len(self.df):
                start_value = self.df[i]['net_worth']
                end_value = self.df[i + days]['net_worth']
                total_return = (end_value - start_value) / start_value * 100
                returns.append(total_return)
                i += days  # 跳跃days天，确保窗口不重叠
            
            if returns:
                # 分开统计正收益和负收益
                positive_returns = [r for r in returns if r > 0]
                negative_returns = [r for r in returns if r < 0]
                
                result[period_name] = {
                    'positive': {
                        'count': len(positive_returns),
                        'mean': float(np.mean(positive_returns)) if positive_returns else 0,
                        'median': float(np.median(positive_returns)) if positive_returns else 0,
                        'max': float(np.max(positive_returns)) if positive_returns else 0
                    },
                    'negative': {
                        'count': len(negative_returns),
                        'mean': float(np.mean(negative_returns)) if negative_returns else 0,
                        'median': float(np.median(negative_returns)) if negative_returns else 0,
                        'min': float(np.min(negative_returns)) if negative_returns else 0
                    },
                    'total_samples': len(returns)
                }
            else:
                result[period_name] = {
                    'positive': {'count': 0, 'mean': 0, 'median': 0, 'max': 0},
                    'negative': {'count': 0, 'mean': 0, 'median': 0, 'min': 0},
                    'total_samples': 0
                }
        
        return result
    
    def find_return_periods(self) -> Dict:
        """
        分析收益周期和反转天数
        
        包含两部分分析：
        1. 为每一天找到从该天开始的最长正/负收益周期
        2. 计算反转天数：从正收益状态转为负收益状态（或反之）的平均时间
        
        反转天数定义：
        - 正转负：从某一天开始持有收益为正，到第一次出现持有收益为负的间隔天数
        - 负转正：从某一天开始持有收益为负，到第一次出现持有收益为正的间隔天数
        """
        if len(self.df) < 2:
            return {
                'positive': {
                    'max_period': {'days': 0, 'start_date': None, 'end_date': None, 'return': 0},
                    'avg_period': {'days': 0},
                    'median_period': {'days': 0}
                },
                'negative': {
                    'max_period': {'days': 0, 'start_date': None, 'end_date': None, 'return': 0},
                    'avg_period': {'days': 0},
                    'median_period': {'days': 0}
                },
                'reversal': {
                    'positive_to_negative': {'avg_days': 0, 'median_days': 0, 'count': 0},
                    'negative_to_positive': {'avg_days': 0, 'median_days': 0, 'count': 0}
                }
            }
        
        positive_periods = []
        negative_periods = []
        
        # 用于计算反转天数
        pos_to_neg_days = []  # 正转负的天数
        neg_to_pos_days = []  # 负转正的天数
        
        for start_idx in range(len(self.df)):
            start_value = self.df[start_idx]['net_worth']
            start_date = self.df[start_idx]['date']
            
            # 找从当前点开始的最长正收益周期
            best_positive = None
            # 找从当前点开始的最长负收益周期
            best_negative = None
            
            # 找第一次反转点
            first_negative = None  # 第一次出现负收益
            first_positive = None  # 第一次出现正收益
            
            for end_idx in range(start_idx + 1, len(self.df)):
                end_value = self.df[end_idx]['net_worth']
                end_date = self.df[end_idx]['date']
                
                total_return = (end_value - start_value) / start_value * 100
                days = (end_date - start_date).days
                
                period_info = {
                    'start_idx': start_idx,
                    'end_idx': end_idx,
                    'days': days,
                    'start_date': start_date.strftime('%Y-%m-%d'),
                    'end_date': end_date.strftime('%Y-%m-%d'),
                    'return': total_return
                }
                
                # 只要是正收益就更新（找最长的）
                if total_return > 0:
                    best_positive = period_info
                    # 记录第一次出现正收益（用于负转正的计算）
                    if first_positive is None:
                        first_positive = days
                # 只要是负收益就更新（找最长的）
                elif total_return < 0:
                    best_negative = period_info
                    # 记录第一次出现负收益（用于正转负的计算）
                    if first_negative is None:
                        first_negative = days
            
            # 记录从当前点开始的最长正收益周期（如果存在）
            if best_positive is not None:
                positive_periods.append(best_positive)
            
            # 记录从当前点开始的最长负收益周期（如果存在）
            if best_negative is not None:
                negative_periods.append(best_negative)
            
            # 计算反转天数
            # 如果当前点既有正收益可能又有负收益可能
            if first_negative is not None:
                pos_to_neg_days.append(first_negative)
            if first_positive is not None:
                neg_to_pos_days.append(first_positive)
        
        # 统计正收益周期
        positive_result = self._calculate_period_stats(positive_periods)
        # 统计负收益周期
        negative_result = self._calculate_period_stats(negative_periods)
        
        # 统计反转天数
        reversal_stats = {
            'positive_to_negative': {
                'avg_days': float(np.mean(pos_to_neg_days)) if pos_to_neg_days else 0,
                'median_days': float(np.median(pos_to_neg_days)) if pos_to_neg_days else 0,
                'max_days': float(np.max(pos_to_neg_days)) if pos_to_neg_days else 0,
                'count': len(pos_to_neg_days)
            },
            'negative_to_positive': {
                'avg_days': float(np.mean(neg_to_pos_days)) if neg_to_pos_days else 0,
                'median_days': float(np.median(neg_to_pos_days)) if neg_to_pos_days else 0,
                'max_days': float(np.max(neg_to_pos_days)) if neg_to_pos_days else 0,
                'count': len(neg_to_pos_days)
            }
        }
        
        return {
            'positive': positive_result,
            'negative': negative_result,
            'reversal': reversal_stats
        }
    
    def _calculate_period_stats(self, periods: List[Dict]) -> Dict:
        """计算周期统计信息"""
        if not periods:
            return {
                'max_period': {'days': 0, 'start_date': None, 'end_date': None, 'return': 0},
                'avg_period': {'days': 0},
                'median_period': {'days': 0},
                'total_periods': 0,
                'distribution': {},
                'warning_days': 0
            }
        
        # 找出最大周期
        max_period = max(periods, key=lambda x: x['days'])
        
        # 计算统计值
        all_days = [p['days'] for p in periods]
        avg_days = np.mean(all_days)
        median_days = np.median(all_days)
        
        # 计算分布（按天数分段）
        distribution = self._calculate_period_distribution(all_days)
        
        # 计算预警天数（基于百分位数）
        # 使用25%分位数作为预警线：25%的正收益周期在这个天数内结束
        warning_days = np.percentile(all_days, 25)
        
        # 计算不同持有时间的平均收益
        return_by_holding = self._calculate_return_by_holding_period(periods)
        
        return {
            'max_period': {
                'days': int(max_period['days']),
                'start_date': max_period['start_date'],
                'end_date': max_period['end_date'],
                'return': float(max_period['return'])
            },
            'avg_period': {
                'days': float(avg_days)
            },
            'median_period': {
                'days': float(median_days)
            },
            'total_periods': len(periods),
            'distribution': distribution,
            'warning_days': float(warning_days),
            'return_by_holding': return_by_holding
        }
    
    def _calculate_period_distribution(self, all_days: List[int]) -> Dict:
        """计算周期天数分布"""
        # 定义时间段
        ranges = [
            (0, 7, '1周内'),
            (7, 30, '1周-1月'),
            (30, 90, '1-3月'),
            (90, 180, '3-6月'),
            (180, 365, '6月-1年'),
            (365, 730, '1-2年'),
            (730, float('inf'), '2年以上')
        ]
        
        distribution = {}
        for min_days, max_days, label in ranges:
            count = sum(1 for d in all_days if min_days <= d < max_days)
            percentage = count / len(all_days) * 100 if all_days else 0
            distribution[label] = {
                'count': count,
                'percentage': float(percentage)
            }
        
        return distribution
    
    def _calculate_return_by_holding_period(self, periods: List[Dict]) -> Dict:
        """计算不同持有时间的平均收益"""
        # 按持有时间分组
        short_term = []  # < 30天
        medium_term = []  # 30-180天
        long_term = []  # > 180天
        
        for p in periods:
            days = p['days']
            ret = p['return']
            if days < 30:
                short_term.append(ret)
            elif days < 180:
                medium_term.append(ret)
            else:
                long_term.append(ret)
        
        return {
            'short_term': {
                'days_range': '< 30天',
                'avg_return': float(np.mean(short_term)) if short_term else 0,
                'count': len(short_term)
            },
            'medium_term': {
                'days_range': '30-180天',
                'avg_return': float(np.mean(medium_term)) if medium_term else 0,
                'count': len(medium_term)
            },
            'long_term': {
                'days_range': '> 180天',
                'avg_return': float(np.mean(long_term)) if long_term else 0,
                'count': len(long_term)
            }
        }
    
    def calculate_max_drawdown(self) -> Dict:
        """计算最大回撤"""
        if not self.df:
            return {'max_drawdown': 0, 'start_date': None, 'end_date': None}
        
        max_drawdown = 0
        peak_value = self.df[0]['net_worth']
        peak_date = self.df[0]['date']
        start_date = None
        end_date = None
        
        for record in self.df:
            if record['net_worth'] > peak_value:
                peak_value = record['net_worth']
                peak_date = record['date']
            
            drawdown = (peak_value - record['net_worth']) / peak_value * 100
            if drawdown > max_drawdown:
                max_drawdown = drawdown
                start_date = peak_date
                end_date = record['date']
        
        return {
            'max_drawdown': max_drawdown,
            'start_date': start_date.strftime('%Y-%m-%d') if start_date else None,
            'end_date': end_date.strftime('%Y-%m-%d') if end_date else None
        }
    
    def calculate_volatility(self) -> Dict:
        """计算波动率"""
        if len(self.df) < 2:
            return {'daily': 0, 'annualized': 0}
        
        daily_returns = []
        for i in range(1, len(self.df)):
            ret = (self.df[i]['net_worth'] - self.df[i-1]['net_worth']) / self.df[i-1]['net_worth']
            daily_returns.append(ret)
        
        daily_vol = np.std(daily_returns) * 100
        annualized_vol = daily_vol * np.sqrt(252)
        
        return {
            'daily': float(daily_vol),
            'annualized': float(annualized_vol)
        }
    
    def get_price_extremes(self) -> Dict:
        """获取价格极值"""
        if not self.df:
            return {}
        
        max_record = max(self.df, key=lambda x: x['net_worth'])
        min_record = min(self.df, key=lambda x: x['net_worth'])
        
        return {
            'max': {
                'value': max_record['net_worth'],
                'date': max_record['date'].strftime('%Y-%m-%d')
            },
            'min': {
                'value': min_record['net_worth'],
                'date': min_record['date'].strftime('%Y-%m-%d')
            }
        }
    
    def monthly_analysis(self) -> Dict:
        """月度收益分析"""
        monthly_returns = {}
        
        for record in self.df:
            month_key = record['date'].strftime('%Y-%m')
            if month_key not in monthly_returns:
                monthly_returns[month_key] = []
            monthly_returns[month_key].append(record['net_worth'])
        
        results = {}
        for month, values in monthly_returns.items():
            if len(values) > 1:
                ret = (values[-1] - values[0]) / values[0] * 100
                results[month] = ret
        
        return results


class HTMLReportGenerator:
    """HTML报告生成器"""
    
    def __init__(self, fund_data: Dict, analysis_results: Dict):
        self.fund_data = fund_data
        self.analysis = analysis_results
        
    def generate(self) -> str:
        """生成HTML报告"""
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>基金分析报告 - {self.fund_data.get('name', '')}</title>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f7fa;
            color: #333;
            line-height: 1.6;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        .header {{ 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            border-radius: 16px;
            margin-bottom: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        }}
        .header h1 {{ font-size: 32px; margin-bottom: 10px; }}
        .header .meta {{ opacity: 0.9; font-size: 14px; }}
        .card {{ 
            background: white;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 20px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        }}
        .card h2 {{ 
            font-size: 20px; 
            margin-bottom: 20px;
            color: #1a1a1a;
            border-left: 4px solid #667eea;
            padding-left: 12px;
        }}
        .info-grid {{ 
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
        }}
        .info-item {{ 
            background: #f8f9fa;
            padding: 16px;
            border-radius: 8px;
        }}
        .info-item .label {{ 
            font-size: 12px;
            color: #666;
            margin-bottom: 4px;
        }}
        .info-item .value {{ 
            font-size: 20px;
            font-weight: 600;
            color: #1a1a1a;
        }}
        .chart-container {{ 
            height: 400px;
            margin: 20px 0;
        }}
        table {{ 
            width: 100%;
            border-collapse: collapse;
            margin-top: 16px;
        }}
        th, td {{ 
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }}
        th {{ 
            background: #f8f9fa;
            font-weight: 600;
            color: #666;
            font-size: 12px;
            text-transform: uppercase;
        }}
        .positive {{ color: #e74c3c; }}
        .negative {{ color: #27ae60; }}
        .highlight {{ 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            margin-top: 20px;
        }}
        .highlight h3 {{ margin-bottom: 12px; }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 16px;
            margin-top: 16px;
        }}
        .metric {{
            text-align: center;
            padding: 16px;
            background: rgba(255,255,255,0.1);
            border-radius: 8px;
        }}
        .metric-value {{
            font-size: 24px;
            font-weight: 700;
            margin-bottom: 4px;
        }}
        .metric-label {{
            font-size: 12px;
            opacity: 0.9;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{self.fund_data.get('name', '')}</h1>
            <div class="meta">
                基金代码: {self.fund_data.get('code', '')} | 
                报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            </div>
        </div>
        
        <div class="card">
            <h2>基金基本信息</h2>
            <div class="info-grid">
                <div class="info-item">
                    <div class="label">基金代码</div>
                    <div class="value">{self.fund_data.get('code', '')}</div>
                </div>
                <div class="info-item">
                    <div class="label">当前费率</div>
                    <div class="value">{self.fund_data.get('rate', '')}%</div>
                </div>
                <div class="info-item">
                    <div class="label">最小申购金额</div>
                    <div class="value">{self.fund_data.get('min_amount', '')}元</div>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h2>累计净值走势</h2>
            <div id="trendChart" class="chart-container"></div>
        </div>
        
        <div class="card">
            <h2>不同间隔周期涨跌幅分析</h2>
            {self._generate_multi_period_returns_table()}
        </div>
        
        <div class="card">
            <h2>收益反转周期分析</h2>
            {self._generate_positive_periods_table()}
        </div>
        
        <div class="card">
            <h2>价格极值</h2>
            {self._generate_extremes_table()}
        </div>
        
        <div class="card">
            <h2>月度收益分析</h2>
            {self._generate_monthly_returns_table()}
            <div id="monthlyChart" class="chart-container" style="margin-top: 24px;"></div>
        </div>
        
        <div class="highlight">
            <h3>数据洞察</h3>
            <p id="insights">等待Agent解读...</p>
        </div>
    </div>
    
    <script>
        // 净值走势图
        const trendChart = echarts.init(document.getElementById('trendChart'));
        const trendData = {self._get_trend_chart_data()};
        trendChart.setOption({{
            tooltip: {{
                trigger: 'axis',
                formatter: function(params) {{
                    const date = new Date(params[0].value[0]);
                    return date.toLocaleDateString() + '<br/>净值: ' + params[0].value[1].toFixed(4);
                }}
            }},
            xAxis: {{
                type: 'time',
                boundaryGap: false
            }},
            yAxis: {{
                type: 'value',
                scale: true
            }},
            series: [{{
                name: '累计净值',
                type: 'line',
                data: trendData,
                smooth: true,
                symbol: 'none',
                lineStyle: {{ width: 2 }},
                areaStyle: {{
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                        {{ offset: 0, color: 'rgba(102, 126, 234, 0.3)' }},
                        {{ offset: 1, color: 'rgba(102, 126, 234, 0.05)' }}
                    ])
                }}
            }}]
        }});
        
        // 月度收益图
        const monthlyChart = echarts.init(document.getElementById('monthlyChart'));
        const monthlyData = {self._get_monthly_chart_data()};
        monthlyChart.setOption({{
            tooltip: {{ trigger: 'axis' }},
            xAxis: {{
                type: 'category',
                data: monthlyData.categories,
                axisLabel: {{ rotate: 45 }}
            }},
            yAxis: {{ type: 'value', name: '收益率(%)' }},
            series: [{{
                name: '月度收益',
                type: 'bar',
                data: monthlyData.values,
                itemStyle: {{
                    color: function(params) {{
                        return params.value >= 0 ? '#e74c3c' : '#27ae60';
                    }}
                }}
            }}]
        }});
        
        window.addEventListener('resize', function() {{
            trendChart.resize();
            monthlyChart.resize();
        }});
    </script>
</body>
</html>"""
        return html
    
    def _generate_monthly_returns_table(self) -> str:
        """生成月度收益分析表格"""
        monthly = self.analysis.get('monthly_returns', {})
        positive = monthly.get('positive', {})
        negative = monthly.get('negative', {})
        
        return f"""
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 16px;">
            <div style="background: #fff5f5; padding: 20px; border-radius: 8px; border-left: 4px solid #e74c3c;">
                <h4 style="color: #e74c3c; margin-bottom: 12px;">📈 上涨月份统计</h4>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                    <div class="info-item">
                        <div class="label">上涨月数</div>
                        <div class="value" style="color: #e74c3c;">{positive.get('count', 0)}</div>
                    </div>
                    <div class="info-item">
                        <div class="label">平均涨幅</div>
                        <div class="value" style="color: #e74c3c;">{positive.get('mean', 0):.2f}%</div>
                    </div>
                    <div class="info-item">
                        <div class="label">中位数涨幅</div>
                        <div class="value" style="color: #e74c3c;">{positive.get('median', 0):.2f}%</div>
                    </div>
                    <div class="info-item">
                        <div class="label">最大涨幅</div>
                        <div class="value" style="color: #e74c3c;">{positive.get('max', 0):.2f}%</div>
                    </div>
                </div>
            </div>
            <div style="background: #f0fff4; padding: 20px; border-radius: 8px; border-left: 4px solid #27ae60;">
                <h4 style="color: #27ae60; margin-bottom: 12px;">📉 下跌月份统计</h4>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                    <div class="info-item">
                        <div class="label">下跌月数</div>
                        <div class="value" style="color: #27ae60;">{negative.get('count', 0)}</div>
                    </div>
                    <div class="info-item">
                        <div class="label">平均跌幅</div>
                        <div class="value" style="color: #27ae60;">{negative.get('mean', 0):.2f}%</div>
                    </div>
                    <div class="info-item">
                        <div class="label">中位数跌幅</div>
                        <div class="value" style="color: #27ae60;">{negative.get('median', 0):.2f}%</div>
                    </div>
                    <div class="info-item">
                        <div class="label">最大跌幅</div>
                        <div class="value" style="color: #27ae60;">{negative.get('min', 0):.2f}%</div>
                    </div>
                </div>
            </div>
        </div>
        """
    

    
    def _generate_positive_periods_table(self) -> str:
        """生成收益周期分析表格（正收益和负收益）"""
        return f"""
        {self._generate_holding_warning_section()}
        """

    def _generate_multi_period_returns_table(self) -> str:
        """生成多周期涨跌幅统计表格"""
        multi_period = self.analysis.get('multi_period_returns', {})
        
        # 构建表格行
        rows = ""
        period_order = ['1天', '3天', '1周', '1月', '半年', '1年']
        
        for period in period_order:
            data = multi_period.get(period, {})
            pos = data.get('positive', {})
            neg = data.get('negative', {})
            total = data.get('total_samples', 0)
            
            rows += f"""
                <tr>
                    <td style="padding: 10px; border-bottom: 1px solid #eee; font-weight: 600;">{period}</td>
                    <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: center;">{total}</td>
                    <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: center; color: #e74c3c;">{pos.get('count', 0)}</td>
                    <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: center; color: #e74c3c;">{pos.get('mean', 0):.2f}%</td>
                    <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: center; color: #e74c3c;">{pos.get('median', 0):.2f}%</td>
                    <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: center; color: #e74c3c; font-weight: 600;">{pos.get('max', 0):.2f}%</td>
                    <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: center; color: #27ae60;">{neg.get('count', 0)}</td>
                    <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: center; color: #27ae60;">{neg.get('mean', 0):.2f}%</td>
                    <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: center; color: #27ae60;">{neg.get('median', 0):.2f}%</td>
                    <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: center; color: #27ae60; font-weight: 600;">{neg.get('min', 0):.2f}%</td>
                </tr>
            """
        
        return f"""
        <div style="background: white; padding: 24px; border-radius: 12px; margin-bottom: 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
            <p style="font-size: 12px; color: #666; margin-bottom: 16px;">
                统计历史上按不同间隔周期（1天、3天、1周、1月、半年、1年）持有后的涨跌幅分布，正收益和负收益分开统计。使用不重叠窗口计算。
            </p>
            <div style="overflow-x: auto;">
                <table style="width: 100%; border-collapse: collapse; font-size: 13px;">
                    <thead>
                        <tr style="background: #3498db; color: white;">
                            <th style="padding: 12px; text-align: left; border-radius: 8px 0 0 0;">间隔周期</th>
                            <th style="padding: 12px; text-align: center;">样本数</th>
                            <th style="padding: 12px; text-align: center;">上涨次数</th>
                            <th style="padding: 12px; text-align: center;">上涨均值</th>
                            <th style="padding: 12px; text-align: center;">上涨中位</th>
                            <th style="padding: 12px; text-align: center;">最大涨幅</th>
                            <th style="padding: 12px; text-align: center;">下跌次数</th>
                            <th style="padding: 12px; text-align: center;">下跌均值</th>
                            <th style="padding: 12px; text-align: center;">下跌中位</th>
                            <th style="padding: 12px; text-align: center; border-radius: 0 8px 0 0;">最大跌幅</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows}
                    </tbody>
                </table>
            </div>
        </div>
        """
    
    def _generate_holding_warning_section(self) -> str:
        """生成持有预警信息板块"""
        return_periods = self.analysis.get('return_periods', {})
        reversal = return_periods.get('reversal', {})
        
        # 反转天数数据
        pos_to_neg = reversal.get('positive_to_negative', {})
        neg_to_pos = reversal.get('negative_to_positive', {})
        
        return f"""
        <div style="margin-top: 24px; background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%); padding: 24px; border-radius: 12px; border-left: 5px solid #ff6b6b;">
            <h3 style="color: #c0392b; margin-bottom: 16px; display: flex; align-items: center;">
                <span style="font-size: 24px; margin-right: 8px;">⚠️</span>
                持有预警与策略建议
            </h3>
            
            <!-- 反转天数分析（核心价值） -->
            <div style="background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; border: 2px solid #e74c3c;">
                <h4 style="color: #c0392b; margin-bottom: 16px; font-size: 16px;">🔄 收益反转天数分析（核心指标）</h4>
                <p style="font-size: 12px; color: #666; margin-bottom: 16px; line-height: 1.6;">
                    <strong>定义：</strong>从某一天买入开始，持有收益为正/负的状态平均持续多久会发生反转。<br>
                    例如：正转负平均{pos_to_neg.get('avg_days', 0):.0f}天，意味着如果你今天买入后收益为正，平均{pos_to_neg.get('avg_days', 0):.0f}天后这个正收益状态会转为负收益状态。
                </p>
                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px;">
                    <div style="background: linear-gradient(135deg, #ff6b6b 0%, #ee5a5a 100%); color: white; padding: 16px; border-radius: 8px; text-align: center;">
                        <div style="font-size: 28px; font-weight: 700;">{pos_to_neg.get('avg_days', 0):.0f}天</div>
                        <div style="font-size: 13px; margin-top: 4px;">正转负平均天数</div>
                        <div style="font-size: 11px; margin-top: 8px; opacity: 0.9;">中位数: {pos_to_neg.get('median_days', 0):.0f}天 | 最大: {pos_to_neg.get('max_days', 0):.0f}天</div>
                        <div style="font-size: 11px; opacity: 0.8;">基于 {pos_to_neg.get('count', 0)} 次反转统计</div>
                    </div>
                    <div style="background: linear-gradient(135deg, #27ae60 0%, #229954 100%); color: white; padding: 16px; border-radius: 8px; text-align: center;">
                        <div style="font-size: 28px; font-weight: 700;">{neg_to_pos.get('avg_days', 0):.0f}天</div>
                        <div style="font-size: 13px; margin-top: 4px;">负转正平均天数</div>
                        <div style="font-size: 11px; margin-top: 8px; opacity: 0.9;">中位数: {neg_to_pos.get('median_days', 0):.0f}天 | 最大: {neg_to_pos.get('max_days', 0):.0f}天</div>
                        <div style="font-size: 11px; opacity: 0.8;">基于 {neg_to_pos.get('count', 0)} 次反转统计</div>
                    </div>
                </div>
            </div>
            
            <!-- 策略建议 -->
            <div style="background: white; padding: 16px; border-radius: 8px;">
                <h4 style="color: #c0392b; margin-bottom: 12px;">📋 持有策略建议</h4>
                <div style="font-size: 13px; line-height: 1.8; color: #333;">
                    <p><strong>🔴 警惕期：</strong>持有 <span style="color: #e74c3c; font-weight: bold;">{pos_to_neg.get('avg_days', 0):.0f}天</span>（正转负平均）后需开始关注，历史上正收益状态平均在此时间后转为负收益。</p>
                    <p><strong>🟡 参考：</strong>正转负最大曾持续 <span style="color: #f39c12; font-weight: bold;">{pos_to_neg.get('max_days', 0):.0f}天</span>，负转正最大曾持续 <span style="color: #27ae60; font-weight: bold;">{neg_to_pos.get('max_days', 0):.0f}天</span>。</p>
                </div>
            </div>
        </div>
        """
    
    def _generate_extremes_table(self) -> str:
        """生成极值表格"""
        extremes = self.analysis.get('extremes', {})
        max_data = extremes.get('max', {})
        min_data = extremes.get('min', {})
        
        return f"""
        <table>
            <thead>
                <tr>
                    <th>类型</th>
                    <th>净值</th>
                    <th>日期</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>历史最高</td>
                    <td class="positive">{max_data.get('value', 0):.4f}</td>
                    <td>{max_data.get('date', '-')}</td>
                </tr>
                <tr>
                    <td>历史最低</td>
                    <td class="negative">{min_data.get('value', 0):.4f}</td>
                    <td>{min_data.get('date', '-')}</td>
                </tr>
            </tbody>
        </table>
        """
    
    def _get_trend_chart_data(self) -> str:
        """获取净值走势图数据"""
        net_worth = self.fund_data.get('net_worth_trend', [])
        data = [[item['x'], item['y']] for item in net_worth]
        return json.dumps(data)
    
    def _get_monthly_chart_data(self) -> str:
        """获取月度图表数据"""
        monthly = self.analysis.get('monthly_returns', {})
        details = monthly.get('monthly_details', {})
        categories = list(details.keys())
        values = [v['return'] for v in details.values()]
        return json.dumps({'categories': categories, 'values': values})


def main():
    parser = argparse.ArgumentParser(description='基金数据分析工具')
    parser.add_argument('--code', required=True, help='基金代码')
    parser.add_argument('--input', required=True, help='输入JS文件路径')
    parser.add_argument('--output', required=True, help='输出HTML文件路径')
    args = parser.parse_args()
    
    # 读取JS文件
    with open(args.input, 'r', encoding='utf-8') as f:
        js_content = f.read()
    
    # 解析数据
    parser = FundDataParser(js_content)
    fund_data = parser.parse()
    
    # 分析数据
    analyzer = FundAnalyzer(fund_data)
    monthly_analysis = analyzer.analyze_monthly_returns()
    return_periods = analyzer.find_return_periods()
    multi_period_returns = analyzer.analyze_multi_period_returns()
    
    analysis_results = {
        'monthly_returns': monthly_analysis,
        'return_periods': return_periods,
        'multi_period_returns': multi_period_returns,
        'max_drawdown': analyzer.calculate_max_drawdown(),
        'volatility': analyzer.calculate_volatility(),
        'extremes': analyzer.get_price_extremes()
    }
    
    # 保存分析结果JSON（供Agent读取）
    json_output = args.output.replace('.html', '_analysis.json')
    with open(json_output, 'w', encoding='utf-8') as f:
        json.dump({
            'fund_info': {
                'name': fund_data.get('name'),
                'code': fund_data.get('code'),
                'rate': fund_data.get('rate'),
                'min_amount': fund_data.get('min_amount')
            },
            'returns': {
                '1月': fund_data.get('return_1m'),
                '3月': fund_data.get('return_3m'),
                '6月': fund_data.get('return_6m'),
                '1年': fund_data.get('return_1y')
            },
            'analysis': analysis_results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"分析结果已保存: {json_output}")
    
    # 生成HTML报告
    report_gen = HTMLReportGenerator(fund_data, analysis_results)
    html_content = report_gen.generate()
    
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"HTML报告已生成: {args.output}")


if __name__ == '__main__':
    main()
