"""
IDX Technical Analysis Library
Shared library for autonomous agent and web dashboard
Manual calculations - no external dependencies
"""

import pandas as pd
import numpy as np

class IDXTechnicalAnalysis:
    """
    Unified technical analysis library for IDX stocks
    Compatible with both yfinance and yahooquery data sources
    """
    
    @staticmethod
    def calculate_rsi(data, period=14):
        """Calculate RSI manually"""
        if isinstance(data, pd.Series):
            delta = data.diff()
        else:
            delta = pd.Series(data).diff()
        
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        # Handle division by zero
        rs = gain / loss.replace(0, np.nan)
        rsi = 100 - (100 / (1 + rs))
        
        return rsi.fillna(50)  # Default to neutral RSI
    
    @staticmethod
    def calculate_sma(data, period):
        """Calculate Simple Moving Average"""
        if isinstance(data, pd.Series):
            return data.rolling(window=period).mean()
        else:
            return pd.Series(data).rolling(window=period).mean()
    
    @staticmethod
    def calculate_ema(data, period):
        """Calculate Exponential Moving Average"""
        if isinstance(data, pd.Series):
            return data.ewm(span=period).mean()
        else:
            return pd.Series(data).ewm(span=period).mean()
    
    @staticmethod
    def calculate_bollinger_bands(data, period=20, std_dev=2):
        """Calculate Bollinger Bands"""
        if isinstance(data, pd.Series):
            sma = data.rolling(window=period).mean()
            std = data.rolling(window=period).std()
        else:
            series = pd.Series(data)
            sma = series.rolling(window=period).mean()
            std = series.rolling(window=period).std()
        
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        
        return upper_band, sma, lower_band
    
    @staticmethod
    def calculate_atr(high, low, close, period=14):
        """Calculate Average True Range"""
        # Convert to pandas Series if needed
        if not isinstance(high, pd.Series):
            high = pd.Series(high)
        if not isinstance(low, pd.Series):
            low = pd.Series(low)
        if not isinstance(close, pd.Series):
            close = pd.Series(close)
        
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        
        return atr.fillna(0)
    
    @staticmethod
    def calculate_macd(data, fast=12, slow=26, signal=9):
        """Calculate MACD"""
        if isinstance(data, pd.Series):
            series = data
        else:
            series = pd.Series(data)
        
        ema_fast = series.ewm(span=fast).mean()
        ema_slow = series.ewm(span=slow).mean()
        
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal).mean()
        histogram = macd_line - signal_line
        
        return {
            'macd': macd_line.fillna(0),
            'signal': signal_line.fillna(0),
            'histogram': histogram.fillna(0)
        }
    
    @staticmethod
    def calculate_volume_sma(volume, period=20):
        """Calculate Volume Simple Moving Average"""
        if isinstance(volume, pd.Series):
            return volume.rolling(window=period).mean()
        else:
            return pd.Series(volume).rolling(window=period).mean()
    
    @staticmethod
    def calculate_volatility(prices, period=252):
        """Calculate annualized volatility"""
        if isinstance(prices, pd.Series):
            returns = prices.pct_change()
        else:
            returns = pd.Series(prices).pct_change()
        
        volatility = returns.std() * np.sqrt(period)
        return volatility.fillna(0)
    
    @staticmethod
    def calculate_trend_strength(data, period=50):
        """Calculate trend strength using linear regression slope"""
        if isinstance(data, pd.Series):
            series = data
        else:
            series = pd.Series(data)
        
        if len(series) < period:
            return 0.5  # Default neutral trend strength
        
        # Use last 'period' data points
        recent_data = series.tail(period)
        
        # Linear regression slope
        x = np.arange(len(recent_data))
        y = recent_data.values
        
        # Calculate slope
        slope = np.polyfit(x, y, 1)[0]
        
        # Normalize slope
        price_range = recent_data.max() - recent_data.min()
        if price_range > 0:
            normalized_slope = (slope * len(recent_data)) / price_range
        else:
            normalized_slope = 0
        
        # Convert to 0-1 scale (absolute value)
        trend_strength = abs(normalized_slope)
        
        return min(1.0, max(0.0, trend_strength))
    
    @staticmethod
    def find_support_resistance(data, lookback=50):
        """Find support and resistance levels"""
        if isinstance(data, pd.Series):
            series = data
        else:
            series = pd.Series(data)
        
        if len(series) < lookback:
            return {'support': 0, 'resistance': 0}
        
        recent_data = series.tail(lookback)
        current_price = recent_data.iloc[-1]
        
        # Find local maxima and minima
        highs = []
        lows = []
        
        for i in range(2, len(recent_data) - 2):
            current_high = recent_data.iloc[i]
            current_low = recent_data.iloc[i]
            
            # Local maximum
            if (current_high > recent_data.iloc[i-1] and 
                current_high > recent_data.iloc[i-2] and
                current_high > recent_data.iloc[i+1] and
                current_high > recent_data.iloc[i+2]):
                highs.append(current_high)
            
            # Local minimum
            if (current_low < recent_data.iloc[i-1] and 
                current_low < recent_data.iloc[i-2] and
                current_low < recent_data.iloc[i+1] and
                current_low < recent_data.iloc[i+2]):
                lows.append(current_low)
        
        # Find nearest resistance above current price
        resistance_levels = [h for h in highs if h > current_price]
        resistance = min(resistance_levels) if resistance_levels else current_price * 1.1
        
        # Find nearest support below current price
        support_levels = [l for l in lows if l < current_price]
        support = max(support_levels) if support_levels else current_price * 0.9
        
        return {
            'support': float(support),
            'resistance': float(resistance),
            'support_distance_pct': ((current_price - support) / current_price) * 100,
            'resistance_distance_pct': ((resistance - current_price) / current_price) * 100
        }
    
    @staticmethod
    def calculate_bollinger_position(price, upper_band, lower_band):
        """Calculate position within Bollinger Bands"""
        if upper_band - lower_band == 0:
            return 0.5  # Middle position if bands are flat
        
        position = (price - lower_band) / (upper_band - lower_band)
        return max(0.0, min(1.0, position))
    
    @staticmethod
    def analyze_volume_sentiment(df):
        """Analyze volume sentiment (accumulation/distribution)"""
        if 'close' not in df.columns or 'open' not in df.columns or 'volume' not in df.columns:
            return "Neutral"
        
        df['vol_sentiment'] = (df['close'] - df['open']) * df['volume']
        recent_sentiment = df['vol_sentiment'].tail(5).sum()
        
        if recent_sentiment > 0:
            return "Accumulation 🟢"
        elif recent_sentiment < 0:
            return "Distribution 🔴"
        else:
            return "Neutral"
    
    @staticmethod
    def get_risk_level(volatility):
        """Get risk level based on volatility"""
        if volatility < 0.20:
            return "Low 🔵"
        elif volatility < 0.35:
            return "Medium 🟡"
        else:
            return "High 🔴"
    
    @staticmethod
    def get_recommendation(rsi, is_elite_fundamental, rsi_oversold=35, rsi_overbought=65):
        """Get trading recommendation based on RSI and fundamentals"""
        if rsi < rsi_oversold and is_elite_fundamental:
            return "BUY 🚀"
        elif rsi > rsi_overbought:
            return "SELL 📉"
        else:
            return "Wait for Dip ⏳"
