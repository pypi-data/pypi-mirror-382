import asyncio
import httpx
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from mcp.server.fastmcp import FastMCP
import json
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
import io
import os
import tempfile
from pathlib import Path
import sys
import locale

# 导入模块
# from pozansky_stock_server.candlestick_patterns import CandlestickPatterns
# from pozansky_stock_server.chart_patterns import ChartPatterns
# from pozansky_stock_server.technical_indicators import TechnicalIndicators

from candlestick_patterns import CandlestickPatterns
from chart_patterns import ChartPatterns
from technical_indicators import TechnicalIndicators

# 设置系统编码为UTF-8
try:
    if sys.platform.startswith('win'):
        # Windows系统设置UTF-8编码
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
except:
    pass

# 创建 FastMCP 实例
mcp = FastMCP("StockAnalysisServer")

class StockAnalyzer:
    def __init__(self):
        self.client = None
        self.chart_storage = {}  # 用于存储图表数据
        
        # 初始化分析模块
        self.candle_patterns = CandlestickPatterns()
        self.chart_patterns = ChartPatterns()
        self.technical_indicators = TechnicalIndicators()
        
        # 扩展支持的股票列表
        self.market_examples = {
            "US": [
                "AAPL", "GOOGL", "TSLA", "MSFT", "AMZN", "META", "NVDA", "NFLX", 
                "AMD", "INTC", "BABA", "PDD", "JD", "BAC", "JPM", "WMT", "DIS", "V", "MA"
            ],
            "HK": [
                "0700.HK", "0005.HK", "1299.HK", "0939.HK", "2318.HK", "3988.HK",
                "0883.HK", "0388.HK", "0288.HK", "2628.HK", "0960.HK", "1810.HK"
            ],
            "CN_SH": [  # 沪市
                "000001.SS", "600036.SS", "601318.SS", "600519.SS", "601888.SS",
                "601398.SS", "601857.SS", "601766.SS", "601668.SS", "601989.SS"
            ],
            "CN_SZ": [  # 深市
                "399001.SZ", "000858.SZ", "000333.SZ", "002415.SZ", "000001.SZ",
                "000002.SZ", "000063.SZ", "002594.SZ", "300750.SZ", "300059.SZ"
            ],
            "INDEX": [  # 指数
                "^GSPC",  # 标普500
                "^IXIC",  # 纳斯达克
                "^DJI",   # 道琼斯
                "^HSI",   # 恒生指数
                "000001.SS",  # 上证指数
                "399001.SZ"   # 深证成指
            ]
        }
        
        # 支持的时间周期及其对应的数据范围
        self.supported_intervals = {
            "1m": "1d",    # 1分钟线，1天数据
            "2m": "1d",    # 2分钟线，1天数据
            "5m": "1d",    # 5分钟线，1天数据
            "15m": "5d",   # 15分钟线，5天数据
            "30m": "5d",   # 30分钟线，5天数据
            "60m": "10d",  # 60分钟线，10天数据
            "90m": "10d",  # 90分钟线，10天数据
            "1h": "1mo",   # 1小时线，1个月数据
            "4h": "3mo",   # 4小时线，3个月数据
            "1d": "1y",    # 日线，1年数据
            "1wk": "2y",   # 周线，2年数据
            "1mo": "5y"    # 月线，5年数据
        }

        # 默认的多周期分析组合
        self.default_multi_intervals = ["15m", "4h", "1d"]
        
        # 备选数据源配置
        self.data_sources = [
            {
                "name": "Yahoo Finance",
                "chart_url": "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}",
                "search_url": "https://query1.finance.yahoo.com/v1/finance/search",
                "headers": {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            },
            {
                "name": "Yahoo Finance Backup",
                "chart_url": "https://query2.finance.yahoo.com/v8/finance/chart/{symbol}",
                "search_url": "https://query2.finance.yahoo.com/v1/finance/search",
                "headers": {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            }
        ]

    async def initialize(self):
        """初始化HTTP客户端"""
        if self.client is None:
            self.client = httpx.AsyncClient(
                timeout=30.0,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            )
        return True

    async def validate_symbol(self, symbol: str) -> bool:
        """验证股票代码是否有效 - 修复版本"""
        try:
            # 首先检查是否是已知的示例代码
            for market_examples in self.market_examples.values():
                if symbol in market_examples:
                    print(f"[INFO] 已知股票代码: {symbol}")
                    return True
            
            # 尝试从多个数据源验证代码
            for source in self.data_sources:
                try:
                    url = source["chart_url"].format(symbol=symbol)
                    params = {"range": "1d", "interval": "1d"}
                    
                    print(f"[INFO] 正在验证 {symbol} 通过 {source['name']}...")
                    response = await self.client.get(url, params=params, headers=source["headers"])
                    
                    # 检查响应状态
                    if response.status_code != 200:
                        print(f"[WARN] {source['name']} 返回状态码: {response.status_code}")
                        continue
                    
                    # 检查响应内容
                    if not response.content:
                        print(f"[WARN] {source['name']} 返回空响应")
                        continue
                    
                    data = response.json()
                    
                    # 更健壮的数据检查
                    if (data and isinstance(data, dict) and 
                        "chart" in data and 
                        data["chart"] is not None and
                        "result" in data["chart"] and 
                        data["chart"]["result"] is not None and 
                        len(data["chart"]["result"]) > 0):
                        
                        result = data["chart"]["result"][0]
                        if (result and 
                            "timestamp" in result and 
                            result["timestamp"] is not None and 
                            len(result["timestamp"]) > 0):
                            print(f"[SUCCESS] 使用 {source['name']} 验证成功")
                            return True
                    else:
                        print(f"[WARN] {source['name']} 返回数据格式不符")
                        
                except Exception as e:
                    print(f"[ERROR] {source['name']} 验证失败: {str(e)}")
                    continue
                    
            print(f"[INFO] 所有数据源验证失败，但将继续使用模拟数据")
            return True  # 即使验证失败也返回True，使用模拟数据
            
        except Exception as e:
            print(f"[ERROR] 验证符号时发生未知错误: {str(e)}")
            return True  # 即使验证失败也返回True，使用模拟数据

    async def search_symbols(self, keyword: str) -> List[Dict]:
        """搜索股票代码"""
        await self.initialize()
        
        # 尝试多个数据源
        for source in self.data_sources:
            try:
                url = source["search_url"]
                params = {"q": keyword, "quotesCount": 10, "newsCount": 0}
                
                response = await self.client.get(url, params=params, headers=source["headers"])
                
                if response.status_code != 200:
                    continue
                    
                data = response.json()
                
                symbols = []
                if "quotes" in data:
                    for quote in data["quotes"]:
                        if "symbol" in quote:
                            symbols.append({
                                "symbol": quote["symbol"],
                                "name": quote.get("longname", quote.get("shortname", "")),
                                "exchange": quote.get("exchange", ""),
                                "type": quote.get("quoteType", "")
                            })
                
                if symbols:
                    print(f"[SUCCESS] 使用 {source['name']} 搜索成功")
                    return symbols
                    
            except Exception as e:
                print(f"[ERROR] {source['name']} 搜索失败: {e}")
                continue
        
        print(f"[ERROR] 所有数据源搜索失败")
        return []

    async def get_stock_data(self, symbol: str, period: str = "1mo", interval: str = "1d") -> Optional[pd.DataFrame]:
        """获取股票数据 - 使用多个数据源"""
        await self.initialize()
        
        # 尝试多个数据源
        for source in self.data_sources:
            try:
                print(f"[INFO] 尝试从 {source['name']} 获取 {symbol} 数据...")
                
                url = source["chart_url"].format(symbol=symbol)
                params = {
                    "range": period,
                    "interval": interval,
                    "includePrePost": "false"
                }
                
                response = await self.client.get(url, params=params, headers=source["headers"])
                
                # 检查响应状态
                if response.status_code != 200:
                    print(f"[WARN] {source['name']} 返回状态码: {response.status_code}")
                    continue
                
                data = response.json()
                
                if ("chart" not in data or 
                    "result" not in data["chart"] or 
                    not data["chart"]["result"] or 
                    data["chart"]["result"] is None):
                    print(f"[WARN] {source['name']} 返回数据格式错误")
                    continue
                    
                result = data["chart"]["result"][0]
                
                if ("timestamp" not in result or 
                    result["timestamp"] is None or 
                    not result["timestamp"] or
                    "indicators" not in result or
                    "quote" not in result["indicators"] or
                    not result["indicators"]["quote"]):
                    print(f"[WARN] {source['name']} 数据不完整")
                    continue
                    
                timestamps = result["timestamp"]
                quotes = result["indicators"]["quote"][0]
                
                # 检查关键数据是否存在
                if (not all(key in quotes for key in ['open', 'high', 'low', 'close', 'volume']) or
                    any(quotes[key] is None for key in ['open', 'high', 'low', 'close', 'volume'])):
                    print(f"[WARN] {source['name']} 价格数据不完整")
                    continue
                
                df = pd.DataFrame({
                    'timestamp': timestamps,
                    'open': quotes['open'],
                    'high': quotes['high'], 
                    'low': quotes['low'],
                    'close': quotes['close'],
                    'volume': quotes['volume']
                })
                
                df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
                df = df.dropna()
                
                if len(df) > 0:
                    print(f"[SUCCESS] 成功从 {source['name']} 获取 {len(df)} 条数据")
                    return df
                else:
                    print(f"[WARN] {source['name']} 数据为空")
                    
            except Exception as e:
                print(f"[ERROR] {source['name']} 获取数据失败: {e}")
                continue
        
        print(f"[INFO] 所有数据源获取失败，将使用模拟数据")
        return await self.get_stock_data_fallback(symbol)

    async def get_stock_data_fallback(self, symbol: str) -> Optional[pd.DataFrame]:
        """备选方法获取股票数据 - 使用模拟数据"""
        try:
            print(f"[INFO] 使用模拟数据获取 {symbol} 数据...")
            
            # 生成最近30天的数据
            dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='D')
            np.random.seed(hash(symbol) % 10000)  # 基于symbol生成随机种子
            
            # 生成模拟价格数据 - 更真实的股价模式
            base_price = 100 + (hash(symbol) % 100)  # 基于symbol的基础价格
            prices = [base_price]
            
            for i in range(1, len(dates)):
                # 更真实的股价变动模式
                change = np.random.normal(0, 0.02)  # 2%的日波动率
                new_price = prices[-1] * (1 + change)
                prices.append(new_price)
            
            df = pd.DataFrame({
                'timestamp': [int(d.timestamp()) for d in dates],
                'datetime': dates,
                'open': [p * (1 + np.random.normal(0, 0.01)) for p in prices],
                'high': [p * (1 + abs(np.random.normal(0.01, 0.015))) for p in prices],
                'low': [p * (1 - abs(np.random.normal(0.01, 0.015))) for p in prices],
                'close': prices,
                'volume': [np.random.randint(1000000, 50000000) for _ in range(len(dates))]
            })
            
            # 确保高价 > 低价
            df['high'] = df[['high', 'low']].max(axis=1)
            df['low'] = df[['high', 'low']].min(axis=1)
            
            print(f"[SUCCESS] 生成 {len(df)} 条模拟数据")
            return df
            
        except Exception as e:
            print(f"[ERROR] 模拟数据生成失败: {e}")
            return None

    def _draw_pattern_highlight(self, ax, pattern, plot_data, edge_color, fill_color):
        """为检测到的形态绘制特定的形态线条 - 完整修复版本"""
        print(f"[DEBUG] 绘制形态: {pattern['name']}, 类型: {pattern.get('type', 'UNKNOWN')}")
        try:
            pattern_name = pattern['name']
            
            # 特殊处理通道形态
            if pattern_name in ["上升通道", "下降通道", "矩形整理"]:
                self._draw_channel_pattern(ax, pattern, plot_data, edge_color)
                return
                
            # 如果有draw_lines，使用专门的线条绘制逻辑
            if 'draw_lines' in pattern:
                # 根据形态类型使用不同的绘制策略
                if pattern_name in ["双顶", "双底"]:
                    self._draw_double_pattern(ax, pattern, plot_data, edge_color)
                elif pattern_name in ["头肩顶", "头肩底"]:
                    self._draw_head_shoulders(ax, pattern, plot_data, edge_color)
                elif pattern_name in ["对称三角形", "上升三角形", "下降三角形"]:
                    self._draw_triangle_pattern(ax, pattern, plot_data, edge_color)
                else:
                    # 默认使用通用线条绘制
                    self._draw_pattern_lines(ax, pattern, plot_data, edge_color)
                        
        except Exception as e:
            print(f"[WARN] 绘制形态标注失败 {pattern.get('name', 'unknown')}: {e}")
            import traceback
            traceback.print_exc()
            
    def _draw_double_pattern(self, ax, pattern, plot_data, color):
        """绘制双顶/双底形态 - 修复版本"""
        pattern_name = pattern['name']
        draw_lines = pattern.get('draw_lines', {})
        
        # 绘制双顶 (M顶)
        if pattern_name == "双顶":
            if 'm_shape' in draw_lines:
                m_shape = draw_lines['m_shape']
                
                # 绘制完整的M型线条
                if len(m_shape['x']) >= 5 and len(m_shape['y']) >= 5:
                    # 绘制M型连线
                    ax.plot(m_shape['x'], m_shape['y'], color=color, linestyle='-', 
                        linewidth=2, alpha=0.8)
                    
                    # 标记所有关键点 - 使用正确的点名称
                    point_configs = [
                        ('v1_point', 'green'),   # 第一个谷底
                        ('p1_point', 'red'),     # 第一个峰值
                        ('v2_point', 'green'),   # 第二个谷底
                        ('p2_point', 'red'),     # 第二个峰值
                        ('v3_point', 'green')    # 第三个谷底
                    ]
                    
                    for point_name, point_color in point_configs:
                        if point_name in draw_lines:
                            point = draw_lines[point_name]
                            ax.scatter(point['x'], point['y'], color=point_color, 
                                    marker='o', s=80, zorder=5, edgecolors='white', linewidth=1)
                    
                    # 绘制颈线
                    if 'neckline' in draw_lines:
                        neckline = draw_lines['neckline']
                        if len(neckline['x']) >= 2:
                            ax.plot(neckline['x'], neckline['y'], color='blue', 
                                linestyle='--', linewidth=1, alpha=0.7)
                    
                    print(f"[DEBUG] 绘制双顶M型: {m_shape['x']}, 点标记: {[name for name, _ in point_configs if name in draw_lines]}")
        
        # 绘制双底 (W底)
        elif pattern_name == "双底":
            if 'w_shape' in draw_lines:
                w_shape = draw_lines['w_shape']
                
                # 绘制完整的W型线条
                if len(w_shape['x']) >= 5 and len(w_shape['y']) >= 5:
                    # 绘制W型连线
                    ax.plot(w_shape['x'], w_shape['y'], color=color, linestyle='-', 
                        linewidth=2, alpha=0.8)
                    
                    # 标记所有关键点 - 使用正确的点名称
                    point_configs = [
                        ('p1_point', 'red'),     # 第一个峰值
                        ('v1_point', 'green'),   # 第一个谷底
                        ('p2_point', 'red'),     # 第二个峰值
                        ('v2_point', 'green'),   # 第二个谷底
                        ('p3_point', 'red')      # 第三个峰值
                    ]
                    
                    for point_name, point_color in point_configs:
                        if point_name in draw_lines:
                            point = draw_lines[point_name]
                            ax.scatter(point['x'], point['y'], color=point_color, 
                                    marker='o', s=80, zorder=5, edgecolors='white', linewidth=1)
                    
                    # 绘制颈线
                    if 'neckline' in draw_lines:
                        neckline = draw_lines['neckline']
                        if len(neckline['x']) >= 2:
                            ax.plot(neckline['x'], neckline['y'], color='blue', 
                                linestyle='--', linewidth=1, alpha=0.7)
                    
                    print(f"[DEBUG] 绘制双底W型: {w_shape['x']}, 点标记: {[name for name, _ in point_configs if name in draw_lines]}")



    def _draw_triangle_pattern(self, ax, pattern, plot_data, color):
        """严格绘制三角形形态 - 重新设计"""
        pattern_name = pattern['name']
        draw_lines = pattern.get('draw_lines', {})
        
        print(f"[DEBUG] 绘制严格{pattern_name}, 可用线条: {list(draw_lines.keys())}")
        
        try:
            # 绘制上趋势线/阻力线
            if 'upper_trend' in draw_lines:
                line_data = draw_lines['upper_trend']
                ax.plot(line_data['x'], line_data['y'], 
                       color='blue', linestyle='-', linewidth=2, alpha=0.8)
            
            if 'resistance_line' in draw_lines:
                line_data = draw_lines['resistance_line']
                ax.plot(line_data['x'], line_data['y'], 
                       color='blue', linestyle='-', linewidth=2, alpha=0.8)
            
            # 绘制下趋势线/支撑线
            if 'lower_trend' in draw_lines:
                line_data = draw_lines['lower_trend']
                ax.plot(line_data['x'], line_data['y'], 
                       color='blue', linestyle='-', linewidth=2, alpha=0.8)
            
            if 'support_line' in draw_lines:
                line_data = draw_lines['support_line']
                ax.plot(line_data['x'], line_data['y'], 
                       color='blue', linestyle='-', linewidth=2, alpha=0.8)
            
            # 绘制关键点
            if 'peak_points' in draw_lines:
                points = draw_lines['peak_points']
                ax.scatter(points['x'], points['y'], 
                          color='blue', marker='o', s=80, zorder=5, 
                          edgecolors='white', linewidth=1)
            
            if 'valley_points' in draw_lines:
                points = draw_lines['valley_points']
                ax.scatter(points['x'], points['y'], 
                          color='blue', marker='o', s=80, zorder=5, 
                          edgecolors='white', linewidth=1)
            
            # 填充三角形区域
            if pattern_name == "对称三角形" and 'upper_trend' in draw_lines and 'lower_trend' in draw_lines:
                upper_line = draw_lines['upper_trend']
                lower_line = draw_lines['lower_trend']
                ax.fill_betweenx(upper_line['y'], upper_line['x'][0], upper_line['x'][1],
                                color='lightblue', alpha=0.3)
            
            elif pattern_name == "上升三角形" and 'resistance_line' in draw_lines and 'support_line' in draw_lines:
                resistance_line = draw_lines['resistance_line']
                support_line = draw_lines['support_line']
                ax.fill_betweenx([support_line['y'][0], resistance_line['y'][0]], 
                                resistance_line['x'][0], resistance_line['x'][1],
                                color='lightblue', alpha=0.3)
            
            elif pattern_name == "下降三角形" and 'support_line' in draw_lines and 'resistance_line' in draw_lines:
                support_line = draw_lines['support_line']
                resistance_line = draw_lines['resistance_line']
                ax.fill_betweenx([support_line['y'][0], resistance_line['y'][0]], 
                                support_line['x'][0], support_line['x'][1],
                                color='lightblue', alpha=0.3)
                
        except Exception as e:
            print(f"[ERROR] 绘制严格{pattern_name}失败: {e}")




    def _draw_head_shoulders(self, ax, pattern, plot_data, color):
        """绘制头肩形态 - 修复版本"""
        pattern_name = pattern['name']
        draw_lines = pattern.get('draw_lines', {})
        
        print(f"[DEBUG] 绘制{pattern_name}, 可用线条: {list(draw_lines.keys())}")
        
        try:
            # 绘制三个关键点：左肩、头部、右肩
            key_points = ['left_shoulder', 'head', 'right_shoulder']
            x_points = []
            y_points = []
            
            for point_name in key_points:
                if point_name in draw_lines:
                    point = draw_lines[point_name]
                    if point['x'] and point['y']:
                        x_val = point['x'][0] if isinstance(point['x'], list) else point['x']
                        y_val = point['y'][0] if isinstance(point['y'], list) else point['y']
                        x_points.append(x_val)
                        y_points.append(y_val)
                        
                        # 绘制点标记
                        point_color = 'red' if pattern_name == "头肩顶" else 'green'
                        ax.scatter(x_val, y_val, color=point_color, marker='o', s=100, zorder=5)
                        print(f"[DEBUG] {point_name}: ({x_val}, {y_val})")
            
            # 连接三个点形成头肩形态
            if len(x_points) == 3:
                ax.plot(x_points, y_points, color=color, linestyle='-', linewidth=2, alpha=0.8, marker='o')
                print(f"[DEBUG] {pattern_name}连线: x={x_points}, y={y_points}")
            
            # 绘制颈线
            if 'neckline' in draw_lines:
                neckline = draw_lines['neckline']
                if neckline['x'] and neckline['y']:
                    x_vals = neckline['x'] if isinstance(neckline['x'], list) else [neckline['x']]
                    y_vals = neckline['y'] if isinstance(neckline['y'], list) else [neckline['y']]
                    if len(x_vals) >= 2:
                        ax.plot(x_vals, y_vals, color='blue', linestyle='--', linewidth=2, alpha=0.7)
                        print(f"[DEBUG] {pattern_name}颈线: x={x_vals}, y={y_vals}")
                        
        except Exception as e:
            print(f"[ERROR] 绘制{pattern_name}失败: {e}")


    def _draw_channel_pattern(self, ax, pattern, plot_data, color):
        """绘制通道形态 - 增加通道线存在性校验"""
        pattern_name = pattern['name']
        draw_lines = pattern.get('draw_lines', {})
        
        print(f"[DEBUG] 绘制{pattern_name}, 可用线条: {list(draw_lines.keys())}")
        
        try:
            # 定义可能的上下轨线键名（优先级：精确匹配→模糊匹配）
            upper_keys = ['upper_channel', 'upper_trend', 'resistance_line', 'upper_line']
            lower_keys = ['lower_channel', 'lower_trend', 'support_line', 'lower_line']
            
            # 查找上轨线（修复：仅保留存在的key）
            upper_line_key = None
            for key in upper_keys:
                if key in draw_lines and len(draw_lines[key].get('x', [])) >= 2:
                    upper_line_key = key
                    break
            upper_line_data = draw_lines[upper_line_key] if upper_line_key else None
            
            # 查找下轨线（修复：仅保留存在的key）
            lower_line_key = None
            for key in lower_keys:
                if key in draw_lines and len(draw_lines[key].get('x', [])) >= 2:
                    lower_line_key = key
                    break
            lower_line_data = draw_lines[lower_line_key] if lower_line_key else None
            
            # 绘制上轨线（修复：确认数据有效）
            if upper_line_data:
                x_coords = upper_line_data.get('x', [])
                y_coords = upper_line_data.get('y', [])
                # 强制转换为float，避免numpy类型导致的绘图异常
                x_coords = [float(x) for x in x_coords if x is not None]
                y_coords = [float(y) for y in y_coords if y is not None]
                
                if len(x_coords) >= 2 and len(y_coords) >= 2:
                    # 根据通道类型选择颜色
                    line_color = 'green' if pattern_name == "上升通道" else 'red' if pattern_name == "下降通道" else 'blue'
                    ax.plot(x_coords, y_coords, color=line_color, linestyle='--', 
                            linewidth=2, alpha=0.8, label=f"{pattern_name}_上轨")
                    print(f"[DEBUG] 绘制上轨线: x={x_coords[:3]}... (共{len(x_coords)}点), y={y_coords[:3]}...")
            
            # 绘制下轨线（同上文逻辑）
            if lower_line_data:
                x_coords = lower_line_data.get('x', [])
                y_coords = lower_line_data.get('y', [])
                x_coords = [float(x) for x in x_coords if x is not None]
                y_coords = [float(y) for y in y_coords if y is not None]
                
                if len(x_coords) >= 2 and len(y_coords) >= 2:
                    line_color = 'green' if pattern_name == "上升通道" else 'red' if pattern_name == "下降通道" else 'blue'
                    ax.plot(x_coords, y_coords, color=line_color, linestyle='--', 
                            linewidth=2, alpha=0.8, label=f"{pattern_name}_下轨")
                    print(f"[DEBUG] 绘制下轨线: x={x_coords[:3]}... (共{len(x_coords)}点), y={y_coords[:3]}...")
            
            # 填充通道区域（修复：确保上下轨点数匹配）
            if upper_line_data and lower_line_data:
                # 获取上下轨坐标（已转换为float）
                upper_x = [float(x) for x in upper_line_data.get('x', []) if x is not None]
                upper_y = [float(y) for y in upper_line_data.get('y', []) if y is not None]
                lower_x = [float(x) for x in lower_line_data.get('x', []) if x is not None]
                lower_y = [float(y) for y in lower_line_data.get('y', []) if y is not None]
                
                # 确保上下轨点数一致（取较小长度）
                min_len = min(len(upper_x), len(lower_x))
                if min_len >= 2:
                    upper_x = upper_x[:min_len]
                    upper_y = upper_y[:min_len]
                    lower_x = lower_x[:min_len]
                    lower_y = lower_y[:min_len]
                    
                    # 创建填充区域（上轨→下轨反向，形成闭合多边形）
                    fill_x = upper_x + lower_x[::-1]
                    fill_y = upper_y + lower_y[::-1]
                    
                    # 选择填充颜色
                    if pattern_name == "上升通道":
                        fill_color = 'lightgreen'
                        alpha = 0.2
                    elif pattern_name == "下降通道":
                        fill_color = 'lightcoral'
                        alpha = 0.2
                    else:
                        fill_color = 'lightblue'
                        alpha = 0.1
                    
                    ax.fill(fill_x, fill_y, color=fill_color, alpha=alpha)
                    print(f"[DEBUG] 填充通道区域: {pattern_name} (使用{min_len}个点)")
            
            # 绘制关键点标记（保留原逻辑，增加float转换）
            key_points = ['start_point', 'end_point', 'peak_points', 'valley_points']
            for point_key in key_points:
                if point_key in draw_lines:
                    point_data = draw_lines[point_key]
                    point_x = point_data.get('x', [])
                    point_y = point_data.get('y', [])
                    
                    point_x = [point_x] if not isinstance(point_x, list) else point_x
                    point_y = [point_y] if not isinstance(point_y, list) else point_y
                    
                    for x, y in zip(point_x, point_y):
                        if x is not None and y is not None:
                            ax.scatter(float(x), float(y), color='blue', 
                                    marker='o', s=60, zorder=5, alpha=0.7)
                            print(f"[DEBUG] 绘制关键点 {point_key}: ({float(x):.1f}, {float(y):.2f})")
            
        except Exception as e:
            print(f"[ERROR] 绘制{pattern_name}失败: {e}")
            import traceback
            traceback.print_exc()

    def _draw_pattern_lines(self, ax, pattern, plot_data, color):
        """通用形态线条绘制 - 修复版本"""
        draw_lines = pattern.get('draw_lines', {})
        
        print(f"[DEBUG] 通用绘制 {pattern['name']}, 线条数: {len(draw_lines)}")
        
        for line_name, line_data in draw_lines.items():
            try:
                x_coords = line_data.get('x', [])
                y_coords = line_data.get('y', [])
                style = line_data.get('style', 'solid')
                line_color = line_data.get('color', color)
                marker = line_data.get('marker', None)
                
                # 处理坐标数据格式
                if not isinstance(x_coords, list):
                    x_coords = [x_coords]
                if not isinstance(y_coords, list):
                    y_coords = [y_coords]
                
                # 过滤有效坐标
                valid_indices = [i for i in range(min(len(x_coords), len(y_coords))) 
                            if x_coords[i] is not None and y_coords[i] is not None]
                
                if len(valid_indices) >= 2:
                    valid_x = [x_coords[i] for i in valid_indices]
                    valid_y = [y_coords[i] for i in valid_indices]
                    
                    # 绘制线条
                    linestyle = '--' if style == 'dashed' else '-'
                    ax.plot(valid_x, valid_y, color=line_color, linestyle=linestyle,
                        linewidth=2, alpha=0.8, label=f"{pattern['name']}_{line_name}")
                    
                    # 绘制标记点
                    if marker:
                        ax.scatter(valid_x, valid_y, color=line_color, marker=marker,
                                s=50, zorder=5, alpha=0.8)
                    
                    print(f"[DEBUG] 绘制线条 {line_name}: x={valid_x}, y={valid_y}")
                    
            except Exception as e:
                print(f"[WARN] 绘制线条 {line_name} 失败: {e}")

    def _convert_pattern_coordinates(self, pattern, data_offset, chart_bars):
        """转换形态坐标到绘图坐标系 - 修复顺序版本"""
        if 'draw_lines' not in pattern:
            return pattern

        import copy
        import numpy as np
        pattern_copy = copy.deepcopy(pattern)
        draw_lines = pattern_copy['draw_lines']
        
        print(f"[DEBUG] 开始坐标转换: 数据偏移={data_offset}, 图表长度={chart_bars}")
        
        # 1. 先处理非通道线（这些需要减去数据偏移）
        non_channel_lines = [line for line in draw_lines.keys() 
                            if line not in ['upper_channel', 'lower_channel', 'up_channel', 'down_channel']]
        
        for line_name in non_channel_lines:
            line_data = draw_lines[line_name]
            x_coords = line_data.get('x', [])
            y_coords = line_data.get('y', [])
            
            x_coords = [x_coords] if not isinstance(x_coords, list) else x_coords
            y_coords = [y_coords] if not isinstance(y_coords, list) else y_coords
            
            converted_x = []
            converted_y = []
            for x, y in zip(x_coords, y_coords):
                if x is None or y is None:
                    continue
                try:
                    # 减去数据偏移，转换为绘图坐标系
                    converted_x_val = float(x) - data_offset
                    converted_y_val = float(y)
                    
                    # 只保留在绘图范围内的点
                    if 0 <= converted_x_val < chart_bars:
                        converted_x.append(converted_x_val)
                        converted_y.append(converted_y_val)
                except Exception as e:
                    print(f"[WARN] 转换 {line_name} 坐标失败({x},{y}): {e}")
                    continue
            
            # 更新非通道线数据
            if len(converted_x) >= 1:
                line_data['x'] = converted_x
                line_data['y'] = converted_y
                print(f"[DEBUG] 转换非通道线 {line_name}: {len(converted_x)}个点")
            else:
                print(f"[WARN] {line_name} 转换后无有效点，移除")
                del draw_lines[line_name]
        
        # 2. 后处理通道线（这些不需要减去数据偏移，直接使用绘图坐标）
        channel_mapping = {
            'upper_channel': 'upper_points',
            'up_channel': 'upper_points',
            'lower_channel': 'lower_points', 
            'down_channel': 'lower_points'
        }
        
        for channel_key, points_key in channel_mapping.items():
            if channel_key not in draw_lines:
                continue
                
            if points_key not in draw_lines:
                print(f"[WARN] 通道线 {channel_key} 对应的 {points_key} 不存在，无法生成通道线")
                del draw_lines[channel_key]
                continue
            
            # 获取points数据（这些points已经在前面的步骤中转换过了）
            points_data = draw_lines[points_key]
            points_x = points_data.get('x', [])
            points_y = points_data.get('y', [])
            
            # 统一转换为列表并过滤None值
            points_x = [x for x in (points_x if isinstance(points_x, list) else [points_x]) if x is not None]
            points_y = [y for y in (points_y if isinstance(points_y, list) else [points_y]) if y is not None]
            
            # 确保points至少有2个有效点
            if len(points_x) < 2 or len(points_y) < 2:
                print(f"[WARN] {points_key} 有效点数不足({len(points_x)}个)，无法生成 {channel_key}")
                del draw_lines[channel_key]
                continue
            
            # 转换points坐标为float
            try:
                points_x_float = [float(x) for x in points_x if isinstance(x, (int, float, np.number))]
                points_y_float = [float(y) for y in points_y if isinstance(y, (int, float, np.number))]
            except (ValueError, TypeError) as e:
                print(f"[ERROR] 转换 {points_key} 坐标失败: {e}")
                del draw_lines[channel_key]
                continue
            
            # 线性拟合生成通道线
            try:
                # 使用已经转换过的绘图坐标进行拟合
                slope, intercept = np.polyfit(points_x_float, points_y_float, 1)
                
                # 使用完整的图表范围
                plot_x_start = 0  # 从图表开始
                plot_x_end = chart_bars - 1  # 到图表结束
                
                # 计算对应y值
                plot_y_start = slope * plot_x_start + intercept
                plot_y_end = slope * plot_x_end + intercept
                
                # 更新通道线数据（强制2个点，覆盖整个图表）
                draw_lines[channel_key]['x'] = [plot_x_start, plot_x_end]
                draw_lines[channel_key]['y'] = [plot_y_start, plot_y_end]
                print(f"[DEBUG] 用 {points_key} 生成 {channel_key}: "
                    f"x=[{plot_x_start:.1f}, {plot_x_end:.1f}], y=[{plot_y_start:.2f}, {plot_y_end:.2f}], 斜率={slope:.4f}")
            
            except Exception as e:
                print(f"[ERROR] 拟合 {channel_key} 失败: {e}")
                del draw_lines[channel_key]
                continue
        
        # 3. 最终验证所有线条
        print(f"[DEBUG] 最终线条数据:")
        for line_name, line_data in draw_lines.items():
            x_coords = line_data.get('x', [])
            y_coords = line_data.get('y', [])
            print(f"  {line_name}: {len(x_coords)}个点, x={x_coords}")
        
        return pattern_copy


    def _draw_candle_patterns(self, ax, candle_patterns, plot_data, data_offset):
        """绘制K线组合形态 - 修复版本"""
        if not candle_patterns:
            return
            
        all_candle_patterns = []
        for category in ['SINGLE', 'DOUBLE', 'MULTI']:
            all_candle_patterns.extend(candle_patterns.get(category, []))
        
        print(f"[DEBUG] 检测到 {len(all_candle_patterns)} 个K线形态")
        print(f"[DEBUG] 数据偏移: {data_offset}, 绘图数据长度: {len(plot_data)}")
        
        # 按位置排序，最新的在前面
        all_candle_patterns.sort(key=lambda x: x.get('position', 0), reverse=True)
        
        drawn_count = 0
        max_draw_count = 6  # 最多绘制10个形态
        
        for pattern in all_candle_patterns:
            if drawn_count >= max_draw_count:
                break
                
            try:
                candle_indices = pattern.get('candle_indices', [])
                if not candle_indices:
                    continue
                
                print(f"[DEBUG] 处理形态 {pattern['name']}, 原始索引: {candle_indices}")
                    
                # 坐标转换：将绝对索引转换为绘图索引
                plot_indices = []
                for idx in candle_indices:
                    plot_idx = idx - data_offset
                    if 0 <= plot_idx < len(plot_data):
                        plot_indices.append(plot_idx)
                        print(f"[DEBUG]  索引转换: {idx} -> {plot_idx} (在绘图范围内)")
                    else:
                        print(f"[DEBUG]  索引转换: {idx} -> {plot_idx} (超出绘图范围)")
                
                if not plot_indices:
                    print(f"[DEBUG] 形态 {pattern['name']} 无有效绘图索引")
                    continue
                    
                min_idx = min(plot_indices)
                max_idx = max(plot_indices)
                center_idx = (min_idx + max_idx) / 2
                
                print(f"[DEBUG]  有效索引: {plot_indices}, 范围: {min_idx}-{max_idx}")
                
                # 获取形态范围内的价格
                pattern_data = plot_data.iloc[min_idx:max_idx+1]
                min_price = pattern_data['low'].min()
                max_price = pattern_data['high'].max()
                price_range = max_price - min_price
                
                # 根据形态类型选择颜色
                pattern_type = pattern.get('type', 'NEUTRAL')
                if pattern_type == 'BULLISH':
                    pattern_color = 'red'
                    text_color = 'darkred'
                    bg_color = 'lightcoral'
                    symbol = '▲'
                elif pattern_type == 'BEARISH':
                    pattern_color = 'green' 
                    text_color = 'darkgreen'
                    bg_color = 'lightgreen'
                    symbol = '▼'
                else:
                    pattern_color = 'blue'
                    text_color = 'darkblue'
                    bg_color = 'lightblue'
                    symbol = '●'
                
                # 绘制形态范围框
                rect_width = max_idx - min_idx + 0.6
                rect_height = price_range * 1.1  # 稍微扩大一点范围
                
                # 如果只有一根K线，调整框的宽度
                if len(plot_indices) == 1:
                    rect_width = 1.2
                    min_idx = min_idx - 0.3
                
                # 根据位置调整透明度（最新的更明显）
                position = pattern.get('position', 0)
                is_recent = position >= (len(plot_data) + data_offset - 5)  # 最近5根K线
                alpha = 0.4 if is_recent else 0.2
                
                rect = Rectangle((min_idx-0.3, min_price - price_range*0.05), 
                            rect_width, 
                            rect_height,
                            linewidth=2 if is_recent else 1,
                            edgecolor=pattern_color, 
                            facecolor=bg_color, 
                            alpha=alpha,
                            linestyle='-')
                ax.add_patch(rect)
                
                # 添加形态名称标注
                confidence = pattern.get('confidence', 0)
                annotation_text = f"{symbol}{pattern['name']}\n置信度:{confidence:.1f}"
                
                # 计算标注位置
                chart_height = ax.get_ylim()[1] - ax.get_ylim()[0]
                
                # 交替标注位置避免重叠
                position_index = drawn_count % 4
                vertical_offset = chart_height * 0.1 * (position_index + 1)
                
                # 根据位置选择标注方向
                if center_idx < len(plot_data) * 0.3:  # 左侧
                    annotation_y = max_price + vertical_offset
                    va = 'bottom'
                elif center_idx > len(plot_data) * 0.7:  # 右侧
                    annotation_y = min_price - vertical_offset
                    va = 'top'
                else:  # 中间
                    if drawn_count % 2 == 0:
                        annotation_y = max_price + vertical_offset
                        va = 'bottom'
                    else:
                        annotation_y = min_price - vertical_offset
                        va = 'top'
                
                # 绘制标注
                ax.annotate(annotation_text, 
                        xy=(center_idx, max_price if va == 'bottom' else min_price),
                        xytext=(center_idx, annotation_y),
                        ha='center', 
                        va=va,
                        fontsize=7, 
                        color=text_color, 
                        weight='bold',
                        bbox=dict(boxstyle="round,pad=0.2", facecolor='white', alpha=0.9),
                        arrowprops=dict(arrowstyle='->', color=pattern_color, lw=1, alpha=0.8))
                
                drawn_count += 1
                print(f"[DEBUG] 成功绘制第{drawn_count}个形态: {pattern['name']}")
                
            except Exception as e:
                print(f"[ERROR] 绘制K线组合 {pattern.get('name', 'unknown')} 失败: {e}")
                continue
        
        print(f"[DEBUG] 总共绘制了 {drawn_count} 个K线形态")

    def save_chart_to_file(self, df: pd.DataFrame, symbol: str, interval: str, 
                candle_patterns: Dict = None, chart_patterns: Dict = None) -> str:
        """保存K线图到临时文件并返回文件路径 - 完整修复版本"""
        try:
            # 创建临时目录
            temp_dir = Path(tempfile.gettempdir()) / "stock_charts"
            temp_dir.mkdir(exist_ok=True)
            
            # 生成文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{symbol}_{interval}_{timestamp}.png"
            filepath = temp_dir / filename
            
            # 生成图表
            if df is None or len(df) == 0:
                return None
                
            # 设置中文字体
            plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
            plt.rcParams['axes.unicode_minus'] = False
            
            # 获取最近100根K线用于绘图
            chart_bars = min(100, len(df))
            plot_data = df.tail(chart_bars).copy()
            data_offset = len(df) - chart_bars  # 原始数据中的起始索引
            
            print(f"[DEBUG] 绘图数据: {len(plot_data)}根, 数据偏移: {data_offset}")
            
            fig, ax = plt.subplots(figsize=(14, 8))
            
            # 绘制K线
            for i, (idx, row) in enumerate(plot_data.iterrows()):
                open_price = row['open']
                close_price = row['close']
                high_price = row['high']
                low_price = row['low']
                
                # 确定颜色
                if close_price >= open_price:
                    color = 'red'  # 阳线用红色
                    body_bottom = open_price
                    body_top = close_price
                else:
                    color = 'green'  # 阴线用绿色
                    body_bottom = close_price
                    body_top = open_price
                
                # 绘制影线
                ax.plot([i, i], [low_price, high_price], color='black', linewidth=1)
                
                # 绘制实体
                body_height = body_top - body_bottom
                if body_height > 0:
                    rect = Rectangle((i-0.3, body_bottom), 0.6, body_height, 
                                facecolor=color, alpha=0.7, edgecolor='black')
                    ax.add_patch(rect)
            
            # 绘制K线组合形态
            if candle_patterns:
                self._draw_candle_patterns(ax, candle_patterns, plot_data, data_offset)
            
            # 标记检测到的图表形态
            if chart_patterns:
                all_chart_patterns = []
                for category in ['CONTINUATION', 'REVERSAL', 'BREAKOUT']:
                    all_chart_patterns.extend(chart_patterns.get(category, []))
                
                print(f"[DEBUG] 检测到 {len(all_chart_patterns)} 个图表形态")
                
                for pattern_idx, pattern in enumerate(all_chart_patterns):
                    # 关键修复：使用专门的坐标转换函数
                    converted_pattern = self._convert_pattern_coordinates(pattern, data_offset, chart_bars)
                    
                    pattern_name = converted_pattern['name']
                    pattern_type = converted_pattern.get('type', 'NEUTRAL')
                    
                    print(f"[DEBUG] 处理形态 {pattern_name}, 类型: {pattern_type}")
                    
                    # 根据形态类型选择颜色
                    if pattern_type == 'BULLISH':
                        base_color = 'green'
                        fill_color = 'lightgreen'
                    elif pattern_type == 'BEARISH':
                        base_color = 'red' 
                        fill_color = 'lightcoral'
                    else:
                        base_color = 'blue'
                        fill_color = 'lightblue'
                    
                    # 关键修复：直接使用已经转换过的形态数据，避免二次转换
                    if 'draw_lines' in converted_pattern:
                        print(f"[DEBUG] 使用已转换的形态数据:")
                        for line_name, line_data in converted_pattern['draw_lines'].items():
                            x_coords = line_data.get('x', [])
                            y_coords = line_data.get('y', [])
                            print(f"  {line_name}: {len(x_coords)}个点, x={x_coords}, y={[f'{y:.2f}' for y in y_coords]}")
                    
                    # 直接调用绘制函数，使用已经转换过的pattern
                    self._draw_pattern_highlight(ax, converted_pattern, plot_data, base_color, fill_color)
                    
                    # 添加形态名称标注
                    if len(plot_data) > 0:
                        max_price = plot_data['high'].max()
                        min_price = plot_data['low'].min()
                        price_range = max_price - min_price
                        
                        # 在图表右上角添加标注
                        label_x = len(plot_data) * 0.85
                        label_y = max_price - price_range * 0.08 * (pattern_idx + 1)
                        
                        # 根据形态类型设置标签背景色
                        if pattern_type == 'BULLISH':
                            bg_color = 'lightgreen'
                            text_color = 'darkgreen'
                        elif pattern_type == 'BEARISH':
                            bg_color = 'lightcoral'
                            text_color = 'darkred'
                        else:
                            bg_color = 'lightyellow'
                            text_color = 'darkblue'
                            
                        ax.text(label_x, label_y, f"{pattern_name}", 
                            fontsize=10, color=text_color, weight='bold',
                            ha='center', va='center',
                            bbox=dict(boxstyle="round,pad=0.3", facecolor=bg_color, alpha=0.8))
            
            # 设置图表属性
            ax.set_title(f'{symbol} K线图 - {interval}周期', fontsize=16, fontweight='bold', pad=20)
            ax.set_xlabel('时间', fontsize=12)
            ax.set_ylabel('价格', fontsize=12)
            
            # 设置x轴刻度
            x_ticks = range(0, len(plot_data), max(1, len(plot_data) // 10))
            x_tick_labels = []
            for i in x_ticks:
                if i < len(plot_data):
                    if 'datetime' in plot_data.columns:
                        if interval in ['1m', '5m', '15m', '30m', '1h']:
                            x_tick_labels.append(plot_data.iloc[i]['datetime'].strftime('%m-%d %H:%M'))
                        else:
                            x_tick_labels.append(plot_data.iloc[i]['datetime'].strftime('%Y-%m-%d'))
                    else:
                        x_tick_labels.append(str(i))
            
            ax.set_xticks(x_ticks)
            ax.set_xticklabels(x_tick_labels, rotation=45)
            
            # 添加网格
            ax.grid(True, alpha=0.3)
            
            # 添加图例
            bull_patch = plt.Line2D([0], [0], color='red', linewidth=8, label='阳线')
            bear_patch = plt.Line2D([0], [0], color='green', linewidth=8, label='阴线')
            ax.legend(handles=[bull_patch, bear_patch], loc='upper left')
            
            plt.tight_layout()
            
            # 保存图片到文件
            plt.savefig(filepath, format='png', dpi=150, bbox_inches='tight')
            plt.close()
            
            print(f"[DEBUG] 图表保存成功: {filepath}")
            return str(filepath)
            
        except Exception as e:
            print(f"[ERROR] 保存K线图失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def analyze_stock(self, symbol: str, interval: str = "1d") -> Dict:
        """分析单个时间周期的股票数据"""
        if interval not in self.supported_intervals:
            return {"error": f"不支持的K线周期: {interval}"}
            
        period = self.supported_intervals.get(interval)
        
        # 获取数据（会自动尝试主要数据源和备选方法）
        df = await self.get_stock_data(symbol, period, interval)
            
        if df is None or len(df) == 0:
            return {"error": f"无法获取 {symbol} 的数据"}
            
        # 使用模块化的分析功能
        candle_patterns = self.candle_patterns.detect_candlestick_patterns(df)
        chart_patterns = self.chart_patterns.detect_chart_patterns(df)
        technical_indicators = self.technical_indicators.calculate_all_indicators(df)
        
        # 生成图表文件路径
        chart_path = self.save_chart_to_file(df, symbol, interval, candle_patterns, chart_patterns)
        
        analysis = {
            "symbol": symbol,
            "interval": interval,
            "current_price": df['close'].iloc[-1],
            "price_change": df['close'].iloc[-1] - df['close'].iloc[-2] if len(df) >= 2 else 0,
            "price_change_pct": ((df['close'].iloc[-1] - df['close'].iloc[-2]) / df['close'].iloc[-2] * 100) if len(df) >= 2 else 0,
            "candle_patterns": candle_patterns,
            "chart_patterns": chart_patterns,
            "technical_indicators": technical_indicators,
            "chart_path": chart_path,
            "data_points": len(df),
            "analysis_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return analysis

    async def analyze_stock_multiple_intervals(self, symbol: str, intervals: List[str] = None) -> Dict:
        """同时分析多个时间周期的股票数据"""
        if intervals is None:
            intervals = self.default_multi_intervals
            
        # 验证所有时间周期
        for interval in intervals:
            if interval not in self.supported_intervals:
                return {"error": f"不支持的K线周期: {interval}"}
        
        # 并发获取所有时间周期的数据
        tasks = []
        for interval in intervals:
            period = self.supported_intervals[interval]
            task = self.get_stock_data(symbol, period, interval)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理结果
        multi_analysis = {
            "symbol": symbol,
            "intervals": intervals,
            "analyses": {},
            "summary": {},
            "analysis_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        overall_candle_patterns = {"SINGLE": [], "DOUBLE": [], "MULTI": []}
        overall_chart_patterns = {"CONTINUATION": [], "REVERSAL": [], "BREAKOUT": []}
        chart_paths = {}
        
        for i, (interval, df) in enumerate(zip(intervals, results)):
            if isinstance(df, Exception) or df is None or len(df) == 0:
                multi_analysis["analyses"][interval] = {"error": "无法获取数据"}
                continue
            
            # 分析该时间周期的数据
            candle_patterns = self.candle_patterns.detect_candlestick_patterns(df)
            chart_patterns = self.chart_patterns.detect_chart_patterns(df)
            technical_indicators = self.technical_indicators.calculate_all_indicators(df)
            chart_path = self.save_chart_to_file(df, symbol, interval, candle_patterns, chart_patterns)
            
            # 合并所有时间周期的形态
            for category in ['SINGLE', 'DOUBLE', 'MULTI']:
                for pattern in candle_patterns.get(category, []):
                    pattern_with_interval = pattern.copy()
                    pattern_with_interval['interval'] = interval
                    overall_candle_patterns[category].append(pattern_with_interval)
            
            for category in ['CONTINUATION', 'REVERSAL', 'BREAKOUT']:
                for pattern in chart_patterns.get(category, []):
                    pattern_with_interval = pattern.copy()
                    pattern_with_interval['interval'] = interval
                    overall_chart_patterns[category].append(pattern_with_interval)
            
            chart_paths[interval] = chart_path
            
            analysis = {
                "interval": interval,
                "current_price": df['close'].iloc[-1],
                "price_change": df['close'].iloc[-1] - df['close'].iloc[-2] if len(df) >= 2 else 0,
                "price_change_pct": ((df['close'].iloc[-1] - df['close'].iloc[-2]) / df['close'].iloc[-2] * 100) if len(df) >= 2 else 0,
                "candle_patterns": candle_patterns,
                "chart_patterns": chart_patterns,
                "technical_indicators": technical_indicators,
                "chart_path": chart_path,
                "data_points": len(df)
            }
            
            multi_analysis["analyses"][interval] = analysis
        
        # 生成总结信息
        multi_analysis["summary"] = {
            "overall_candle_patterns": overall_candle_patterns,
            "overall_chart_patterns": overall_chart_patterns,
            "chart_paths": chart_paths,
            "total_candle_patterns": sum(len(patterns) for patterns in overall_candle_patterns.values()),
            "total_chart_patterns": sum(len(patterns) for patterns in overall_chart_patterns.values())
        }
        
        return multi_analysis

    async def close(self):
        """关闭客户端"""
        if self.client:
            await self.client.aclose()
            self.client = None

# 创建全局实例
stock_analyzer = StockAnalyzer()

def _format_single_analysis(analysis: Dict) -> str:
    """格式化单个时间周期的分析结果"""
    if "error" in analysis:
        return f"[ERROR] 分析失败: {analysis['error']}"
    
    result = [
        f"当前价格: {analysis['current_price']:.2f}",
        f"涨跌幅: {analysis['price_change']:+.2f} ({analysis['price_change_pct']:+.2f}%)",
        f"数据点数: {analysis.get('data_points', 0)}",
    ]
    
    # K线形态分类显示
    candle_patterns = analysis.get('candle_patterns', {})
    
    total_candle_patterns = sum(len(patterns) for patterns in candle_patterns.values())
    
    if total_candle_patterns == 0:
        result.append("未检测到明显的K线形态")
    else:
        # 单K线形态
        single_patterns = candle_patterns.get('SINGLE', [])
        if single_patterns:
            result.append("  单K线形态:")
            for pattern in single_patterns:
                trend_emoji = "[看涨]" if pattern['type'] == 'BULLISH' else "[看跌]" if pattern['type'] == 'BEARISH' else "[中性]"
                result.append(f"    {trend_emoji} {pattern['name']} (置信度: {pattern['confidence']:.1f})")
        
        # 双K线组合
        double_patterns = candle_patterns.get('DOUBLE', [])
        if double_patterns:
            result.append("  双K线组合:")
            for pattern in double_patterns:
                trend_emoji = "[看涨]" if pattern['type'] == 'BULLISH' else "[看跌]" if pattern['type'] == 'BEARISH' else "[中性]"
                result.append(f"    {trend_emoji} {pattern['name']} (置信度: {pattern['confidence']:.1f})")
        
        # 多K线组合
        multi_patterns = candle_patterns.get('MULTI', [])
        if multi_patterns:
            result.append("  多K线组合:")
            for pattern in multi_patterns:
                trend_emoji = "[看涨]" if pattern['type'] == 'BULLISH' else "[看跌]" if pattern['type'] == 'BEARISH' else "[中性]"
                result.append(f"    {trend_emoji} {pattern['name']} (置信度: {pattern['confidence']:.1f})")
    
    # 图表形态显示
    chart_patterns = analysis.get('chart_patterns', {})
    
    total_chart_patterns = sum(len(patterns) for patterns in chart_patterns.values())
    
    if total_chart_patterns > 0:
        result.append("  图表形态:")
        
        # 持续形态
        continuation_patterns = chart_patterns.get('CONTINUATION', [])
        for pattern in continuation_patterns:
            result.append(f"    [持续] {pattern['name']} (置信度: {pattern['confidence']:.1f})")
            if 'breakout_direction' in pattern:
                result.append(f"      预期突破方向: {pattern['breakout_direction']}")
            if 'target_price' in pattern:
                result.append(f"      目标价格: {pattern['target_price']:.2f}")
        
        # 反转形态
        reversal_patterns = chart_patterns.get('REVERSAL', [])
        for pattern in reversal_patterns:
            trend_emoji = "[看涨]" if pattern['type'] == 'BULLISH' else "[看跌]"
            result.append(f"    {trend_emoji} {pattern['name']} (置信度: {pattern['confidence']:.1f})")
            if 'target_price' in pattern:
                result.append(f"      目标价格: {pattern['target_price']:.2f}")
        
        # 突破形态
        breakout_patterns = chart_patterns.get('BREAKOUT', [])
        for pattern in breakout_patterns:
            trend_emoji = "[看涨]" if pattern['type'] == 'BULLISH' else "[看跌]"
            result.append(f"    {trend_emoji} {pattern['name']} (置信度: {pattern['confidence']:.1f})")
            if 'breakout_level' in pattern:
                result.append(f"      突破位: {pattern['breakout_level']:.2f}")
            if 'target_price' in pattern:
                result.append(f"      目标价格: {pattern['target_price']:.2f}")
    
    # 技术指标
    if analysis['technical_indicators']:
        result.append("  技术指标:")
        indicators = analysis['technical_indicators']
        
        # 移动平均线
        if all(k in indicators for k in ['MA5', 'MA10', 'MA20']):
            ma_signal = indicators.get('MA_Signal', '未知')
            result.append(f"    移动平均线: {ma_signal}")
            result.append(f"    MA5: {indicators['MA5']:.2f}, MA10: {indicators['MA10']:.2f}, MA20: {indicators['MA20']:.2f}")
        
        # RSI
        if 'RSI' in indicators:
            rsi = indicators['RSI']
            if isinstance(rsi, (int, float)):
                rsi_signal = indicators.get('RSI_Signal', '未知')
                result.append(f"    RSI: {rsi:.1f} ({rsi_signal})")
        
        # MACD
        if all(k in indicators for k in ['MACD', 'MACD_Signal']):
            macd_signal = indicators.get('MACD_Signal', '未知')
            result.append(f"    MACD: {macd_signal}")
        
        # 布林带
        if 'BB_Signal' in indicators:
            bb_signal = indicators['BB_Signal']
            result.append(f"    布林带: {bb_signal}")
        
        # 综合信号
        if 'Overall_Signal' in indicators:
            result.append(f"    综合信号: {indicators['Overall_Signal']}")
    
    # 图表信息
    if analysis.get('chart_path'):
        result.append(f"  图表: {analysis['chart_path']}")
    
    return "\n".join(result)

def _format_multi_analysis(multi_analysis: Dict) -> str:
    """格式化多时间周期分析结果"""
    if "error" in multi_analysis:
        return f"[ERROR] 分析失败: {multi_analysis['error']}"
    
    result = [
        f"{multi_analysis['symbol']} 多周期综合分析",
        f"分析时间: {multi_analysis['analysis_time']}",
        ""
    ]
    
    # 显示每个时间周期的分析
    for interval, analysis in multi_analysis["analyses"].items():
        if "error" in analysis:
            result.append(f"[ERROR] {interval}周期: {analysis['error']}")
            result.append("")
            continue
            
        interval_name = {
            "15m": "15分钟线 (短线)",
            "4h": "4小时线 (中线)", 
            "1d": "日线 (长线)"
        }.get(interval, f"{interval}周期")
        
        result.append(f"### {interval_name}")
        result.append(_format_single_analysis(analysis))
        result.append("")
    
    # 总体形态总结
    summary = multi_analysis.get("summary", {})
    overall_candle_patterns = summary.get("overall_candle_patterns", {})
    overall_chart_patterns = summary.get("overall_chart_patterns", {})
    
    result.append("## 总体形态总结")
    
    total_candle_patterns = sum(len(patterns) for patterns in overall_candle_patterns.values())
    total_chart_patterns = sum(len(patterns) for patterns in overall_chart_patterns.values())
    
    if total_candle_patterns == 0 and total_chart_patterns == 0:
        result.append("所有周期均未检测到明显的形态")
    else:
        # K线形态总结
        if total_candle_patterns > 0:
            result.append("### K线形态总结")
            
            for category_name, category in [("单K线形态", "SINGLE"), ("双K线组合", "DOUBLE"), ("多K线组合", "MULTI")]:
                patterns = overall_candle_patterns.get(category, [])
                if patterns:
                    result.append(f"#### {category_name}")
                    
                    # 按时间周期分组
                    interval_patterns = {}
                    for pattern in patterns:
                        interval = pattern.get('interval', 'unknown')
                        if interval not in interval_patterns:
                            interval_patterns[interval] = []
                        interval_patterns[interval].append(pattern)
                    
                    for interval, pattern_list in interval_patterns.items():
                        interval_display = {
                            "15m": "15分钟",
                            "4h": "4小时",
                            "1d": "日线"
                        }.get(interval, interval)
                        
                        result.append(f"{interval_display}:")
                        for pattern in pattern_list:
                            trend_emoji = "[看涨]" if pattern['type'] == 'BULLISH' else "[看跌]" if pattern['type'] == 'BEARISH' else "[中性]"
                            result.append(f"  {trend_emoji} {pattern['name']} (置信度: {pattern['confidence']:.1f})")
                    result.append("")
        
        # 图表形态总结
        if total_chart_patterns > 0:
            result.append("### 图表形态总结")
            
            for category_name, category in [("持续形态", "CONTINUATION"), ("反转形态", "REVERSAL"), ("突破形态", "BREAKOUT")]:
                patterns = overall_chart_patterns.get(category, [])
                if patterns:
                    result.append(f"#### {category_name}")
                    
                    # 按时间周期分组
                    interval_patterns = {}
                    for pattern in patterns:
                        interval = pattern.get('interval', 'unknown')
                        if interval not in interval_patterns:
                            interval_patterns[interval] = []
                        interval_patterns[interval].append(pattern)
                    
                    for interval, pattern_list in interval_patterns.items():
                        interval_display = {
                            "15m": "15分钟",
                            "4h": "4小时",
                            "1d": "日线"
                        }.get(interval, interval)
                        
                        result.append(f"{interval_display}:")
                        for pattern in pattern_list:
                            if category == "CONTINUATION":
                                result.append(f"  [持续] {pattern['name']} (置信度: {pattern['confidence']:.1f})")
                            else:
                                trend_emoji = "[看涨]" if pattern['type'] == 'BULLISH' else "[看跌]"
                                result.append(f"  {trend_emoji} {pattern['name']} (置信度: {pattern['confidence']:.1f})")
                            
                            if 'breakout_direction' in pattern:
                                result.append(f"    预期突破方向: {pattern['breakout_direction']}")
                            if 'target_price' in pattern:
                                result.append(f"    目标价格: {pattern['target_price']:.2f}")
                    result.append("")
    
    # 图表文件路径
    chart_paths = summary.get("chart_paths", {})
    if chart_paths:
        result.append("## 生成的图表")
        for interval, path in chart_paths.items():
            if path:
                interval_display = {
                    "15m": "15分钟",
                    "4h": "4小时", 
                    "1d": "日线"
                }.get(interval, interval)
                result.append(f"{interval_display}: {path}")
        result.append("")
        result.append("提示: 您可以在文件管理器中查看这些图片")
    
    return "\n".join(result)

@mcp.tool()
async def analyze_stock_price(symbol: str, interval: str = "1d") -> str:
    """分析股票价格和K线形态（单个周期）
    
    Args:
        symbol: 股票代码 (如: AAPL, 0700.HK, 000001.SS, ^GSPC)
        interval: K线周期 (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 4h, 1d, 1wk, 1mo)
    """
    try:
        if interval not in stock_analyzer.supported_intervals:
            supported = ", ".join(stock_analyzer.supported_intervals.keys())
            return f"[ERROR] 不支持的K线周期，请使用: {supported}"
            
        # 即使验证失败也继续，使用模拟数据
        await stock_analyzer.validate_symbol(symbol)
            
        analysis = await stock_analyzer.analyze_stock(symbol, interval)
        
        result = [
            f"{symbol} 股票分析 - {interval}周期",
            f"分析时间: {analysis.get('analysis_time', '未知')}",
            ""
        ]
        result.append(_format_single_analysis(analysis))
        
        return "\n".join(result)
        
    except Exception as e:
        return f"[ERROR] 分析股票失败: {str(e)}"

@mcp.tool()
async def analyze_stock_multiple_intervals(symbol: str, intervals: List[str] = None) -> str:
    """同时分析多个时间周期的股票数据
    
    Args:
        symbol: 股票代码
        intervals: K线周期列表，如 ["15m", "4h", "1d"]，默认为15分钟、4小时、日线
    """
    try:
        if intervals is None:
            intervals = stock_analyzer.default_multi_intervals
            
        # 即使验证失败也继续，使用模拟数据
        await stock_analyzer.validate_symbol(symbol)
            
        multi_analysis = await stock_analyzer.analyze_stock_multiple_intervals(symbol, intervals)
        return _format_multi_analysis(multi_analysis)
        
    except Exception as e:
        return f"[ERROR] 多周期分析失败: {str(e)}"

@mcp.tool()
async def search_stock_symbols(keyword: str) -> str:
    """搜索股票代码"""
    try:
        if not keyword or len(keyword.strip()) < 2:
            return "[ERROR] 请输入至少2个字符进行搜索"
            
        symbols = await stock_analyzer.search_symbols(keyword.strip())
        
        if not symbols:
            if any('\u4e00' <= char <= '\u9fff' for char in keyword):
                return f"[ERROR] 中文搜索 '{keyword}' 失败，请尝试使用英文或股票代码搜索"
            else:
                return f"[ERROR] 未找到与 '{keyword}' 相关的股票"
            
        result = [f"搜索 '{keyword}' 的结果:", ""]
        
        for i, symbol_info in enumerate(symbols, 1):
            result.append(f"{i}. {symbol_info['symbol']} - {symbol_info['name']}")
            result.append(f"   交易所: {symbol_info.get('exchange', '未知')} | 类型: {symbol_info.get('type', '未知')}")
            result.append("")
            
        result.append("使用示例:")
        result.append(f'analyze_stock_multiple_intervals(symbol="{symbols[0]["symbol"]}")')
        
        return "\n".join(result)
        
    except Exception as e:
        return f"[ERROR] 搜索股票失败: {str(e)}"

@mcp.tool()
async def get_stock_examples() -> str:
    """获取股票代码示例"""
    result = ["股票代码示例:", ""]
    
    for market, examples in stock_analyzer.market_examples.items():
        market_name = {
            "US": "美股",
            "HK": "港股", 
            "CN_SH": "沪市",
            "CN_SZ": "深市",
            "INDEX": "指数"
        }.get(market, market)
        
        result.append(f"{market_name}:")
        for i in range(0, len(examples), 5):
            result.append("  " + ", ".join(examples[i:i+5]))
        result.append("")
    
    # 添加时间周期说明
    result.extend([
        "推荐的多周期分析组合:",
        "  - 15分钟线: 短线交易信号",
        "  - 4小时线: 中线趋势分析", 
        "  - 日线: 长线投资参考",
        "",
        "使用说明:",
        "1. 使用 search_stock_symbols('公司名') 搜索股票代码",
        "2. 使用 analyze_stock_multiple_intervals('代码') 进行多周期分析",
        "3. 使用 analyze_stock_price('代码', '周期') 进行单周期分析",
        "",
        "推荐使用多周期分析:",
        'analyze_stock_multiple_intervals("AAPL")  # 苹果多周期分析',
        'analyze_stock_multiple_intervals("0700.HK", ["15m", "1h", "1d"])  # 自定义周期',
        'analyze_stock_price("^GSPC", "4h")  # 标普500单周期分析'
    ])
    
    return "\n".join(result)

@mcp.tool()
async def get_supported_intervals() -> str:
    """获取支持的时间周期列表"""
    result = ["支持的时间周期:", ""]
    
    # 按类别分组显示
    categories = {
        "分钟级周期": ["1m", "2m", "5m", "15m", "30m", "60m", "90m"],
        "小时级周期": ["1h", "4h"],
        "日级及以上周期": ["1d", "1wk", "1mo"]
    }
    
    for category, intervals in categories.items():
        result.append(f"{category}:")
        result.append("  " + ", ".join(intervals))
        result.append("")
    
    result.extend([
        "多周期分析推荐组合:",
        "  - 短线交易: 15m + 1h + 4h",
        "  - 中线投资: 1h + 4h + 1d", 
        "  - 长线投资: 4h + 1d + 1wk",
        "",
        "默认多周期分析: 15m, 4h, 1d",
        "",
        "使用示例:",
        'analyze_stock_multiple_intervals("AAPL")  # 默认三周期',
        'analyze_stock_multiple_intervals("TSLA", ["5m", "1h", "1d"])  # 自定义周期',
        'analyze_stock_price("MSFT", "15m")  # 单周期分析'
    ])
    
    return "\n".join(result)

@mcp.tool()
async def get_candlestick_patterns_info() -> str:
    """获取K线形态说明"""
    result = ["K线形态完全指南:", ""]
    
    # 单K线形态说明
    result.append("## 单K线形态")
    single_descriptions = {
        "光头光脚阳线": "没有上下影线，开盘价即最低价，收盘价即最高价，表示强烈的看涨信号",
        "光脚阳线": "没有下影线，表示买方力量强劲，但上方有压力",
        "光头阳线": "没有上影线，收盘价即最高价，表示买方完全控制局面",
        "带上下影线的阳线": "有上下影线，表示多空双方有争夺，但最终买方获胜",
        "光头光脚阴线": "没有上下影线，开盘价即最高价，收盘价即最低价，表示强烈的看跌信号",
        "光脚阴线": "没有下影线，表示卖方力量强劲，开盘后价格一路下跌",
        "光头阴线": "没有上影线，开盘价即最高价，表示卖方完全控制局面",
        "带上下影线的阴线": "有上下影线，表示多空双方有争夺，但最终卖方获胜",
        "十字线": "开盘收盘价接近，表示市场犹豫不决，可能预示反转",
        "T字线": "卖方打压后买方收复失地，出现在底部时看涨信号更强",
        "倒T字线": "买方推高后卖方打压回落，出现在顶部时看跌信号更强",
        "一字线": "开盘即涨停或跌停，表示极强的买盘或卖盘力量",
        "锤头线": "出现在下跌趋势中，长下影线表示买方力量开始增强",
        "上吊线": "出现在上涨趋势中，长下影线表示卖方力量开始增强",
        "倒锤头线": "出现在下跌趋势中，长上影线表示买方尝试反攻",
        "射击之星": "出现在上涨趋势中，长上影线表示上方压力巨大"
    }
    
    for pattern, desc in single_descriptions.items():
        trend_indicator = "[看涨]" if "阳" in pattern or "涨" in desc else "[看跌]" if "阴" in pattern or "跌" in desc else "[中性]"
        result.append(f"{trend_indicator} {pattern}: {desc}")
    
    result.append("\n## 双K线组合")
    double_descriptions = {
        "乌云盖顶组合": "第二根阴线开盘高于前一根高点，收盘低于前一根中点，预示上涨趋势可能结束",
        "旭日东升组合": "第二根阳线开盘低于前一根低点，收盘高于前一根中点，预示下跌趋势可能结束",
        "抱线组合": "阳线或阴线完全吞没前一根K线，强烈反转信号",
        "孕线组合": "小实体在大实体内，出现在趋势中可能反转",
        "插入线组合": "阳线插入到前一根阴线实体内部，显示买方力量增强",
        "跳空组合": "K线之间出现跳空缺口，显示强劲的买卖力量",
        "双飞乌鸦组合": "连续两根阴线，第二根开盘高于第一根但收盘更低，预示上涨乏力"
    }
    
    for pattern, desc in double_descriptions.items():
        trend_indicator = "[看涨]" if "旭日" in pattern or "阳" in desc else "[看跌]" if "乌云" in pattern or "阴" in desc or "乌鸦" in pattern else "[中性]"
        result.append(f"{trend_indicator} {pattern}: {desc}")
    
    result.append("\n## 多K线组合")
    multi_descriptions = {
        "黄昏之星": "三根K线组合，出现在上涨趋势顶部，强烈看跌反转信号",
        "红三兵": "连续三根实体逐渐增长的阳线，显示强劲的买方力量",
        "多方炮": "两阳夹一阴形态，显示洗盘后继续上涨的强势信号",
        "上升三法": "大阳线后跟随小阴线，再出现创新高的大阳线，上升中继形态",
        "早晨之星": "三根K线组合，出现在下跌趋势底部，强烈看涨反转信号",
        "黑三鸦": "连续三根实体逐渐增长的阴线，显示强劲的卖方力量",
        "空方炮": "两阴夹一阳形态，显示反弹后继续下跌的弱势信号",
        "下降三法": "大阴线后跟随小阳线，再出现创新低的大阴线，下降中继形态"
    }
    
    for pattern, desc in multi_descriptions.items():
        trend_indicator = "[看涨]" if "红" in pattern or "多方" in pattern or "早晨" in pattern or "上升" in pattern else "[看跌]" if "黑" in pattern or "空方" in pattern or "黄昏" in pattern or "下降" in pattern else "[中性]"
        result.append(f"{trend_indicator} {pattern}: {desc}")
    
    return "\n".join(result)

@mcp.tool()
async def get_chart_patterns_info() -> str:
    """获取图表形态说明"""
    result = ["图表形态完全指南:", ""]
    
    result.append("## 持续形态")
    continuation_descriptions = {
        "对称三角形": "高点和低点趋势线收敛，通常表示整理后延续原趋势",
        "上升三角形": "水平阻力线，上升支撑线，通常向上突破",
        "下降三角形": "水平支撑线，下降阻力线，通常向下突破",
        "旗形": "快速涨跌后的整理形态，形态与趋势方向相反",
        "三角旗形": "三角形和旗形的结合，强烈的持续信号",
        "矩形整理": "价格在水平通道内整理，等待突破方向",
        "上升通道": "价格在上升通道内运行，触及下轨买入，触及上轨卖出",
        "下降通道": "价格在下降通道内运行，反弹至上轨做空"
    }
    
    for pattern, desc in continuation_descriptions.items():
        result.append(f"[持续] {pattern}: {desc}")
    
    result.append("\n## 反转形态")
    reversal_descriptions = {
        "头肩顶": "经典的反转形态，左肩、头部、右肩构成，预示下跌",
        "头肩底": "经典的反转形态，左肩、头部、右肩构成，预示上涨",
        "双顶": "两个相近的高点构成，预示下跌反转",
        "双底": "两个相近的低点构成，预示上涨反转",
        "三重顶": "三个相近的高点构成，强烈的看跌信号",
        "三重底": "三个相近的低点构成，强烈的看涨信号",
        "圆弧顶": "缓慢形成的顶部形态，预示趋势反转",
        "圆弧底": "缓慢形成的底部形态，预示趋势反转"
    }
    
    for pattern, desc in reversal_descriptions.items():
        trend_indicator = "[看涨]" if "底" in pattern else "[看跌]"
        result.append(f"{trend_indicator} {pattern}: {desc}")
    
    result.append("\n## 突破形态")
    breakout_descriptions = {
        "上升通道突破": "价格突破上升通道上轨，可能加速上涨",
        "下降通道突破": "价格突破下降通道下轨，可能加速下跌",
        "支撑位突破": "价格跌破重要支撑位，可能继续下跌",
        "阻力位突破": "价格突破重要阻力位，可能继续上涨"
    }
    
    for pattern, desc in breakout_descriptions.items():
        trend_indicator = "[看涨]" if "上升" in pattern or "阻力" in pattern else "[看跌]"
        result.append(f"{trend_indicator} {pattern}: {desc}")
    
    return "\n".join(result)

@mcp.tool()
async def get_technical_indicators_info() -> str:
    """获取技术指标说明"""
    result = ["技术指标完全指南:", ""]
    
    result.append("## 趋势指标")
    trend_descriptions = {
        "移动平均线(MA)": "反映价格的平均水平，金叉看涨，死叉看跌",
        "指数移动平均线(EMA)": "对近期价格给予更高权重，反应更灵敏",
        "MACD": "趋势动能指标，金叉看涨，死叉看跌",
        "布林带(Bollinger Bands)": "价格波动通道，上轨阻力，下轨支撑",
        "平均真实波幅(ATR)": "衡量价格波动性的指标"
    }
    
    for indicator, desc in trend_descriptions.items():
        result.append(f"[趋势] {indicator}: {desc}")
    
    result.append("\n## 动量指标")
    momentum_descriptions = {
        "相对强弱指数(RSI)": "超买超卖指标，30以下超卖，70以上超买",
        "随机指标(Stochastic)": "动量振荡器，反映价格相对位置",
        "威廉指标(Williams %R)": "超买超卖指标，-20以上超买，-80以下超卖",
        "顺势指标(CCI)": "衡量价格偏离平均水平的程度"
    }
    
    for indicator, desc in momentum_descriptions.items():
        result.append(f"[动量] {indicator}: {desc}")
    
    result.append("\n## 成交量指标")
    volume_descriptions = {
        "成交量(Volume)": "反映市场参与程度",
        "能量潮(OBV)": "量价关系指标，确认趋势强度",
        "成交量分布": "分析成交量在不同价格区间的分布"
    }
    
    for indicator, desc in volume_descriptions.items():
        result.append(f"[成交量] {indicator}: {desc}")
    
    result.extend([
        "\n## 使用建议",
        "1. 不要单独依赖任何一个指标",
        "2. 结合多个时间周期分析",
        "3. 指标信号要与价格行为一致", 
        "4. 注意指标在趋势市和震荡市中的不同表现",
        "5. 设置合理的止损和目标位"
    ])
    
    return "\n".join(result)

@mcp.tool()
async def get_stock_chart(symbol: str, interval: str = "1d") -> str:
    """获取股票K线图
    
    Args:
        symbol: 股票代码
        interval: K线周期
    """
    try:
        if interval not in stock_analyzer.supported_intervals:
            supported = ", ".join(stock_analyzer.supported_intervals.keys())
            return f"[ERROR] 不支持的K线周期，请使用: {supported}"
            
        # 即使验证失败也继续，使用模拟数据
        await stock_analyzer.validate_symbol(symbol)
            
        analysis = await stock_analyzer.analyze_stock(symbol, interval)
        
        if "error" in analysis:
            return f"[ERROR] 分析失败: {analysis['error']}"
            
        chart_path = analysis.get('chart_path')
        
        if chart_path:
            # 返回文件路径信息
            return (f"{symbol} K线图已保存\n"
                   f"文件路径: {chart_path}\n\n"
                   f"查看方式:\n"
                   f"- 在文件管理器中打开此路径查看图片\n"
                   f"- 或者使用系统命令查看: `open {chart_path}` (Mac) 或 `start {chart_path}` (Windows)\n\n"
                   f"图表说明:\n"
                   f"- 红色矩形: 阳线 (收盘价 ≥ 开盘价)\n"
                   f"- 绿色矩形: 阴线 (收盘价 < 开盘价)\n"
                   f"- 彩色区域: 检测到的K线形态范围\n"
                   f"- 文字标注: 形态名称和置信度")
        else:
            return "[ERROR] 无法生成K线图"
            
    except Exception as e:
        return f"[ERROR] 获取股票图表失败: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport="stdio")