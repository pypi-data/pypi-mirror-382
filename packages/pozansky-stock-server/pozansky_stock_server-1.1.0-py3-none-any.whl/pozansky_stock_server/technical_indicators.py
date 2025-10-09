import pandas as pd
import numpy as np
from typing import Dict, List
import warnings

class TechnicalIndicators:
    def __init__(self):
        self.indicators_config = {
            "trend": ["MA", "EMA", "MACD", "ADX"],
            "momentum": ["RSI", "Stochastic", "WilliamsR", "CCI"],
            "volatility": ["BollingerBands", "ATR", "StandardDeviation"],
            "volume": ["Volume", "OBV", "VolumeProfile"]
        }

    def calculate_moving_averages(self, df: pd.DataFrame) -> Dict:
        """计算移动平均线"""
        indicators = {}
        
        try:
            # 简单移动平均线
            indicators['MA5'] = df['close'].tail(5).mean()
            indicators['MA10'] = df['close'].tail(10).mean()
            indicators['MA20'] = df['close'].tail(20).mean()
            indicators['MA50'] = df['close'].tail(50).mean() if len(df) >= 50 else None
            indicators['MA200'] = df['close'].tail(200).mean() if len(df) >= 200 else None
            
            # 指数移动平均线
            indicators['EMA12'] = df['close'].ewm(span=12).mean().iloc[-1]
            indicators['EMA26'] = df['close'].ewm(span=26).mean().iloc[-1]
            
            # 移动平均线信号
            if indicators['MA5'] and indicators['MA10'] and indicators['MA20']:
                if indicators['MA5'] > indicators['MA10'] > indicators['MA20']:
                    indicators['MA_Signal'] = "强烈看涨"
                elif indicators['MA5'] < indicators['MA10'] < indicators['MA20']:
                    indicators['MA_Signal'] = "强烈看跌"
                else:
                    indicators['MA_Signal'] = "震荡整理"
            
        except Exception as e:
            print(f"[ERROR] 移动平均线计算失败: {e}")
            
        return indicators

    def calculate_rsi(self, df: pd.DataFrame, period: int = 14) -> float:
        """计算相对强弱指数RSI"""
        try:
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50
        except:
            return 50

    def calculate_macd(self, df: pd.DataFrame) -> Dict:
        """计算MACD指标"""
        macd_data = {}
        
        try:
            ema12 = df['close'].ewm(span=12).mean()
            ema26 = df['close'].ewm(span=26).mean()
            macd_data['MACD'] = (ema12 - ema26).iloc[-1]
            macd_data['MACD_Signal'] = (ema12 - ema26).ewm(span=9).mean().iloc[-1]
            macd_data['MACD_Histogram'] = macd_data['MACD'] - macd_data['MACD_Signal']
            
            # MACD信号
            if macd_data['MACD'] > macd_data['MACD_Signal'] and macd_data['MACD_Histogram'] > 0:
                macd_data['MACD_Signal'] = "看涨"
            elif macd_data['MACD'] < macd_data['MACD_Signal'] and macd_data['MACD_Histogram'] < 0:
                macd_data['MACD_Signal'] = "看跌"
            else:
                macd_data['MACD_Signal'] = "中性"
                
        except Exception as e:
            print(f"[ERROR] MACD计算失败: {e}")
            
        return macd_data

    def calculate_bollinger_bands(self, df: pd.DataFrame, period: int = 20, std: int = 2) -> Dict:
        """计算布林带"""
        bb_data = {}
        
        try:
            rolling_mean = df['close'].rolling(window=period).mean()
            rolling_std = df['close'].rolling(window=period).std()
            
            bb_data['BB_Upper'] = rolling_mean.iloc[-1] + (rolling_std.iloc[-1] * std)
            bb_data['BB_Middle'] = rolling_mean.iloc[-1]
            bb_data['BB_Lower'] = rolling_mean.iloc[-1] - (rolling_std.iloc[-1] * std)
            
            # 布林带位置
            current_price = df['close'].iloc[-1]
            bb_range = bb_data['BB_Upper'] - bb_data['BB_Lower']
            if bb_range > 0:
                bb_position = (current_price - bb_data['BB_Lower']) / bb_range
                bb_data['BB_Position'] = bb_position
                
                if bb_position > 0.8:
                    bb_data['BB_Signal'] = "超买区域"
                elif bb_position < 0.2:
                    bb_data['BB_Signal'] = "超卖区域"
                else:
                    bb_data['BB_Signal'] = "正常区域"
                    
            # 布林带宽度（波动率指标）
            bb_data['BB_Width'] = (bb_data['BB_Upper'] - bb_data['BB_Lower']) / bb_data['BB_Middle']
            
        except Exception as e:
            print(f"[ERROR] 布林带计算失败: {e}")
            
        return bb_data

    def calculate_stochastic(self, df: pd.DataFrame, k_period: int = 14, d_period: int = 3) -> Dict:
        """计算随机指标"""
        stoch_data = {}
        
        try:
            low_14 = df['low'].rolling(window=k_period).min()
            high_14 = df['high'].rolling(window=k_period).max()
            
            stoch_data['%K'] = 100 * ((df['close'] - low_14) / (high_14 - low_14))
            stoch_data['%D'] = stoch_data['%K'].rolling(window=d_period).mean()
            
            current_k = stoch_data['%K'].iloc[-1] if not pd.isna(stoch_data['%K'].iloc[-1]) else 50
            current_d = stoch_data['%D'].iloc[-1] if not pd.isna(stoch_data['%D'].iloc[-1]) else 50
            
            # 随机指标信号
            if current_k > 80 and current_d > 80:
                stoch_data['Stoch_Signal'] = "超买"
            elif current_k < 20 and current_d < 20:
                stoch_data['Stoch_Signal'] = "超卖"
            elif current_k > current_d:
                stoch_data['Stoch_Signal'] = "看涨"
            elif current_k < current_d:
                stoch_data['Stoch_Signal'] = "看跌"
            else:
                stoch_data['Stoch_Signal'] = "中性"
                
        except Exception as e:
            print(f"[ERROR] 随机指标计算失败: {e}")
            
        return stoch_data

    def calculate_volume_indicators(self, df: pd.DataFrame) -> Dict:
        """计算成交量指标"""
        volume_data = {}
        
        try:
            # 成交量移动平均
            volume_data['Volume_MA5'] = df['volume'].tail(5).mean()
            volume_data['Volume_MA20'] = df['volume'].tail(20).mean()
            
            # 量价关系
            current_volume = df['volume'].iloc[-1]
            price_change = (df['close'].iloc[-1] - df['close'].iloc[-2]) / df['close'].iloc[-2] * 100 if len(df) >= 2 else 0
            
            if price_change > 0 and current_volume > volume_data['Volume_MA20']:
                volume_data['Volume_Price_Signal'] = "放量上涨"
            elif price_change > 0 and current_volume < volume_data['Volume_MA20']:
                volume_data['Volume_Price_Signal'] = "缩量上涨"
            elif price_change < 0 and current_volume > volume_data['Volume_MA20']:
                volume_data['Volume_Price_Signal'] = "放量下跌"
            elif price_change < 0 and current_volume < volume_data['Volume_MA20']:
                volume_data['Volume_Price_Signal'] = "缩量下跌"
            else:
                volume_data['Volume_Price_Signal'] = "量价正常"
                
            # 能量潮(OBV)
            obv = [0]
            for i in range(1, len(df)):
                if df['close'].iloc[i] > df['close'].iloc[i-1]:
                    obv.append(obv[-1] + df['volume'].iloc[i])
                elif df['close'].iloc[i] < df['close'].iloc[i-1]:
                    obv.append(obv[-1] - df['volume'].iloc[i])
                else:
                    obv.append(obv[-1])
            
            volume_data['OBV'] = obv[-1] if obv else 0
            volume_data['OBV_MA5'] = pd.Series(obv).tail(5).mean() if len(obv) >= 5 else 0
            
        except Exception as e:
            print(f"[ERROR] 成交量指标计算失败: {e}")
            
        return volume_data

    def calculate_atr(self, df: pd.DataFrame, period: int = 14) -> float:
        """计算平均真实波幅ATR"""
        try:
            high_low = df['high'] - df['low']
            high_close = abs(df['high'] - df['close'].shift())
            low_close = abs(df['low'] - df['close'].shift())
            
            true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            atr = true_range.rolling(window=period).mean()
            return atr.iloc[-1] if not pd.isna(atr.iloc[-1]) else 0
        except:
            return 0

    def calculate_all_indicators(self, df: pd.DataFrame) -> Dict:
        """计算所有技术指标"""
        if df is None or len(df) < 20:
            return {}
            
        indicators = {}
        
        try:
            # 移动平均线
            ma_indicators = self.calculate_moving_averages(df)
            indicators.update(ma_indicators)
            
            # RSI
            indicators['RSI'] = self.calculate_rsi(df)
            if indicators['RSI'] > 70:
                indicators['RSI_Signal'] = "超买"
            elif indicators['RSI'] < 30:
                indicators['RSI_Signal'] = "超卖"
            else:
                indicators['RSI_Signal'] = "正常"
            
            # MACD
            macd_indicators = self.calculate_macd(df)
            indicators.update(macd_indicators)
            
            # 布林带
            bb_indicators = self.calculate_bollinger_bands(df)
            indicators.update(bb_indicators)
            
            # 随机指标
            stoch_indicators = self.calculate_stochastic(df)
            indicators.update(stoch_indicators)
            
            # 成交量指标
            volume_indicators = self.calculate_volume_indicators(df)
            indicators.update(volume_indicators)
            
            # ATR
            indicators['ATR'] = self.calculate_atr(df)
            indicators['ATR_Percent'] = indicators['ATR'] / df['close'].iloc[-1] * 100 if df['close'].iloc[-1] > 0 else 0
            
            # 价格动量
            if len(df) >= 10:
                indicators['Momentum_10'] = (df['close'].iloc[-1] - df['close'].iloc[-10]) / df['close'].iloc[-10] * 100
            
            # 价格波动率
            if len(df) >= 20:
                returns = df['close'].pct_change().dropna()
                indicators['Volatility_20'] = returns.tail(20).std() * np.sqrt(252) * 100  # 年化波动率
            
            # 综合信号
            bullish_signals = 0
            bearish_signals = 0
            
            # RSI信号
            if indicators.get('RSI_Signal') == "超卖":
                bullish_signals += 1
            elif indicators.get('RSI_Signal') == "超买":
                bearish_signals += 1
            
            # MACD信号
            if indicators.get('MACD_Signal') == "看涨":
                bullish_signals += 1
            elif indicators.get('MACD_Signal') == "看跌":
                bearish_signals += 1
            
            # 布林带信号
            if indicators.get('BB_Signal') == "超卖区域":
                bullish_signals += 1
            elif indicators.get('BB_Signal') == "超买区域":
                bearish_signals += 1
            
            # 随机指标信号
            if indicators.get('Stoch_Signal') == "超卖":
                bullish_signals += 1
            elif indicators.get('Stoch_Signal') == "超买":
                bearish_signals += 1
            
            # 移动平均线信号
            if indicators.get('MA_Signal') == "强烈看涨":
                bullish_signals += 2
            elif indicators.get('MA_Signal') == "强烈看跌":
                bearish_signals += 2
            
            # 量价信号
            if indicators.get('Volume_Price_Signal') == "放量上涨":
                bullish_signals += 1
            elif indicators.get('Volume_Price_Signal') == "放量下跌":
                bearish_signals += 1
            
            # 综合评级
            total_signals = bullish_signals + bearish_signals
            if total_signals > 0:
                if bullish_signals > bearish_signals * 1.5:
                    indicators['Overall_Signal'] = "强烈看涨"
                elif bullish_signals > bearish_signals:
                    indicators['Overall_Signal'] = "看涨"
                elif bearish_signals > bullish_signals * 1.5:
                    indicators['Overall_Signal'] = "强烈看跌"
                elif bearish_signals > bullish_signals:
                    indicators['Overall_Signal'] = "看跌"
                else:
                    indicators['Overall_Signal'] = "中性"
            else:
                indicators['Overall_Signal'] = "无明确信号"
                
        except Exception as e:
            print(f"[ERROR] 技术指标计算失败: {e}")
            
        return indicators