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

    def _calculate_trend_lines(self, highs: np.ndarray, lows: np.ndarray, peaks, valleys) -> Dict:
        """计算趋势线 - 修复版本"""
        result = {}
        
        try:
            # 修复：使用正确的索引
            x_peaks = np.arange(len(peaks))
            x_valleys = np.arange(len(valleys))
            
            # 使用稳健的线性回归
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                
                # 高点趋势线 - 降低数据点要求
                if len(peaks) >= 2:
                    high_slope, high_intercept, high_r, _, _ = stats.linregress(x_peaks, highs[peaks])
                    result['high_trend'] = {
                        'slope': high_slope,
                        'intercept': high_intercept,
                        'r_squared': high_r**2
                    }
                    print(f"[DEBUG] 高点趋势: 斜率={high_slope:.6f}, R²={high_r**2:.3f}")
                
                # 低点趋势线 - 降低数据点要求
                if len(valleys) >= 2:
                    low_slope, low_intercept, low_r, _, _ = stats.linregress(x_valleys, lows[valleys])
                    result['low_trend'] = {
                        'slope': low_slope,
                        'intercept': low_intercept,
                        'r_squared': low_r**2
                    }
                    print(f"[DEBUG] 低点趋势: 斜率={low_slope:.6f}, R²={low_r**2:.3f}")
                        
        except Exception as e:
            print(f"[WARN] 趋势线计算失败: {e}")
            
        return result


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
        """检测通道形态 - 严格版本，必须有完整的上下轨线"""
        patterns = []
        
        if len(df) < 30:  # 最小30根K线，确保有足够数据
            return patterns
        
        # 使用所有可用数据
        data = df.copy()
        
        # 寻找关键的高点和低点
        highs = data['high'].values
        lows = data['low'].values
        
        # 使用滚动窗口寻找局部极值点
        window_size = max(5, len(data) // 15)  # 更大的窗口，减少噪声
        
        peak_indices = []
        valley_indices = []
        
        # 寻找局部高点和低点
        for i in range(window_size, len(data) - window_size):
            if (all(highs[i] >= highs[i-window_size:i]) and 
                all(highs[i] >= highs[i+1:i+window_size+1])):
                peak_indices.append(i)
            if (all(lows[i] <= lows[i-window_size:i]) and 
                all(lows[i] <= lows[i+1:i+window_size+1])):
                valley_indices.append(i)
        
        # 如果没有足够的极值点，返回空
        if len(peak_indices) < 3 or len(valley_indices) < 3:
            return patterns
        
        print(f"[DEBUG] 通道检测: 找到{len(peak_indices)}个高点, {len(valley_indices)}个低点")
        
        # 尝试构建上升通道
        up_channels = self._find_strict_channel(data, peak_indices, valley_indices, "up")
        # 尝试构建下降通道  
        down_channels = self._find_strict_channel(data, peak_indices, valley_indices, "down")
        # 尝试构建水平通道
        flat_channels = self._find_strict_channel(data, peak_indices, valley_indices, "flat")
        
        # 选择最好的通道
        all_channels = up_channels + down_channels + flat_channels
        if all_channels:
            # 按分数排序，选择最好的几个
            all_channels.sort(key=lambda x: x['score'], reverse=True)
            for channel in all_channels[:2]:  # 最多返回2个最好的通道
                patterns.append(channel['pattern'])
        
        return patterns
    def _create_strict_channel_lines(self, upper_points, lower_points, upper_slope, upper_intercept, lower_slope, lower_intercept, channel_type):
        """创建严格通道线的绘图数据 - 修复矩形整理版本"""
        # 使用实际的极值点坐标
        upper_x = [p[0] for p in upper_points]
        upper_y = [p[1] for p in upper_points]
        
        lower_x = [p[0] for p in lower_points]
        lower_y = [p[1] for p in lower_points]
        
        # 计算通道的起点和终点
        start_idx = min(upper_x[0], lower_x[0])
        end_idx = max(upper_x[-1], lower_x[-1])
        
        # 对于矩形整理，使用水平线而不是斜线
        if channel_type == "flat":
            # 计算上下轨的平均值
            upper_avg = np.mean(upper_y)
            lower_avg = np.mean(lower_y)
            
            extended_upper_x = [start_idx, end_idx]
            extended_upper_y = [upper_avg, upper_avg]  # 水平线
            
            extended_lower_x = [start_idx, end_idx]
            extended_lower_y = [lower_avg, lower_avg]  # 水平线
            
            print(f"[DEBUG] 矩形整理: 上轨水平线={upper_avg:.4f}, 下轨水平线={lower_avg:.4f}")
        else:
            # 创建扩展的通道线（用于绘制完整的线）
            extended_upper_x = [start_idx, end_idx]
            extended_upper_y = [upper_intercept + upper_slope * start_idx, 
                            upper_intercept + upper_slope * end_idx]
            
            extended_lower_x = [start_idx, end_idx]
            extended_lower_y = [lower_intercept + lower_slope * start_idx, 
                            lower_intercept + lower_slope * end_idx]
        
        draw_lines = {
            "upper_channel": {
                "x": extended_upper_x, 
                "y": extended_upper_y,
                "style": "solid"
            },
            "lower_channel": {
                "x": extended_lower_x, 
                "y": extended_lower_y,
                "style": "solid"
            },
            "upper_points": {
                "x": upper_x, 
                "y": upper_y,
                "style": "marker"
            },
            "lower_points": {
                "x": lower_x, 
                "y": lower_y,
                "style": "marker"
            }
        }
        
        print(f"[DEBUG] 创建{channel_type}通道线: 上轨{len(upper_points)}点, 下轨{len(lower_points)}点, 范围{start_idx}-{end_idx}")
        
        return draw_lines

    def _find_strict_channel(self, data, peak_indices, valley_indices, channel_type):
        """寻找严格定义的通道 - 修复矩形整理版本"""
        channels = []
        highs = data['high'].values
        lows = data['low'].values
        
        # 根据通道类型选择极值点
        if channel_type == "up":
            # 上升通道：需要至少3个连续上升的高点和低点
            upper_points = self._find_trend_points(peak_indices, highs, "up")
            lower_points = self._find_trend_points(valley_indices, lows, "up")
        elif channel_type == "down":
            # 下降通道：需要至少3个连续下降的高点和低点
            upper_points = self._find_trend_points(peak_indices, highs, "down")
            lower_points = self._find_trend_points(valley_indices, lows, "down")
        else:  # flat - 矩形整理
            # 水平通道：高点和低点都在水平范围内
            upper_points = self._find_horizontal_points(peak_indices, highs, tolerance=0.015)  # 更严格的容忍度
            lower_points = self._find_horizontal_points(valley_indices, lows, tolerance=0.015)
        
        # 必须有至少3个点才能形成通道
        if len(upper_points) < 3 or len(lower_points) < 3:
            print(f"[DEBUG] {channel_type}通道: 上轨{len(upper_points)}点, 下轨{len(lower_points)}点 - 点数不足")
            return channels
        
        print(f"[DEBUG] {channel_type}通道: 上轨{len(upper_points)}点, 下轨{len(lower_points)}点")
        
        # 对上轨点进行线性拟合
        upper_x = [p[0] for p in upper_points]
        upper_y = [p[1] for p in upper_points]
        upper_slope, upper_intercept = self._linear_regression(upper_x, upper_y)
        
        # 对下轨点进行线性拟合
        lower_x = [p[0] for p in lower_points]
        lower_y = [p[1] for p in lower_points]
        lower_slope, lower_intercept = self._linear_regression(lower_x, lower_y)
        
        print(f"[DEBUG] 矩形整理斜率: 上轨={upper_slope:.6f}, 下轨={lower_slope:.6f}")
        
        # 特别检查矩形整理的斜率
        if channel_type == "flat":
            # 矩形整理的斜率应该接近0
            slope_threshold = 0.0002  # 更严格的斜率阈值
            if abs(upper_slope) > slope_threshold or abs(lower_slope) > slope_threshold:
                print(f"[DEBUG] 矩形整理斜率超出阈值: 上轨{abs(upper_slope):.6f}, 下轨{abs(lower_slope):.6f} > {slope_threshold}")
                return channels
        
        # 检查通道质量
        start_idx = min(upper_x[0], lower_x[0])
        end_idx = max(upper_x[-1], lower_x[-1])
        
        # 通道必须覆盖足够的数据
        if end_idx - start_idx < len(data) * 0.4:  # 至少覆盖40%的数据
            print(f"[DEBUG] 通道覆盖不足: {end_idx-start_idx}根 < {len(data)*0.4}根")
            return channels
        
        # 评估通道质量
        score, in_channel_ratio = self._evaluate_strict_channel_quality(
            data, start_idx, end_idx, upper_slope, upper_intercept, lower_slope, lower_intercept, channel_type
        )
        
        # 严格的质量要求
        if score > 0.6 and in_channel_ratio > 0.75:
            # 确定通道类型和名称
            if channel_type == "up":
                name = "上升通道"
                pattern_type = "BULLISH"
            elif channel_type == "down":
                name = "下降通道" 
                pattern_type = "BEARISH"
            else:
                name = "矩形整理"
                pattern_type = "NEUTRAL"
            
            # 创建绘图数据
            draw_lines = self._create_strict_channel_lines(
                upper_points, lower_points, upper_slope, upper_intercept, lower_slope, lower_intercept, channel_type
            )
            
            pattern = {
                "name": name,
                "type": pattern_type,
                "confidence": min(0.95, score * 0.9),
                "description": f"{name}，质量评分{score:.2f}，{in_channel_ratio*100:.1f}%K线在通道内",
                "duration_bars": end_idx - start_idx + 1,
                "draw_lines": draw_lines
            }
            
            channels.append({
                "pattern": pattern,
                "score": score
            })
            print(f"[SUCCESS] 检测到{name}, 评分: {score:.2f}")
        else:
            print(f"[DEBUG] 通道质量不足: 评分{score:.2f}, 通道内比例{in_channel_ratio:.2f}")
        
        return channels

    def _find_trend_points(self, indices, values, trend_direction):
        """寻找符合趋势方向的连续点"""
        if len(indices) < 3:
            return []
        
        trend_points = []
        current_trend = []
        
        for i in range(len(indices)):
            idx = indices[i]
            value = values[idx]
            
            if not current_trend:
                current_trend.append((idx, value))
                continue
            
            # 检查是否符合趋势
            last_value = current_trend[-1][1]
            
            if trend_direction == "up":
                valid = value > last_value
            else:  # down
                valid = value < last_value
            
            if valid:
                current_trend.append((idx, value))
            else:
                # 当前趋势结束，检查是否足够长
                if len(current_trend) >= 3:
                    trend_points.extend(current_trend)
                current_trend = [(idx, value)]
        
        # 处理最后一个趋势
        if len(current_trend) >= 3:
            trend_points.extend(current_trend)
        
        # 去重并排序
        trend_points = list(dict.fromkeys(trend_points))
        trend_points.sort(key=lambda x: x[0])
        
        return trend_points

    def _find_horizontal_points(self, indices, values, tolerance=0.02):
        """寻找水平方向的点 - 修复版本"""
        if len(indices) < 3:
            return []
        
        # 计算价格的平均值和标准差
        price_values = [values[i] for i in indices]
        mean_price = np.mean(price_values)
        std_price = np.std(price_values)
        
        print(f"[DEBUG] 水平点检测: 均值={mean_price:.4f}, 标准差={std_price:.4f}, 容忍度={tolerance}")
        
        # 找到在容忍范围内的点
        horizontal_points = []
        for idx in indices:
            value = values[idx]
            deviation = abs(value - mean_price) / mean_price
            if deviation < tolerance:
                horizontal_points.append((idx, value))
                print(f"[DEBUG]  包含点 {idx}: {value:.4f} (偏差: {deviation:.4f})")
            else:
                print(f"[DEBUG]  排除点 {idx}: {value:.4f} (偏差: {deviation:.4f})")
        
        # 按索引排序
        horizontal_points.sort(key=lambda x: x[0])
        
        print(f"[DEBUG] 水平点结果: 找到{len(horizontal_points)}个点")
        return horizontal_points

    def _linear_regression(self, x, y):
        """线性回归拟合"""
        if len(x) < 2:
            return 0, y[0] if y else 0
        
        x_array = np.array(x)
        y_array = np.array(y)
        
        # 简单线性回归
        slope = np.cov(x_array, y_array)[0, 1] / np.var(x_array)
        intercept = np.mean(y_array) - slope * np.mean(x_array)
        
        return slope, intercept

    def _evaluate_strict_channel_quality(self, data, start_idx, end_idx, upper_slope, upper_intercept, lower_slope, lower_intercept, channel_type):
        """严格评估通道质量 - 修复矩形整理版本"""
        highs = data['high'].values
        lows = data['low'].values
        
        in_channel_count = 0
        total_bars = end_idx - start_idx + 1
        
        # 计算价格范围用于容差
        price_range = np.mean(highs[start_idx:end_idx+1] - lows[start_idx:end_idx+1])
        
        # 根据通道类型调整容差
        if channel_type == "flat":
            tolerance = price_range * 0.01  # 矩形整理使用更严格的容差
        else:
            tolerance = price_range * 0.015
        
        close_to_upper = 0
        close_to_lower = 0
        
        for i in range(start_idx, end_idx + 1):
            # 计算当前时刻的通道边界
            upper_bound = upper_intercept + upper_slope * i
            lower_bound = lower_intercept + lower_slope * i
            
            # 检查K线是否在通道内（带容差）
            high_in_channel = highs[i] <= upper_bound + tolerance
            low_in_channel = lows[i] >= lower_bound - tolerance
            
            if high_in_channel and low_in_channel:
                in_channel_count += 1
                
                # 检查是否接近边界
                if abs(highs[i] - upper_bound) < tolerance * 0.5:
                    close_to_upper += 1
                if abs(lows[i] - lower_bound) < tolerance * 0.5:
                    close_to_lower += 1
        
        in_channel_ratio = in_channel_count / total_bars
        
        # 检查是否有K线接触到边界
        boundary_contact_ratio = (close_to_upper + close_to_lower) / (2 * total_bars)
        
        # 计算综合评分
        coverage_ratio = total_bars / len(data)  # 通道覆盖的数据比例
        channel_width = np.mean([(upper_intercept + upper_slope * i) - (lower_intercept + lower_slope * i) 
                            for i in range(start_idx, end_idx+1)])
        width_score = min(1.0, max(0.5, channel_width / price_range / 2))
        
        # 边界接触也很重要
        boundary_score = min(1.0, boundary_contact_ratio * 3)
        
        # 对于矩形整理，额外检查水平度
        if channel_type == "flat":
            # 计算平均斜率
            avg_slope = (abs(upper_slope) + abs(lower_slope)) / 2
            # 水平度得分：斜率越小得分越高
            flatness_score = max(0, 1.0 - avg_slope * 5000)  # 调整系数
            print(f"[DEBUG] 矩形整理水平度: 平均斜率{avg_slope:.6f}, 水平度得分{flatness_score:.2f}")
            
            score = (in_channel_ratio * 0.4 + 
                    coverage_ratio * 0.15 + 
                    width_score * 0.2 +
                    boundary_score * 0.15 +
                    flatness_score * 0.1)
        else:
            score = (in_channel_ratio * 0.5 + 
                    coverage_ratio * 0.15 + 
                    width_score * 0.2 +
                    boundary_score * 0.15)
        
        print(f"[DEBUG] 通道质量评估: 类型{channel_type}, 评分{score:.2f}, 通道内{in_channel_ratio:.2f}, 覆盖{coverage_ratio:.2f}, 宽度{width_score:.2f}, 边界{boundary_score:.2f}")
        
        return score, in_channel_ratio

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
    
    def _detect_triangle_patterns(self, df: pd.DataFrame) -> List[Dict]:
        """严格检测三角形形态 - 重新设计"""
        patterns = []
        
        if len(df) < 20:  # 需要足够的数据点
            return patterns
        
        analysis_bars = min(60, len(df))
        data = df.tail(analysis_bars).copy()
        data_start_idx = len(df) - analysis_bars
        
        highs = data['high'].values
        lows = data['low'].values
        closes = data['close'].values
        
        print(f"[DEBUG] 严格三角形检测: 分析{analysis_bars}根K线")
        
        # 1. 寻找显著的高点和低点
        peaks, valleys = self._find_significant_extremes(highs, lows)
        
        if len(peaks) < 3 or len(valleys) < 3:
            print(f"[DEBUG] 三角形检测失败: 极值点不足(峰{len(peaks)},谷{len(valleys)})")
            return patterns
        
        print(f"[DEBUG] 找到{len(peaks)}个显著峰: {[(p, highs[p]) for p in peaks]}")
        print(f"[DEBUG] 找到{len(valleys)}个显著谷: {[(v, lows[v]) for v in valleys]}")
        
        # 2. 检测各种三角形形态
        patterns.extend(self._detect_strict_symmetric_triangle(data, peaks, valleys, data_start_idx))
        patterns.extend(self._detect_strict_ascending_triangle(data, peaks, valleys, data_start_idx))
        patterns.extend(self._detect_strict_descending_triangle(data, peaks, valleys, data_start_idx))
        
        return patterns

    def _find_significant_extremes(self, highs, lows, min_change_pct=0.02):
        """寻找显著的高点和低点 - 基于价格变化幅度"""
        peaks = []
        valleys = []
        
        # 寻找高点
        for i in range(1, len(highs)-1):
            if (highs[i] > highs[i-1] and highs[i] > highs[i+1] and
                highs[i] > np.mean(highs[max(0,i-5):i]) * (1 + min_change_pct)):
                peaks.append(i)
        
        # 寻找低点
        for i in range(1, len(lows)-1):
            if (lows[i] < lows[i-1] and lows[i] < lows[i+1] and
                lows[i] < np.mean(lows[max(0,i-5):i]) * (1 - min_change_pct)):
                valleys.append(i)
        
        return peaks, valleys

    def _detect_strict_symmetric_triangle(self, data, peaks, valleys, data_start_idx):
        """检测对称三角形（允许轻微突破）"""
        patterns = []
        
        if len(peaks) < 3 or len(valleys) < 3:
            return patterns
        
        # 按时间排序所有极值点
        all_extremes = []
        for p in peaks:
            all_extremes.append(('peak', p, data['high'].iloc[p]))
        for v in valleys:
            all_extremes.append(('valley', v, data['low'].iloc[v]))
        all_extremes.sort(key=lambda x: x[1])
        
        # 选择最近的3个高点和3个低点
        recent_peaks = sorted(peaks[-3:])
        recent_valleys = sorted(valleys[-3:])
        
        if len(recent_peaks) < 3 or len(recent_valleys) < 3:
            return patterns
        
        # 检查高点是否下降趋势
        high_x = np.array([0, 1, 2])
        high_y = np.array([data['high'].iloc[recent_peaks[0]], 
                        data['high'].iloc[recent_peaks[1]], 
                        data['high'].iloc[recent_peaks[2]]])
        
        # 检查低点是否上升趋势
        low_x = np.array([0, 1, 2])
        low_y = np.array([data['low'].iloc[recent_valleys[0]], 
                        data['low'].iloc[recent_valleys[1]], 
                        data['low'].iloc[recent_valleys[2]]])
        
        try:
            high_slope, high_intercept, high_r, _, _ = stats.linregress(high_x, high_y)
            low_slope, low_intercept, low_r, _, _ = stats.linregress(low_x, low_y)
        except:
            return patterns
        
        print(f"[DEBUG] 对称三角形: 高线斜率={high_slope:.6f}(R²={high_r**2:.3f}), 低线斜率={low_slope:.6f}(R²={low_r**2:.3f})")
        
        # 放宽条件：高点下降，低点上升
        if (high_slope < -0.0008 and low_slope > 0.0008 and  # 放宽斜率要求
            high_r**2 > 0.6 and low_r**2 > 0.6):  # 放宽R²要求
            
            # 检查K线是否基本在三角形区域内（允许轻微突破）
            start_idx = min(recent_peaks[0], recent_valleys[0])
            end_idx = max(recent_peaks[-1], recent_valleys[-1])
            
            triangle_data = data.iloc[start_idx:end_idx+1]
            
            # 计算价格范围用于设置容差
            max_high = np.max([data['high'].iloc[p] for p in recent_peaks])
            min_low = np.min([data['low'].iloc[v] for v in recent_valleys])
            price_range = max_high - min_low
            tolerance = price_range * 0.02  # 2%的价格范围作为容差
            
            valid_bars = 0
            total_bars = len(triangle_data)
            minor_breakout_bars = 0
            
            for i, (idx, row) in enumerate(triangle_data.iterrows()):
                bar_idx = idx - data_start_idx
                x_pos = (bar_idx - start_idx) / (end_idx - start_idx) * 2  # 标准化到0-2范围
                
                upper_bound = high_intercept + high_slope * x_pos
                lower_bound = low_intercept + low_slope * x_pos
                
                # 检查K线是否在三角形区域内（带容差）
                high_break = row['high'] > upper_bound + tolerance
                low_break = row['low'] < lower_bound - tolerance
                
                if not high_break and not low_break:
                    valid_bars += 1
                elif (row['high'] <= upper_bound + tolerance * 2 and 
                    row['low'] >= lower_bound - tolerance * 2):
                    # 轻微突破，在2倍容差范围内
                    minor_breakout_bars += 1
                    valid_bars += 0.5  # 轻微突破的K线给一半分数
            
            # 计算有效K线比例
            valid_ratio = valid_bars / total_bars
            
            print(f"[DEBUG] 对称三角形区域检查: 有效比例={valid_ratio:.2f}, 总K线数={total_bars}, 轻微突破={minor_breakout_bars}")
            
            # 放宽有效性要求：至少65%的K线在区域内
            if valid_ratio >= 0.65:
                # 计算绘图坐标
                start_plot_idx = data_start_idx + start_idx
                end_plot_idx = data_start_idx + end_idx
                
                upper_line_x = [start_plot_idx, end_plot_idx]
                upper_line_y = [high_intercept + high_slope * 0, 
                            high_intercept + high_slope * 2]
                
                lower_line_x = [start_plot_idx, end_plot_idx]
                lower_line_y = [low_intercept + low_slope * 0, 
                            low_intercept + low_slope * 2]
                
                # 根据有效性调整置信度
                confidence = 0.65 + min(0.25, (valid_ratio - 0.65) * 2.5)  # 0.65-0.9之间
                
                # 判断突破方向（基于斜率强度）
                slope_ratio = abs(high_slope) / (abs(high_slope) + abs(low_slope))
                if slope_ratio > 0.6:
                    breakout_direction = "DOWN"  # 下降趋势更强
                elif slope_ratio < 0.4:
                    breakout_direction = "UP"    # 上升趋势更强
                else:
                    breakout_direction = "UNKNOWN"  # 相对平衡
                
                draw_lines = {
                    "upper_trend": {"x": upper_line_x, "y": upper_line_y, "style": "solid", "color": "red", "linewidth": 2},
                    "lower_trend": {"x": lower_line_x, "y": lower_line_y, "style": "solid", "color": "green", "linewidth": 2},
                    "peak_points": {"x": [data_start_idx + p for p in recent_peaks], 
                                "y": [data['high'].iloc[p] for p in recent_peaks], 
                                "style": "marker", "color": "red", "marker": "o", "markersize": 8},
                    "valley_points": {"x": [data_start_idx + v for v in recent_valleys], 
                                    "y": [data['low'].iloc[v] for v in recent_valleys], 
                                    "style": "marker", "color": "green", "marker": "o", "markersize": 8}
                }
                
                patterns.append({
                    "name": "对称三角形",
                    "type": "CONTINUATION",
                    "confidence": confidence,
                    "description": f"对称三角形，{valid_ratio*100:.1f}%K线在形态区域内，预期突破方向：{breakout_direction}",
                    "duration_bars": end_idx - start_idx + 1,
                    "breakout_direction": breakout_direction,
                    "draw_lines": draw_lines
                })
                print(f"[DEBUG] ✅ 发现对称三角形! 置信度={confidence:.2f}, 预期突破方向={breakout_direction}")
        
        return patterns

    def _detect_strict_ascending_triangle(self, data, peaks, valleys, data_start_idx):
        """严格检测上升三角形（允许轻微突破）"""
        patterns = []
        
        if len(peaks) < 3 or len(valleys) < 3:
            return patterns
        
        # 选择最近的3个高点和3个低点
        recent_peaks = sorted(peaks[-3:])
        recent_valleys = sorted(valleys[-3:])
        
        # 检查高点是否水平（阻力位）
        high_values = [data['high'].iloc[p] for p in recent_peaks]
        high_mean = np.mean(high_values)
        high_std = np.std(high_values)
        high_cv = high_std / high_mean if high_mean != 0 else float('inf')
        
        # 检查低点是否上升
        low_x = np.array([0, 1, 2])
        low_y = np.array([data['low'].iloc[recent_valleys[0]], 
                        data['low'].iloc[recent_valleys[1]], 
                        data['low'].iloc[recent_valleys[2]]])
        
        try:
            low_slope, low_intercept, low_r, _, _ = stats.linregress(low_x, low_y)
        except:
            return patterns
        
        print(f"[DEBUG] 上升三角形: 高点变异系数={high_cv:.4f}, 低线斜率={low_slope:.6f}(R²={low_r**2:.3f})")
        
        # 放宽条件：高点基本水平，低点明显上升
        if (high_cv < 0.015 and  # 放宽到1.5%以内
            low_slope > 0.0015 and low_r**2 > 0.7):  # 放宽斜率要求和R²要求
            
            # 检查K线是否基本在三角形区域内（允许轻微突破）
            start_idx = min(recent_peaks[0], recent_valleys[0])
            end_idx = max(recent_peaks[-1], recent_valleys[-1])
            
            triangle_data = data.iloc[start_idx:end_idx+1]
            
            # 计算价格范围用于设置容差
            price_range = high_mean - np.min([data['low'].iloc[v] for v in recent_valleys])
            tolerance = price_range * 0.02  # 2%的价格范围作为容差
            
            valid_bars = 0
            total_bars = len(triangle_data)
            minor_breakout_bars = 0
            
            for i, (idx, row) in enumerate(triangle_data.iterrows()):
                bar_idx = idx - data_start_idx
                x_pos = (bar_idx - start_idx) / (end_idx - start_idx) * 2
                
                upper_bound = high_mean
                lower_bound = low_intercept + low_slope * x_pos
                
                # 检查K线是否在三角形区域内（带容差）
                high_break = row['high'] > upper_bound + tolerance
                low_break = row['low'] < lower_bound - tolerance
                
                if not high_break and not low_break:
                    valid_bars += 1
                elif (row['high'] <= upper_bound + tolerance * 2 and 
                    row['low'] >= lower_bound - tolerance * 2):
                    # 轻微突破，在2倍容差范围内
                    minor_breakout_bars += 1
                    valid_bars += 0.5  # 轻微突破的K线给一半分数
            
            # 计算有效K线比例
            valid_ratio = valid_bars / total_bars
            
            print(f"[DEBUG] 三角形区域检查: 有效比例={valid_ratio:.2f}, 总K线数={total_bars}, 轻微突破={minor_breakout_bars}")
            
            # 放宽有效性要求：至少70%的K线在区域内
            if valid_ratio >= 0.7:
                start_plot_idx = data_start_idx + start_idx
                end_plot_idx = data_start_idx + end_idx
                
                resistance_line_x = [start_plot_idx, end_plot_idx]
                resistance_line_y = [high_mean, high_mean]
                
                support_line_x = [start_plot_idx, end_plot_idx]
                support_line_y = [low_intercept + low_slope * 0, 
                                low_intercept + low_slope * 2]
                
                # 根据有效性调整置信度
                confidence = 0.7 + min(0.2, (valid_ratio - 0.7) * 2)  # 0.7-0.9之间
                
                draw_lines = {
                    "resistance_line": {"x": resistance_line_x, "y": resistance_line_y, 
                                    "style": "solid", "color": "red", "linewidth": 2},
                    "support_line": {"x": support_line_x, "y": support_line_y, 
                                "style": "solid", "color": "green", "linewidth": 2},
                    "peak_points": {"x": [data_start_idx + p for p in recent_peaks], 
                                "y": [data['high'].iloc[p] for p in recent_peaks], 
                                "style": "marker", "color": "red", "marker": "o", "markersize": 8},
                    "valley_points": {"x": [data_start_idx + v for v in recent_valleys], 
                                    "y": [data['low'].iloc[v] for v in recent_valleys], 
                                    "style": "marker", "color": "green", "marker": "o", "markersize": 8}
                }
                
                patterns.append({
                    "name": "上升三角形",
                    "type": "BULLISH",
                    "confidence": confidence,
                    "description": f"上升三角形，{valid_ratio*100:.1f}%K线在形态区域内",
                    "resistance_level": high_mean,
                    "breakout_direction": "UP",
                    "target_price": high_mean + (high_mean - support_line_y[0]),
                    "duration_bars": end_idx - start_idx + 1,
                    "draw_lines": draw_lines
                })
                print(f"[DEBUG] ✅ 发现上升三角形! 置信度={confidence:.2f}")
        
        return patterns
    def _detect_strict_descending_triangle(self, data, peaks, valleys, data_start_idx):
        """检测下降三角形（允许轻微突破）"""
        patterns = []
        
        if len(peaks) < 3 or len(valleys) < 3:
            return patterns
        
        # 选择最近的3个高点和3个低点
        recent_peaks = sorted(peaks[-3:])
        recent_valleys = sorted(valleys[-3:])
        
        # 检查低点是否水平（支撑位）
        low_values = [data['low'].iloc[v] for v in recent_valleys]
        low_mean = np.mean(low_values)
        low_std = np.std(low_values)
        low_cv = low_std / low_mean if low_mean != 0 else float('inf')
        
        # 检查高点是否下降
        high_x = np.array([0, 1, 2])
        high_y = np.array([data['high'].iloc[recent_peaks[0]], 
                        data['high'].iloc[recent_peaks[1]], 
                        data['high'].iloc[recent_peaks[2]]])
        
        try:
            high_slope, high_intercept, high_r, _, _ = stats.linregress(high_x, high_y)
        except:
            return patterns
        
        print(f"[DEBUG] 下降三角形: 低点变异系数={low_cv:.4f}, 高线斜率={high_slope:.6f}(R²={high_r**2:.3f})")
        
        # 放宽条件：低点基本水平，高点明显下降
        if (low_cv < 0.015 and  # 放宽到1.5%以内
            high_slope < -0.0015 and high_r**2 > 0.7):  # 放宽斜率要求和R²要求
            
            # 检查K线是否基本在三角形区域内（允许轻微突破）
            start_idx = min(recent_peaks[0], recent_valleys[0])
            end_idx = max(recent_peaks[-1], recent_valleys[-1])
            
            triangle_data = data.iloc[start_idx:end_idx+1]
            
            # 计算价格范围用于设置容差
            price_range = np.max([data['high'].iloc[p] for p in recent_peaks]) - low_mean
            tolerance = price_range * 0.02  # 2%的价格范围作为容差
            
            valid_bars = 0
            total_bars = len(triangle_data)
            minor_breakout_bars = 0
            
            for i, (idx, row) in enumerate(triangle_data.iterrows()):
                bar_idx = idx - data_start_idx
                x_pos = (bar_idx - start_idx) / (end_idx - start_idx) * 2
                
                upper_bound = high_intercept + high_slope * x_pos
                lower_bound = low_mean
                
                # 检查K线是否在三角形区域内（带容差）
                high_break = row['high'] > upper_bound + tolerance
                low_break = row['low'] < lower_bound - tolerance
                
                if not high_break and not low_break:
                    valid_bars += 1
                elif (row['high'] <= upper_bound + tolerance * 2 and 
                    row['low'] >= lower_bound - tolerance * 2):
                    # 轻微突破，在2倍容差范围内
                    minor_breakout_bars += 1
                    valid_bars += 0.5  # 轻微突破的K线给一半分数
            
            # 计算有效K线比例
            valid_ratio = valid_bars / total_bars
            
            print(f"[DEBUG] 下降三角形区域检查: 有效比例={valid_ratio:.2f}, 总K线数={total_bars}, 轻微突破={minor_breakout_bars}")
            
            # 放宽有效性要求：至少70%的K线在区域内
            if valid_ratio >= 0.7:
                start_plot_idx = data_start_idx + start_idx
                end_plot_idx = data_start_idx + end_idx
                
                support_line_x = [start_plot_idx, end_plot_idx]
                support_line_y = [low_mean, low_mean]
                
                resistance_line_x = [start_plot_idx, end_plot_idx]
                resistance_line_y = [high_intercept + high_slope * 0, 
                                high_intercept + high_slope * 2]
                
                # 根据有效性调整置信度
                confidence = 0.7 + min(0.2, (valid_ratio - 0.7) * 2)  # 0.7-0.9之间
                
                draw_lines = {
                    "support_line": {"x": support_line_x, "y": support_line_y, 
                                "style": "solid", "color": "green", "linewidth": 2},
                    "resistance_line": {"x": resistance_line_x, "y": resistance_line_y, 
                                    "style": "solid", "color": "red", "linewidth": 2},
                    "peak_points": {"x": [data_start_idx + p for p in recent_peaks], 
                                "y": [data['high'].iloc[p] for p in recent_peaks], 
                                "style": "marker", "color": "red", "marker": "o", "markersize": 8},
                    "valley_points": {"x": [data_start_idx + v for v in recent_valleys], 
                                    "y": [data['low'].iloc[v] for v in recent_valleys], 
                                    "style": "marker", "color": "green", "marker": "o", "markersize": 8}
                }
                
                patterns.append({
                    "name": "下降三角形",
                    "type": "BEARISH",
                    "confidence": confidence,
                    "description": f"下降三角形，{valid_ratio*100:.1f}%K线在形态区域内",
                    "support_level": low_mean,
                    "breakout_direction": "DOWN",
                    "target_price": low_mean - (resistance_line_y[0] - low_mean),
                    "duration_bars": end_idx - start_idx + 1,
                    "draw_lines": draw_lines
                })
                print(f"[DEBUG] ✅ 发现下降三角形! 置信度={confidence:.2f}")
        
        return patterns



  



    def _find_convergence_point(self, slope1, intercept1, slope2, intercept2, x_range):
        """计算两条趋势线的收敛点"""
        if slope1 == slope2:  # 平行线，无交点
            return None
        
        # 计算交点
        x_intersect = (intercept2 - intercept1) / (slope1 - slope2)
        y_intersect = intercept1 + slope1 * x_intersect
        
        # 检查交点是否在合理范围内
        if 0 <= x_intersect <= x_range * 1.5:  # 允许一定的延伸
            return x_intersect
        return None

    def detect_chart_patterns(self, df: pd.DataFrame) -> Dict[str, List[Dict]]:
        """检测所有图表形态 - 主函数"""
        if df is None or len(df) < 15:
            return {"CONTINUATION": [], "REVERSAL": [], "BREAKOUT": []}
        
        # 分别检测各类形态
        triangle_patterns = self._detect_triangle_patterns(df)
        double_patterns = self._detect_double_patterns(df)
        channel_patterns = self._detect_channel_patterns(df)
        breakout_patterns = self._detect_support_resistance(df)
        
        # 分类整理
        continuation_patterns = triangle_patterns + channel_patterns
        reversal_patterns = double_patterns
        
        # 进一步降低置信度过滤
        continuation_patterns = [p for p in continuation_patterns if p.get('confidence', 0) > 0.5]
        reversal_patterns = [p for p in reversal_patterns if p.get('confidence', 0) > 0.5]
        breakout_patterns = [p for p in breakout_patterns if p.get('confidence', 0) > 0.5]
        
        return {
            "CONTINUATION": continuation_patterns,
            "REVERSAL": reversal_patterns,
            "BREAKOUT": breakout_patterns
        }