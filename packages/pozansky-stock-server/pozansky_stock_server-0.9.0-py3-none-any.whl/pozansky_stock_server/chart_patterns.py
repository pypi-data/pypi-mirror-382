import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Tuple, Any
from scipy import stats
import warnings
from scipy.signal import argrelextrema

class ChartPatterns:
    def __init__(self):
        self.patterns_info = {
            "CONTINUATION": [
                "对称三角形", "上升三角形", "下降三角形", "旗形", "三角旗形", "矩形整理"
            ],
            "REVERSAL": [
                "头肩顶", "头肩底", "双顶", "双底", "三重顶", "三重底", "圆弧顶", "圆弧底"
            ],
            "BREAKOUT": [
                "上升通道突破", "下降通道突破", "支撑位突破", "阻力位突破"
            ]
        }
        
        # 降低最小K线数量要求
        self.min_bars_required = {
            "triangle": 15,      # 三角形至少15根K线
            "head_shoulders": 20, # 头肩形态至少20根K线
            "double_top_bottom": 15, # 双顶双底至少15根K线
            "flag": 10,          # 旗形至少10根K线
            "channel": 15        # 通道至少15根K线
        }

    def _find_peaks_valleys(self, prices: np.ndarray, order: int = 2) -> Tuple[np.ndarray, np.ndarray]:
        """寻找价格的高点和低点 - 降低order提高检测率"""
        try:
            # 寻找局部高点
            peaks = argrelextrema(prices, np.greater, order=order)[0]
            # 寻找局部低点
            valleys = argrelextrema(prices, np.less, order=order)[0]
            
            return peaks, valleys
        except:
            return np.array([]), np.array([])

    def _calculate_trend_lines(self, highs: np.ndarray, lows: np.ndarray) -> Dict:
        """计算趋势线 - 降低要求"""
        result = {}
        
        try:
            x = np.arange(len(highs))
            
            # 使用稳健的线性回归
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                
                # 高点趋势线 - 降低数据点要求
                if len(highs) >= 3:
                    high_slope, high_intercept, high_r, _, _ = stats.linregress(x, highs)
                    result['high_trend'] = {
                        'slope': high_slope,
                        'intercept': high_intercept,
                        'r_squared': high_r**2
                    }
                
                # 低点趋势线 - 降低数据点要求
                if len(lows) >= 3:
                    low_slope, low_intercept, low_r, _, _ = stats.linregress(x, lows)
                    result['low_trend'] = {
                        'slope': low_slope,
                        'intercept': low_intercept,
                        'r_squared': low_r**2
                    }
                    
        except Exception as e:
            print(f"[WARN] 趋势线计算失败: {e}")
            
        return result

    def _detect_triangle_patterns(self, df: pd.DataFrame) -> List[Dict]:
        """检测三角形形态 - 大幅降低条件"""
        patterns = []
        
        if len(df) < self.min_bars_required["triangle"]:
            return patterns
        
        # 使用固定数量的K线进行分析
        analysis_bars = min(30, len(df))
        data = df.tail(analysis_bars).copy()
        data_start_idx = len(df) - analysis_bars
        
        highs = data['high'].values
        lows = data['low'].values
        
        # 寻找高点和低点 - 降低order
        peaks, valleys = self._find_peaks_valleys(highs, order=2), self._find_peaks_valleys(lows, order=2)
        
        if len(peaks[0]) < 2 or len(valleys[0]) < 2:
            return patterns
        
        peaks = peaks[0]
        valleys = valleys[0]
        
        # 计算趋势线
        trend_data = self._calculate_trend_lines(highs[peaks], lows[valleys])
        
        if not trend_data:
            return patterns
        
        high_trend = trend_data.get('high_trend', {})
        low_trend = trend_data.get('low_trend', {})
        
        if not high_trend or not low_trend:
            return patterns
        
        current_price = data['close'].iloc[-1]
        avg_price = (highs.mean() + lows.mean()) / 2
        
        # 1. 对称三角形 - 大幅降低条件
        if (high_trend['r_squared'] > 0.3 and low_trend['r_squared'] > 0.3 and
            high_trend['slope'] < -0.0005 and low_trend['slope'] > 0.0005):
            
            breakout_direction = "向上" if current_price > avg_price else "向下"
            
            x_points = np.array([data_start_idx, len(df)-1])
            upper_line = high_trend['intercept'] + high_trend['slope'] * np.array([0, analysis_bars-1])
            lower_line = low_trend['intercept'] + low_trend['slope'] * np.array([0, analysis_bars-1])
            
            patterns.append({
                "name": "对称三角形",
                "type": "CONTINUATION",
                "confidence": 0.6,  # 降低置信度要求
                "description": "高点和低点趋势线收敛，波动逐渐减小",
                "breakout_direction": breakout_direction,
                "target_price": current_price * (1.08 if breakout_direction == "向上" else 0.92),
                "duration_bars": analysis_bars,
                "volume_trend": "收缩",
                "draw_lines": {
                    "upper_line": {"x": x_points.tolist(), "y": upper_line.tolist(), "style": "dashed", "color": "red"},
                    "lower_line": {"x": x_points.tolist(), "y": lower_line.tolist(), "style": "dashed", "color": "blue"}
                }
            })
        
        # 2. 上升三角形 - 降低条件
        if (low_trend['r_squared'] > 0.4 and low_trend['slope'] > 0.001 and
            np.std(highs[peaks]) / np.mean(highs[peaks]) < 0.05):  # 放宽波动要求
            
            resistance_level = np.mean(highs[peaks])
            x_points = np.array([data_start_idx, len(df)-1])
            resistance_line = np.full_like(x_points, resistance_level)
            support_line = low_trend['intercept'] + low_trend['slope'] * np.array([0, analysis_bars-1])
            
            patterns.append({
                "name": "上升三角形",
                "type": "BULLISH",
                "confidence": 0.65,
                "description": "水平阻力线，上升支撑线，买方力量逐渐增强",
                "breakout_direction": "向上",
                "target_price": resistance_level * 1.1,
                "duration_bars": analysis_bars,
                "volume_trend": "收缩后放量",
                "draw_lines": {
                    "resistance_line": {"x": x_points.tolist(), "y": resistance_line.tolist(), "style": "dashed", "color": "red"},
                    "support_line": {"x": x_points.tolist(), "y": support_line.tolist(), "style": "dashed", "color": "blue"}
                }
            })
        
        # 3. 下降三角形 - 降低条件
        if (high_trend['r_squared'] > 0.4 and high_trend['slope'] < -0.001 and
            np.std(lows[valleys]) / np.mean(lows[valleys]) < 0.05):  # 放宽波动要求
            
            support_level = np.mean(lows[valleys])
            x_points = np.array([data_start_idx, len(df)-1])
            support_line = np.full_like(x_points, support_level)
            resistance_line = high_trend['intercept'] + high_trend['slope'] * np.array([0, analysis_bars-1])
            
            patterns.append({
                "name": "下降三角形",
                "type": "BEARISH",
                "confidence": 0.65,
                "description": "水平支撑线，下降阻力线，卖方力量逐渐增强",
                "breakout_direction": "向下",
                "target_price": support_level * 0.9,
                "duration_bars": analysis_bars,
                "volume_trend": "收缩后放量",
                "draw_lines": {
                    "support_line": {"x": x_points.tolist(), "y": support_line.tolist(), "style": "dashed", "color": "blue"},
                    "resistance_line": {"x": x_points.tolist(), "y": resistance_line.tolist(), "style": "dashed", "color": "red"}
                }
            })
        
        return patterns

    def _detect_head_shoulders(self, df: pd.DataFrame) -> List[Dict]:
        """检测头肩形态 - 大幅简化"""
        patterns = []
        
        if len(df) < self.min_bars_required["head_shoulders"]:
            return patterns
        
        analysis_bars = min(25, len(df))
        data = df.tail(analysis_bars).copy()
        data_start_idx = len(df) - analysis_bars
        
        highs = data['high'].values
        lows = data['low'].values
        closes = data['close'].values
        
        # 寻找高点和低点 - 降低要求
        peaks, valleys = self._find_peaks_valleys(highs, order=2), self._find_peaks_valleys(lows, order=2)
        
        if len(peaks[0]) < 3 or len(valleys[0]) < 2:
            return patterns
        
        peaks = peaks[0]
        valleys = valleys[0]
        
        # 简化头肩顶检测
        for i in range(len(peaks) - 2):
            left_shoulder_idx = data_start_idx + peaks[i]
            head_idx = data_start_idx + peaks[i + 1]
            right_shoulder_idx = data_start_idx + peaks[i + 2]
            
            left_shoulder_price = highs[peaks[i]]
            head_price = highs[peaks[i + 1]]
            right_shoulder_price = highs[peaks[i + 2]]
            
            # 大幅降低条件：头部比肩膀高即可
            if (head_price > left_shoulder_price and head_price > right_shoulder_price and
                abs(left_shoulder_price - right_shoulder_price) / head_price < 0.05):  # 肩膀高度相近
                
                # 简单计算颈线
                neckline_valleys = valleys[np.where((valleys > peaks[i]) & (valleys < peaks[i + 2]))[0]]
                if len(neckline_valleys) > 0:
                    neckline_level = np.mean(lows[neckline_valleys])
                    
                    current_close = closes[-1]
                    neckline_break = current_close < neckline_level
                    
                    draw_lines = {
                        "left_shoulder": {"x": [left_shoulder_idx], "y": [left_shoulder_price], "style": "circle", "color": "red"},
                        "head": {"x": [head_idx], "y": [head_price], "style": "circle", "color": "red"},
                        "right_shoulder": {"x": [right_shoulder_idx], "y": [right_shoulder_price], "style": "circle", "color": "red"},
                        "neckline": {"x": [left_shoulder_idx, right_shoulder_idx], "y": [neckline_level, neckline_level], "style": "dashed", "color": "blue"}
                    }
                    
                    patterns.append({
                        "name": "头肩顶",
                        "type": "BEARISH",
                        "confidence": 0.7,
                        "description": "头部高于左右肩，预示可能反转下跌",
                        "neckline_break": neckline_break,
                        "neckline_level": neckline_level,
                        "target_price": neckline_level - (head_price - neckline_level) * 0.8,
                        "duration_bars": right_shoulder_idx - left_shoulder_idx + 1,
                        "draw_lines": draw_lines
                    })
                    break
        
        # 简化头肩底检测
        for i in range(len(valleys) - 2):
            left_shoulder_idx = data_start_idx + valleys[i]
            head_idx = data_start_idx + valleys[i + 1]
            right_shoulder_idx = data_start_idx + valleys[i + 2]
            
            left_shoulder_price = lows[valleys[i]]
            head_price = lows[valleys[i + 1]]
            right_shoulder_price = lows[valleys[i + 2]]
            
            # 大幅降低条件：头部比肩膀低即可
            if (head_price < left_shoulder_price and head_price < right_shoulder_price and
                abs(left_shoulder_price - right_shoulder_price) / abs(head_price) < 0.05):
                
                # 简单计算颈线
                neckline_peaks = peaks[np.where((peaks > valleys[i]) & (peaks < valleys[i + 2]))[0]]
                if len(neckline_peaks) > 0:
                    neckline_level = np.mean(highs[neckline_peaks])
                    
                    current_close = closes[-1]
                    neckline_break = current_close > neckline_level
                    
                    draw_lines = {
                        "left_shoulder": {"x": [left_shoulder_idx], "y": [left_shoulder_price], "style": "circle", "color": "green"},
                        "head": {"x": [head_idx], "y": [head_price], "style": "circle", "color": "green"},
                        "right_shoulder": {"x": [right_shoulder_idx], "y": [right_shoulder_price], "style": "circle", "color": "green"},
                        "neckline": {"x": [left_shoulder_idx, right_shoulder_idx], "y": [neckline_level, neckline_level], "style": "dashed", "color": "blue"}
                    }
                    
                    patterns.append({
                        "name": "头肩底",
                        "type": "BULLISH",
                        "confidence": 0.7,
                        "description": "头部低于左右肩，预示可能反转上涨",
                        "neckline_break": neckline_break,
                        "neckline_level": neckline_level,
                        "target_price": neckline_level + (neckline_level - head_price) * 0.8,
                        "duration_bars": right_shoulder_idx - left_shoulder_idx + 1,
                        "draw_lines": draw_lines
                    })
                    break
        
        return patterns




    def _detect_double_patterns(self, df: pd.DataFrame) -> List[Dict]:
        """检测双顶双底形态 - 严格五个点，强调两个顶/底价格水平接近"""
        patterns = []
        
        min_required = self.min_bars_required.get("double_top_bottom", 10)
        if len(df) < min_required:
            return patterns

        analysis_bars = min(60, len(df))  # 增加分析范围
        data = df.tail(analysis_bars).copy()
        data_start_idx = len(df) - analysis_bars

        highs = data['high'].values
        lows = data['low'].values
        closes = data['close'].values

        print(f"[DEBUG] 双顶双底检测: 分析{analysis_bars}根K线")

        # 获取局部极值点（峰和谷）
        try:
            peak_indices = self._find_peaks_valleys(highs, order=3)[0]  # 更稳定
            valley_indices = self._find_peaks_valleys(lows, order=3)[0]
        except Exception as e:
            print(f"[ERROR] 极值检测失败: {e}")
            return patterns

        if len(peak_indices) < 2 or len(valley_indices) < 2:
            return patterns

        # 合并并排序所有极值点
        extrema = []
        for i in peak_indices:
            extrema.append(('peak', i, highs[i]))
        for i in valley_indices:
            extrema.append(('valley', i, lows[i]))
        
        extrema.sort(key=lambda x: x[1])  # 按时间排序

        # 提取交替序列（去除非交替点）
        alternating = []
        for typ, idx, price in extrema:
            if not alternating or alternating[-1][0] != typ:
                alternating.append((typ, idx, price))
            else:
                # 同类型保留更极端者
                if typ == 'peak' and price > alternating[-1][2]:
                    alternating[-1] = (typ, idx, price)
                elif typ == 'valley' and price < alternating[-1][2]:
                    alternating[-1] = (typ, idx, price)

        print(f"[DEBUG] 交替极值: {[(t, i, f'{p:.2f}') for t,i,p in alternating]}")

        n = len(alternating)

        # ======================================
        # 🔻 检测双顶 M型: 谷-峰-谷-峰-谷
        # ======================================
        for i in range(n - 4):
            seq = alternating[i:i+5]
            types = [s[0] for s in seq]
            if types != ['valley', 'peak', 'valley', 'peak', 'valley']:
                continue

            v1_idx, p1_idx, v2_idx, p2_idx, v3_idx = [s[1] for s in seq]
            v1_p, p1_p, v2_p, p2_p, v3_p = [s[2] for s in seq]

            if not (v1_idx < p1_idx < v2_idx < p2_idx < v3_idx):
                continue

            print(f"[DEBUG] 双顶候选: V1({v1_idx},{v1_p:.2f})→P1({p1_idx},{p1_p:.2f})→V2({v2_idx},{v2_p:.2f})→P2({p2_idx},{p2_p:.2f})→V3({v3_idx},{v3_p:.2f})")

            # ✅ 核心条件1: 两个高点价格非常接近（< 1.8%）
            peak_diff = abs(p1_p - p2_p) / max(p1_p, p2_p)
            if peak_diff > 0.018:  # 更严格
                print(f"[DEBUG] ❌ 高点差异过大: {peak_diff:.2%}")
                continue

            # ✅ 核心条件2: 第二个低点 V2 不显著低于 V1（防止是下降双顶）
            if v2_p < v1_p * 0.98:  # V2 比 V1 低超过 2%
                print(f"[DEBUG] ❌ V2 过低: {v2_p:.2f} < {v1_p:.2f}")
                continue

            # ✅ 颈线 = V1 和 V2 的最低价（支撑位）
            neckline_level = min(v1_p, v2_p)

            # 突破判定：当前价格是否跌破颈线
            current_close = closes[-1]
            neckline_break = current_close < neckline_level

            # ✅ 趋势背景：P1 前有上升趋势（简单判断）
            if p1_idx < 5:
                continue
            avg_high_before = np.mean(highs[p1_idx-5:p1_idx])
            if p1_p < avg_high_before * 1.02:  # 缺乏明显上涨
                continue

            print(f"[DEBUG] ✅ 双顶确认! 高点差{peak_diff:.2%}, 颈线={neckline_level:.2f}, 突破={neckline_break}")

            # 转换为全局索引
            v1_f, p1_f, v2_f, p2_f, v3_f = (data_start_idx + idx for idx in [v1_idx, p1_idx, v2_idx, p2_idx, v3_idx])

            # 双顶的五个点标记：顶用红色，底用绿色
            draw_lines = {
                "m_shape": {
                    "x": [v1_f, p1_f, v2_f, p2_f, v3_f],
                    "y": [v1_p, p1_p, v2_p, p2_p, v3_p],
                    "style": "solid", "color": "red", "marker": "o"
                },
                "neckline": {
                    "x": [v1_f, v2_f],
                    "y": [neckline_level, neckline_level],
                    "style": "dashed", "color": "blue"
                },
                # 单独标记五个点，顶用红色，底用绿色
                "v1_point": {"x": [v1_f], "y": [v1_p], "style": "marker", "color": "green", "marker": "o", "markersize": 8},
                "p1_point": {"x": [p1_f], "y": [p1_p], "style": "marker", "color": "red", "marker": "o", "markersize": 8},
                "v2_point": {"x": [v2_f], "y": [v2_p], "style": "marker", "color": "green", "marker": "o", "markersize": 8},
                "p2_point": {"x": [p2_f], "y": [p2_p], "style": "marker", "color": "red", "marker": "o", "markersize": 8},
                "v3_point": {"x": [v3_f], "y": [v3_p], "style": "marker", "color": "green", "marker": "o", "markersize": 8}
            }

            patterns.append({
                "name": "双顶",
                "type": "BEARISH",
                "confidence": 0.85,
                "description": "两个高点价格接近，形成M顶，跌破颈线支撑，趋势反转",
                "neckline_break": neckline_break,
                "neckline_level": neckline_level,
                "target_price": neckline_level - (p1_p - neckline_level),
                "duration_bars": v3_idx - v1_idx + 1,
                "volume_pattern": "第二个顶部缩量，确认抛压减弱",
                "draw_lines": draw_lines
            })
            break  # 只取第一个

        # ======================================
        # 🔺 检测双底 W型: 峰-谷-峰-谷-峰
        # ======================================
        for i in range(n - 4):
            seq = alternating[i:i+5]
            types = [s[0] for s in seq]
            if types != ['peak', 'valley', 'peak', 'valley', 'peak']:
                continue

            p1_idx, v1_idx, p2_idx, v2_idx, p3_idx = [s[1] for s in seq]
            p1_p, v1_p, p2_p, v2_p, p3_p = [s[2] for s in seq]

            if not (p1_idx < v1_idx < p2_idx < v2_idx < p3_idx):
                continue

            print(f"[DEBUG] 双底候选: P1({p1_idx},{p1_p:.2f})→V1({v1_idx},{v1_p:.2f})→P2({p2_idx},{p2_p:.2f})→V2({v2_idx},{v2_p:.2f})→P3({p3_idx},{p3_p:.2f})")

            # ✅ 核心条件1: 两个低点价格非常接近（< 1.8%）
            bottom_diff = abs(v1_p - v2_p) / max(v1_p, v2_p)
            if bottom_diff > 0.018:
                print(f"[DEBUG] ❌ 低点差异过大: {bottom_diff:.2%}")
                continue

            # ✅ 核心条件2: 第二个高点 P2 不显著高于 P1（防止是上升双底）
            if p2_p > p1_p * 1.02:
                print(f"[DEBUG] ❌ P2 过高: {p2_p:.2f} > {p1_p:.2f}")
                continue

            # ✅ 颈线 = P1 和 P2 的最高价（阻力位）
            neckline_level = max(p1_p, p2_p)

            # 突破判定：当前收盘价是否突破颈线
            current_close = closes[-1]
            neckline_break = current_close > neckline_level

            # ✅ 趋势背景：V1 前有下跌趋势
            if v1_idx < 5:
                continue
            avg_low_before = np.mean(lows[v1_idx-5:v1_idx])
            if v1_p > avg_low_before * 0.98:
                continue

            print(f"[DEBUG] ✅ 双底确认! 低点差{bottom_diff:.2%}, 颈线={neckline_level:.2f}, 突破={neckline_break}")

            p1_f, v1_f, p2_f, v2_f, p3_f = (data_start_idx + idx for idx in [p1_idx, v1_idx, p2_idx, v2_idx, p3_idx])

            # 双底的五个点标记：顶用红色，底用绿色
            draw_lines = {
                "w_shape": {
                    "x": [p1_f, v1_f, p2_f, v2_f, p3_f],
                    "y": [p1_p, v1_p, p2_p, v2_p, p3_p],
                    "style": "solid", "color": "green", "marker": "o"
                },
                "neckline": {
                    "x": [p1_f, p2_f],
                    "y": [neckline_level, neckline_level],
                    "style": "dashed", "color": "blue"
                },
                # 单独标记五个点，顶用红色，底用绿色
                "p1_point": {"x": [p1_f], "y": [p1_p], "style": "marker", "color": "red", "marker": "o", "markersize": 8},
                "v1_point": {"x": [v1_f], "y": [v1_p], "style": "marker", "color": "green", "marker": "o", "markersize": 8},
                "p2_point": {"x": [p2_f], "y": [p2_p], "style": "marker", "color": "red", "marker": "o", "markersize": 8},
                "v2_point": {"x": [v2_f], "y": [v2_p], "style": "marker", "color": "green", "marker": "o", "markersize": 8},
                "p3_point": {"x": [p3_f], "y": [p3_p], "style": "marker", "color": "red", "marker": "o", "markersize": 8}
            }

            patterns.append({
                "name": "双底",
                "type": "BULLISH",
                "confidence": 0.85,
                "description": "两个低点价格接近，形成W底，突破颈线阻力，趋势反转",
                "neckline_break": neckline_break,
                "neckline_level": neckline_level,
                "target_price": neckline_level + (neckline_level - v1_p),
                "duration_bars": p3_idx - p1_idx + 1,
                "volume_pattern": "第二个底部缩量，确认抛压枯竭",
                "draw_lines": draw_lines
            })
            break

        print(f"[DEBUG] 共检测到 {len(patterns)} 个有效形态")
        return patterns












    def _detect_channel_patterns(self, df: pd.DataFrame) -> List[Dict]:
        """检测通道形态 - 简化版本"""
        patterns = []
        
        if len(df) < self.min_bars_required["channel"]:
            return patterns
        
        analysis_bars = min(20, len(df))
        data = df.tail(analysis_bars).copy()
        data_start_idx = len(df) - analysis_bars
        
        highs = data['high'].values
        lows = data['low'].values
        closes = data['close'].values
        
        # 简单线性回归
        x = np.arange(len(data))
        
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            try:
                high_slope, high_intercept, high_r, _, _ = stats.linregress(x, highs)
                low_slope, low_intercept, low_r, _, _ = stats.linregress(x, lows)
            except:
                return patterns
        
        # 大幅降低通道检测条件
        if high_r > 0.4 and low_r > 0.4:  # 降低相关性要求
            
            # 计算通道线
            x_points = np.array([data_start_idx, len(df)-1])
            upper_line = high_intercept + high_slope * np.array([0, analysis_bars-1])
            lower_line = low_intercept + low_slope * np.array([0, analysis_bars-1])
            
            draw_lines = {
                "upper_channel": {"x": x_points.tolist(), "y": upper_line.tolist(), "style": "dashed", "color": "red"},
                "lower_channel": {"x": x_points.tolist(), "y": lower_line.tolist(), "style": "dashed", "color": "blue"}
            }
            
            if high_slope > 0.0005:  # 上升通道
                patterns.append({
                    "name": "上升通道",
                    "type": "BULLISH",
                    "confidence": 0.6,
                    "description": "价格在上升通道内运行",
                    "duration_bars": analysis_bars,
                    "draw_lines": draw_lines
                })
            elif high_slope < -0.0005:  # 下降通道
                patterns.append({
                    "name": "下降通道",
                    "type": "BEARISH",
                    "confidence": 0.6,
                    "description": "价格在下降通道内运行",
                    "duration_bars": analysis_bars,
                    "draw_lines": draw_lines
                })
            else:  # 水平通道
                patterns.append({
                    "name": "矩形整理",
                    "type": "NEUTRAL",
                    "confidence": 0.55,
                    "description": "价格在水平通道内整理",
                    "duration_bars": analysis_bars,
                    "draw_lines": draw_lines
                })
        
        return patterns

    def _detect_support_resistance(self, df: pd.DataFrame) -> List[Dict]:
        """检测支撑阻力突破 - 简化版本"""
        patterns = []
        
        if len(df) < 10:
            return patterns
        
        current_price = df['close'].iloc[-1]
        current_volume = df['volume'].iloc[-1]
        
        # 简单计算支撑阻力位
        support_level = df['low'].tail(10).min()
        resistance_level = df['high'].tail(10).max()
        avg_volume = df['volume'].tail(10).mean()
        
        # 阻力位突破 - 降低条件
        if (current_price > resistance_level * 1.02 and  # 2%突破即可
            current_volume > avg_volume * 0.8):  # 成交量要求降低
            
            patterns.append({
                "name": "阻力位突破",
                "type": "BULLISH",
                "confidence": 0.7,
                "description": "价格突破近期阻力位",
                "breakout_level": resistance_level,
                "target_price": current_price * 1.05,
                "volume_confirmation": current_volume > avg_volume
            })
        
        # 支撑位突破 - 降低条件
        elif (current_price < support_level * 0.98 and  # 2%跌破即可
              current_volume > avg_volume * 0.8):
            
            patterns.append({
                "name": "支撑位突破",
                "type": "BEARISH",
                "confidence": 0.7,
                "description": "价格跌破近期支撑位",
                "breakout_level": support_level,
                "target_price": current_price * 0.95,
                "volume_confirmation": current_volume > avg_volume
            })
        
        return patterns

    def detect_chart_patterns(self, df: pd.DataFrame) -> Dict[str, List[Dict]]:
        """检测所有图表形态 - 主函数"""
        if df is None or len(df) < 15:
            return {"CONTINUATION": [], "REVERSAL": [], "BREAKOUT": []}
        
        # 分别检测各类形态
        triangle_patterns = self._detect_triangle_patterns(df)
        head_shoulder_patterns = self._detect_head_shoulders(df)
        double_patterns = self._detect_double_patterns(df)
        channel_patterns = self._detect_channel_patterns(df)
        breakout_patterns = self._detect_support_resistance(df)
        
        # 分类整理
        continuation_patterns = triangle_patterns + channel_patterns
        reversal_patterns = head_shoulder_patterns + double_patterns
        
        # 进一步降低置信度过滤
        continuation_patterns = [p for p in continuation_patterns if p.get('confidence', 0) > 0.5]
        reversal_patterns = [p for p in reversal_patterns if p.get('confidence', 0) > 0.5]
        breakout_patterns = [p for p in breakout_patterns if p.get('confidence', 0) > 0.5]
        
        return {
            "CONTINUATION": continuation_patterns,
            "REVERSAL": reversal_patterns,
            "BREAKOUT": breakout_patterns
        }