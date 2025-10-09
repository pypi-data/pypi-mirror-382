import pandas as pd
import numpy as np
from typing import List, Dict, Optional
from datetime import datetime

class CandlestickPatterns:
    def __init__(self):
        # K线形态分类
        self.patterns = {
            "SINGLE": [
                "光头光脚阳线", "光脚阳线", "光头阳线", "带上下影线的阳线",
                "光头光脚阴线", "光脚阴线", "光头阴线", "带上下影线的阴线",
                "十字线", "T字线", "倒T字线", "一字线", "锤头线", "上吊线", 
                "倒锤头线", "射击之星"
            ],
            "DOUBLE": [
                "乌云盖顶组合", "旭日东升组合", "抱线组合", "孕线组合", 
                "插入线组合", "跳空组合", "双飞乌鸦组合"
            ],
            "MULTI": [
                "黄昏之星", "红三兵", "多方炮", "上升三法", "早晨之星", 
                "黑三鸦", "空方炮", "下降三法"
            ]
        }

    def _calculate_trend(self, df: pd.DataFrame, period: int) -> str:
        """计算趋势方向"""
        if len(df) < period:
            return "neutral"
        
        closes = df['close'].tail(period)
        if len(closes) < 2:
            return "neutral"
        
        price_change = (closes.iloc[-1] - closes.iloc[0]) / closes.iloc[0] * 100
        
        if price_change > 3:
            return "up"
        elif price_change < -3:
            return "down"
        else:
            return "neutral"

    def _analyze_candle_features(self, candle):
        """分析单根K线特征"""
        body = abs(candle['close'] - candle['open'])
        upper_shadow = candle['high'] - max(candle['open'], candle['close'])
        lower_shadow = min(candle['open'], candle['close']) - candle['low']
        total_range = candle['high'] - candle['low']
        
        if total_range == 0:
            return {}
            
        body_ratio = body / total_range
        upper_ratio = upper_shadow / total_range
        lower_ratio = lower_shadow / total_range
        
        is_bullish = candle['close'] > candle['open']
        is_bearish = candle['close'] < candle['open']
        
        return {
            'body': body,
            'upper_shadow': upper_shadow,
            'lower_shadow': lower_shadow,
            'total_range': total_range,
            'body_ratio': body_ratio,
            'upper_ratio': upper_ratio,
            'lower_ratio': lower_ratio,
            'is_bullish': is_bullish,
            'is_bearish': is_bearish
        }

    def detect_single_candle_patterns(self, current_candle, trend) -> List[Dict]:
        """检测单K线形态"""
        patterns = []
        candle_data = self._analyze_candle_features(current_candle)
        
        if not candle_data:
            return patterns
            
        body_ratio = candle_data['body_ratio']
        upper_ratio = candle_data['upper_ratio']
        lower_ratio = candle_data['lower_ratio']
        is_bullish = candle_data['is_bullish']
        is_bearish = candle_data['is_bearish']
        
        # 1. 光头光脚阳线
        if (is_bullish and upper_ratio < 0.05 and lower_ratio < 0.05 and body_ratio > 0.8):
            patterns.append({
                "name": "光头光脚阳线",
                "type": "BULLISH",
                "category": "SINGLE",
                "confidence": 0.9,
                "description": "没有上下影线，开盘价即最低价，收盘价即最高价，表示强烈的看涨信号",
                "candle_count": 1,
                "candle_indices": [-1]
            })
        
        # 2. 光脚阳线
        elif (is_bullish and lower_ratio < 0.05 and upper_ratio > 0.1 and body_ratio > 0.5):
            patterns.append({
                "name": "光脚阳线",
                "type": "BULLISH",
                "category": "SINGLE",
                "confidence": 0.7,
                "description": "没有下影线，表示买方力量强劲，但上方有压力",
                "candle_count": 1,
                "candle_indices": [-1]
            })
        
        # 3. 光头阳线
        elif (is_bullish and upper_ratio < 0.05 and lower_ratio > 0.1 and body_ratio > 0.5):
            patterns.append({
                "name": "光头阳线",
                "type": "BULLISH",
                "category": "SINGLE",
                "confidence": 0.7,
                "description": "没有上影线，收盘价即最高价，表示买方完全控制局面",
                "candle_count": 1,
                "candle_indices": [-1]
            })
        
        # 4. 带上下影线的阳线
        elif (is_bullish and upper_ratio > 0.1 and lower_ratio > 0.1 and body_ratio > 0.3):
            patterns.append({
                "name": "带上下影线的阳线",
                "type": "BULLISH",
                "category": "SINGLE",
                "confidence": 0.5,
                "description": "有上下影线，表示多空双方有争夺，但最终买方获胜",
                "candle_count": 1,
                "candle_indices": [-1]
            })
        
        # 5. 光头光脚阴线
        elif (is_bearish and upper_ratio < 0.05 and lower_ratio < 0.05 and body_ratio > 0.8):
            patterns.append({
                "name": "光头光脚阴线",
                "type": "BEARISH",
                "category": "SINGLE",
                "confidence": 0.9,
                "description": "没有上下影线，开盘价即最高价，收盘价即最低价，表示强烈的看跌信号",
                "candle_count": 1,
                "candle_indices": [-1]
            })
        
        # 6. 光脚阴线
        elif (is_bearish and lower_ratio < 0.05 and upper_ratio > 0.1 and body_ratio > 0.5):
            patterns.append({
                "name": "光脚阴线",
                "type": "BEARISH",
                "category": "SINGLE",
                "confidence": 0.7,
                "description": "没有下影线，表示卖方力量强劲，开盘后价格一路下跌",
                "candle_count": 1,
                "candle_indices": [-1]
            })
        
        # 7. 光头阴线
        elif (is_bearish and upper_ratio < 0.05 and lower_ratio > 0.1 and body_ratio > 0.5):
            patterns.append({
                "name": "光头阴线",
                "type": "BEARISH",
                "category": "SINGLE",
                "confidence": 0.7,
                "description": "没有上影线，开盘价即最高价，表示卖方完全控制局面",
                "candle_count": 1,
                "candle_indices": [-1]
            })
        
        # 8. 带上下影线的阴线
        elif (is_bearish and upper_ratio > 0.1 and lower_ratio > 0.1 and body_ratio > 0.3):
            patterns.append({
                "name": "带上下影线的阴线",
                "type": "BEARISH",
                "category": "SINGLE",
                "confidence": 0.5,
                "description": "有上下影线，表示多空双方有争夺，但最终卖方获胜",
                "candle_count": 1,
                "candle_indices": [-1]
            })
        
        # 9. 十字线
        elif (body_ratio < 0.1 and upper_ratio > 0.3 and lower_ratio > 0.3):
            patterns.append({
                "name": "十字线",
                "type": "NEUTRAL",
                "category": "SINGLE",
                "confidence": 0.8,
                "description": "开盘收盘价接近，表示市场犹豫不决，可能预示反转",
                "candle_count": 1,
                "candle_indices": [-1]
            })
        
        # 10. T字线
        elif (is_bullish and upper_ratio < 0.1 and lower_ratio > 0.6 and body_ratio < 0.3):
            patterns.append({
                "name": "T字线",
                "type": "BULLISH",
                "category": "SINGLE",
                "confidence": 0.7,
                "description": "卖方打压后买方收复失地，出现在底部时看涨信号更强",
                "candle_count": 1,
                "candle_indices": [-1]
            })
        
        # 11. 倒T字线
        elif (is_bearish and upper_ratio > 0.6 and lower_ratio < 0.1 and body_ratio < 0.3):
            patterns.append({
                "name": "倒T字线",
                "type": "BEARISH",
                "category": "SINGLE",
                "confidence": 0.7,
                "description": "买方推高后卖方打压回落，出现在顶部时看跌信号更强",
                "candle_count": 1,
                "candle_indices": [-1]
            })
        
        # 12. 一字线 (涨停或跌停)
        elif (body_ratio > 0.95 and upper_ratio < 0.05 and lower_ratio < 0.05):
            if is_bullish:
                patterns.append({
                    "name": "一字线(涨停)",
                    "type": "BULLISH",
                    "category": "SINGLE",
                    "confidence": 0.9,
                    "description": "开盘即涨停，表示极强的买盘力量",
                    "candle_count": 1,
                    "candle_indices": [-1]
                })
            else:
                patterns.append({
                    "name": "一字线(跌停)",
                    "type": "BEARISH",
                    "category": "SINGLE",
                    "confidence": 0.9,
                    "description": "开机即跌停，表示极强的卖盘力量",
                    "candle_count": 1,
                    "candle_indices": [-1]
                })
        
        # 13. 锤头线 (出现在下跌趋势中)
        elif (trend == "down" and is_bullish and lower_ratio > 0.6 and upper_ratio < 0.2 and 0.1 < body_ratio < 0.4):
            patterns.append({
                "name": "锤头线",
                "type": "BULLISH",
                "category": "SINGLE",
                "confidence": 0.8,
                "description": "出现在下跌趋势中，长下影线表示买方力量开始增强",
                "candle_count": 1,
                "candle_indices": [-1]
            })
        
        # 14. 上吊线 (出现在上涨趋势中)
        elif (trend == "up" and is_bearish and lower_ratio > 0.6 and upper_ratio < 0.2 and 0.1 < body_ratio < 0.4):
            patterns.append({
                "name": "上吊线",
                "type": "BEARISH",
                "category": "SINGLE",
                "confidence": 0.8,
                "description": "出现在上涨趋势中，长下影线表示卖方力量开始增强",
                "candle_count": 1,
                "candle_indices": [-1]
            })
        
        # 15. 倒锤头线 (出现在下跌趋势中)
        elif (trend == "down" and is_bullish and upper_ratio > 0.6 and lower_ratio < 0.2 and 0.1 < body_ratio < 0.4):
            patterns.append({
                "name": "倒锤头线",
                "type": "BULLISH",
                "category": "SINGLE",
                "confidence": 0.7,
                "description": "出现在下跌趋势中，长上影线表示买方尝试反攻",
                "candle_count": 1,
                "candle_indices": [-1]
            })
        
        # 16. 射击之星 (出现在上涨趋势中)
        elif (trend == "up" and is_bearish and upper_ratio > 0.6 and lower_ratio < 0.2 and 0.1 < body_ratio < 0.4):
            patterns.append({
                "name": "射击之星",
                "type": "BEARISH",
                "category": "SINGLE",
                "confidence": 0.8,
                "description": "出现在上涨趋势中，长上影线表示上方压力巨大",
                "candle_count": 1,
                "candle_indices": [-1]
            })
        
        return patterns

    def detect_double_candle_patterns(self, current_candle, prev_candle, trend) -> List[Dict]:
        """检测双K线组合形态"""
        patterns = []
        
        current_data = self._analyze_candle_features(current_candle)
        prev_data = self._analyze_candle_features(prev_candle)
        
        if not current_data or not prev_data:
            return patterns
        
        # 1. 乌云盖顶组合
        if (trend == "up" and 
            prev_data['is_bullish'] and current_data['is_bearish'] and
            current_candle['open'] > prev_candle['high'] and
            current_candle['close'] < (prev_candle['open'] + prev_candle['close']) / 2 and
            current_candle['close'] > prev_candle['open']):
            patterns.append({
                "name": "乌云盖顶组合",
                "type": "BEARISH",
                "category": "DOUBLE",
                "confidence": 0.8,
                "description": "第二根阴线开盘高于前一根高点，收盘低于前一根中点，预示上涨趋势可能结束",
                "candle_count": 2,
                "candle_indices": [-2, -1]
            })
        
        # 2. 旭日东升组合
        if (trend == "down" and 
            prev_data['is_bearish'] and current_data['is_bullish'] and
            current_candle['open'] < prev_candle['low'] and
            current_candle['close'] > (prev_candle['open'] + prev_candle['close']) / 2 and
            current_candle['close'] < prev_candle['open']):
            patterns.append({
                "name": "旭日东升组合",
                "type": "BULLISH",
                "category": "DOUBLE",
                "confidence": 0.8,
                "description": "第二根阳线开盘低于前一根低点，收盘高于前一根中点，预示下跌趋势可能结束",
                "candle_count": 2,
                "candle_indices": [-2, -1]
            })
        
        # 3. 抱线组合 (吞没形态)
        if (trend == "down" and 
            current_data['is_bullish'] and prev_data['is_bearish'] and
            current_candle['close'] > prev_candle['open'] and 
            current_candle['open'] < prev_candle['close'] and
            current_data['body'] > prev_data['body'] * 1.2):
            patterns.append({
                "name": "抱线组合(看涨吞没)",
                "type": "BULLISH",
                "category": "DOUBLE",
                "confidence": 0.8,
                "description": "阳线完全吞没前一根阴线，强烈看涨反转信号",
                "candle_count": 2,
                "candle_indices": [-2, -1]
            })
        
        if (trend == "up" and 
            current_data['is_bearish'] and prev_data['is_bullish'] and
            current_candle['close'] < prev_candle['open'] and 
            current_candle['open'] > prev_candle['close'] and
            current_data['body'] > prev_data['body'] * 1.2):
            patterns.append({
                "name": "抱线组合(看跌吞没)",
                "type": "BEARISH",
                "category": "DOUBLE",
                "confidence": 0.8,
                "description": "阴线完全吞没前一根阳线，强烈看跌反转信号",
                "candle_count": 2,
                "candle_indices": [-2, -1]
            })
        
        # 4. 孕线组合
        if (abs(current_data['body']) < 0.5 * abs(prev_data['body']) and
            current_candle['high'] < prev_candle['high'] and 
            current_candle['low'] > prev_candle['low']):
            
            if trend == "down" and current_data['is_bullish'] and prev_data['is_bearish']:
                patterns.append({
                    "name": "孕线组合(看涨)",
                    "type": "BULLISH",
                    "category": "DOUBLE",
                    "confidence": 0.6,
                    "description": "小实体在大实体内，出现在下跌趋势中可能反转",
                    "candle_count": 2,
                    "candle_indices": [-2, -1]
                })
            elif trend == "up" and current_data['is_bearish'] and prev_data['is_bullish']:
                patterns.append({
                    "name": "孕线组合(看跌)",
                    "type": "BEARISH",
                    "category": "DOUBLE",
                    "confidence": 0.6,
                    "description": "小实体在大实体内，出现在上涨趋势中可能反转",
                    "candle_count": 2,
                    "candle_indices": [-2, -1]
                })
        
        # 5. 插入线组合
        if (trend == "down" and 
            prev_data['is_bearish'] and current_data['is_bullish'] and
            current_candle['open'] < prev_candle['low'] and
            current_candle['close'] > prev_candle['close'] and
            current_candle['close'] < (prev_candle['open'] + prev_candle['close']) / 2):
            patterns.append({
                "name": "插入线组合",
                "type": "BULLISH",
                "category": "DOUBLE",
                "confidence": 0.7,
                "description": "阳线插入到前一根阴线实体内部，显示买方力量增强",
                "candle_count": 2,
                "candle_indices": [-2, -1]
            })
        
        # 6. 跳空组合
        gap_up = current_candle['low'] > prev_candle['high']
        gap_down = current_candle['high'] < prev_candle['low']
        
        if gap_up and current_data['is_bullish']:
            patterns.append({
                "name": "向上跳空组合",
                "type": "BULLISH",
                "category": "DOUBLE",
                "confidence": 0.7,
                "description": "第二根K线向上跳空，显示强劲的买方力量",
                "candle_count": 2,
                "candle_indices": [-2, -1]
            })
        elif gap_down and current_data['is_bearish']:
            patterns.append({
                "name": "向下跳空组合",
                "type": "BEARISH",
                "category": "DOUBLE",
                "confidence": 0.7,
                "description": "第二根K线向下跳空，显示强劲的卖方力量",
                "candle_count": 2,
                "candle_indices": [-2, -1]
            })
        
        # 7. 双飞乌鸦组合
        if (trend == "up" and 
            prev_data['is_bearish'] and current_data['is_bearish'] and
            current_candle['open'] > prev_candle['open'] and
            current_candle['close'] < prev_candle['close']):
            patterns.append({
                "name": "双飞乌鸦组合",
                "type": "BEARISH",
                "category": "DOUBLE",
                "confidence": 0.7,
                "description": "连续两根阴线，第二根开盘高于第一根但收盘更低，预示上涨乏力",
                "candle_count": 2,
                "candle_indices": [-2, -1]
            })
        
        return patterns

    def detect_multi_candle_patterns(self, df, trend) -> List[Dict]:
        """检测多K线组合形态"""
        patterns = []
        
        if len(df) < 3:
            return patterns
        
        # 获取最近几根K线
        current = df.iloc[-1]
        prev = df.iloc[-2]
        prev2 = df.iloc[-3]
        prev3 = df.iloc[-4] if len(df) >= 4 else None
        
        current_data = self._analyze_candle_features(current)
        prev_data = self._analyze_candle_features(prev)
        prev2_data = self._analyze_candle_features(prev2)
        
        if not all([current_data, prev_data, prev2_data]):
            return patterns
        
        # 1. 黄昏之星
        if (trend == "up" and 
            prev2_data['is_bullish'] and  # 第一根阳线
            prev_data['body_ratio'] < 0.3 and  # 第二根小实体
            current_data['is_bearish'] and  # 第三根阴线
            current['close'] < (prev2['open'] + prev2['close']) / 2):  # 收盘低于第一根中点
            patterns.append({
                "name": "黄昏之星",
                "type": "BEARISH",
                "category": "MULTI",
                "confidence": 0.8,
                "description": "三根K线组合，出现在上涨趋势顶部，强烈看跌反转信号",
                "candle_count": 3,
                "candle_indices": [-3, -2, -1]
            })
        
        # 2. 红三兵
        if (trend == "down" and 
            current_data['is_bullish'] and prev_data['is_bullish'] and prev2_data['is_bullish'] and
            current['open'] > prev['open'] and prev['open'] > prev2['open'] and
            current['close'] > prev['close'] and prev['close'] > prev2['close'] and
            all(data['body_ratio'] > 0.5 for data in [current_data, prev_data, prev2_data])):
            patterns.append({
                "name": "红三兵",
                "type": "BULLISH",
                "category": "MULTI",
                "confidence": 0.8,
                "description": "连续三根实体逐渐增长的阳线，显示强劲的买方力量",
                "candle_count": 3,
                "candle_indices": [-3, -2, -1]
            })
        
        # 3. 多方炮
        if (prev3 is not None and 
            self._analyze_candle_features(prev3)['is_bullish'] and  # 第一根阳线
            prev2_data['is_bearish'] and  # 第二根阴线
            prev_data['is_bullish'] and  # 第三根阳线
            current_data['is_bullish'] and  # 第四根阳线
            prev['close'] > prev2['open'] and  # 第三根收盘高于第二根开盘
            current['close'] > prev['close']):  # 第四根收盘高于第三根
            patterns.append({
                "name": "多方炮",
                "type": "BULLISH",
                "category": "MULTI",
                "confidence": 0.7,
                "description": "两阳夹一阴形态，显示洗盘后继续上涨的强势信号",
                "candle_count": 4,
                "candle_indices": [-4, -3, -2, -1]
            })
        
        # 4. 上升三法
        if (trend == "up" and 
            prev2_data['is_bullish'] and  # 第一根大阳线
            prev2_data['body_ratio'] > 0.6 and
            prev_data['is_bearish'] and  # 第二根小阴线
            prev_data['body_ratio'] < 0.4 and
            current_data['is_bullish'] and  # 第三根阳线
            current['close'] > prev2['close'] and  # 收盘创出新高
            prev['high'] < prev2['high'] and prev['low'] > prev2['low']):  # 小阴线在第一根范围内
            patterns.append({
                "name": "上升三法",
                "type": "BULLISH",
                "category": "MULTI",
                "confidence": 0.7,
                "description": "大阳线后跟随小阴线，再出现创新高的大阳线，上升中继形态",
                "candle_count": 3,
                "candle_indices": [-3, -2, -1]
            })
        
        # 5. 早晨之星
        if (trend == "down" and 
            prev2_data['is_bearish'] and  # 第一根阴线
            prev_data['body_ratio'] < 0.3 and  # 第二根小实体
            current_data['is_bullish'] and  # 第三根阳线
            current['close'] > (prev2['open'] + prev2['close']) / 2):  # 收盘超过第一根中点
            patterns.append({
                "name": "早晨之星",
                "type": "BULLISH",
                "category": "MULTI",
                "confidence": 0.8,
                "description": "三根K线组合，出现在下跌趋势底部，强烈看涨反转信号",
                "candle_count": 3,
                "candle_indices": [-3, -2, -1]
            })
        
        # 6. 黑三鸦 (三只乌鸦)
        if (trend == "up" and 
            current_data['is_bearish'] and prev_data['is_bearish'] and prev2_data['is_bearish'] and
            current['open'] < prev['open'] and prev['open'] < prev2['open'] and
            current['close'] < prev['close'] and prev['close'] < prev2['close'] and
            all(data['body_ratio'] > 0.4 for data in [current_data, prev_data, prev2_data])):
            patterns.append({
                "name": "黑三鸦",
                "type": "BEARISH",
                "category": "MULTI",
                "confidence": 0.8,
                "description": "连续三根实体逐渐增长的阴线，显示强劲的卖方力量",
                "candle_count": 3,
                "candle_indices": [-3, -2, -1]
            })
        
        # 7. 空方炮
        if (prev3 is not None and 
            self._analyze_candle_features(prev3)['is_bearish'] and  # 第一根阴线
            prev2_data['is_bullish'] and  # 第二根阳线
            prev_data['is_bearish'] and  # 第三根阴线
            current_data['is_bearish'] and  # 第四根阴线
            prev['close'] < prev2['open'] and  # 第三根收盘低于第二根开盘
            current['close'] < prev['close']):  # 第四根收盘低于第三根
            patterns.append({
                "name": "空方炮",
                "type": "BEARISH",
                "category": "MULTI",
                "confidence": 0.7,
                "description": "两阴夹一阳形态，显示反弹后继续下跌的弱势信号",
                "candle_count": 4,
                "candle_indices": [-4, -3, -2, -1]
            })
        
        # 8. 下降三法
        if (trend == "down" and 
            prev2_data['is_bearish'] and  # 第一根大阴线
            prev2_data['body_ratio'] > 0.6 and
            prev_data['is_bullish'] and  # 第二根小阳线
            prev_data['body_ratio'] < 0.4 and
            current_data['is_bearish'] and  # 第三根阴线
            current['close'] < prev2['close'] and  # 收盘创出新低
            prev['high'] < prev2['high'] and prev['low'] > prev2['low']):  # 小阳线在第一根范围内
            patterns.append({
                "name": "下降三法",
                "type": "BEARISH",
                "category": "MULTI",
                "confidence": 0.7,
                "description": "大阴线后跟随小阳线，再出现创新低的大阴线，下降中继形态",
                "candle_count": 3,
                "candle_indices": [-3, -2, -1]
            })
        
        return patterns

    def detect_candlestick_patterns(self, df: pd.DataFrame) -> Dict[str, List[Dict]]:
        """检测所有K线形态 - 在整个数据集上检测"""
        if df is None or len(df) < 3:
            return {"SINGLE": [], "DOUBLE": [], "MULTI": []}
        
        single_patterns = []
        double_patterns = []
        multi_patterns = []
        
        # 在整个数据集上滑动检测
        for i in range(2, len(df)):
            # 计算当前窗口的趋势
            window_start = max(0, i-10)
            window_df = df.iloc[window_start:i+1]
            short_trend = self._calculate_trend(window_df, period=min(10, len(window_df)))
            
            current = df.iloc[i]
            prev = df.iloc[i-1] if i >= 1 else None
            prev2 = df.iloc[i-2] if i >= 2 else None
            
            # 检测单K线形态
            single_ps = self.detect_single_candle_patterns(current, short_trend)
            for pattern in single_ps:
                pattern['candle_indices'] = [i]  # 使用绝对索引
                pattern['position'] = i
                single_patterns.append(pattern)
            
            # 检测双K线形态
            if prev is not None:
                double_ps = self.detect_double_candle_patterns(current, prev, short_trend)
                for pattern in double_ps:
                    pattern['candle_indices'] = [i-1, i]  # 使用绝对索引
                    pattern['position'] = i
                    double_patterns.append(pattern)
            
            # 检测多K线形态 (需要至少3根K线)
            if i >= 2:
                # 创建当前窗口的数据子集
                window_data = df.iloc[max(0, i-3):i+1]
                multi_ps = self.detect_multi_candle_patterns(window_data, short_trend)
                for pattern in multi_ps:
                    # 根据蜡烛数量设置索引
                    candle_count = pattern.get('candle_count', 3)
                    pattern['candle_indices'] = list(range(i-candle_count+1, i+1))
                    pattern['position'] = i
                    multi_patterns.append(pattern)
        
        # 按位置排序，最新的在前面
        single_patterns.sort(key=lambda x: x['position'], reverse=True)
        double_patterns.sort(key=lambda x: x['position'], reverse=True)
        multi_patterns.sort(key=lambda x: x['position'], reverse=True)
        
        # 限制每个类别的数量，避免过多
        max_patterns_per_category = 15
        
        return {
            "SINGLE": single_patterns[:max_patterns_per_category],
            "DOUBLE": double_patterns[:max_patterns_per_category],
            "MULTI": multi_patterns[:max_patterns_per_category]
        }