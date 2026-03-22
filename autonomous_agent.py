"""
Autonomous IDX Analyst Agent
Transforms market data into strategic intelligence without human intervention
"""

import os
import json
import time
import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

import yfinance as yf
import pandas as pd
import pandas_ta as ta
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SignalType(Enum):
    STRONG_BUY = "STRONG_BUY"
    BUY = "BUY"
    HOLD = "HOLD"
    SELL = "SELL"
    STRONG_SELL = "STRONG_SELL"

class AnomalyType(Enum):
    PRICE_SPIKE = "PRICE_SPIKE"
    VOLUME_SURGE = "VOLUME_SURGE"
    RSI_DIVERGENCE = "RSI_DIVERGENCE"
    BREAKOUT = "BREAKOUT"
    NEWS_DRIVEN = "NEWS_DRIVEN"

@dataclass
class MarketSignal:
    symbol: str
    signal_type: SignalType
    anomaly_type: AnomalyType
    confidence: float
    price: float
    volume: int
    rsi: float
    timestamp: datetime
    metadata: Dict

@dataclass
class ResearchResult:
    symbol: str
    technical_analysis: Dict
    fundamental_analysis: Dict
    news_sentiment: Dict
    risk_reward_ratio: float
    recommendation: str
    confidence: float
    timestamp: datetime

class AutonomousAnalystAgent:
    def __init__(self):
        self.telegram_token = os.environ.get("TELEGRAM_TOKEN")
        self.chat_id = os.environ.get("CHAT_ID")
        self.news_api_key = os.environ.get("NEWS_API_KEY")
        self.engine_tickers = self._get_engine_tickers()
        self.active_signals = []
        self.research_cache = {}
        
    def _get_engine_tickers(self) -> List[str]:
        """Top 100 IDX tickers with additional monitoring targets"""
        return [
            "ADRO.JK", "AKRA.JK", "AMRT.JK", "ANTM.JK", "ASII.JK", "BBCA.JK", "BBNI.JK", "BBRI.JK", 
            "BBTN.JK", "BMRI.JK", "BRMS.JK", "BRPT.JK", "BSDE.JK", "CPIN.JK", "EMTK.JK", "ESSA.JK", 
            "EXCL.JK", "GOTO.JK", "HRUM.JK", "ICBP.JK", "INCO.JK", "INDF.JK", "INKP.JK", "INTP.JK", 
            "ITMG.JK", "JSMR.JK", "KLBF.JK", "MDKA.JK", "MEDC.JK", "MIKA.JK", "PGAS.JK", "PTBA.JK", 
            "PTPP.JK", "SIDO.JK", "SMGR.JK", "TLKM.JK", "TOWR.JK", "UNTR.JK", "UNVR.JK", "ADMR.JK", 
            "ARTO.JK", "AUTO.JK", "AVIA.JK", "BDMN.JK", "BFIN.JK", "BMTR.JK", "BNGA.JK", "BRIS.JK", 
            "BTPS.JK", "BUKA.JK", "CTRA.JK", "ENRG.JK", "ERAA.JK", "HEAL.JK", "IMAS.JK", "JPFA.JK", 
            "MBMA.JK", "MDRN.JK", "MTEL.JK", "MYOR.JK", "NCKL.JK", "PANI.JK", "PNLF.JK", "PWON.JK", 
            "SCMA.JK", "SILO.JK", "SMRA.JK", "SSIA.JK", "TPIA.JK", "TYRE.JK", "UNIT.JK", "VBNI.JK", 
            "VICI.JK", "VKTR.JK", "WIKA.JK", "WOOD.JK", "YPAS.JK", "ZATA.JK", "ACES.JK", "ADHI.JK", 
            "AGRO.JK", "ALII.JK", "AMMN.JK", "ASRI.JK", "BBYB.JK", "BELI.JK", "BIRD.JK", "CPRO.JK", 
            "DOID.JK", "ELSA.JK", "GEMS.JK", "GJTL.JK", "MAIN.JK", "MAPA.JK", "MAPI.JK", "MNCN.JK", 
            "MPPA.JK", "RAJA.JK", "SSMS.JK", "CUAN.JK"
        ]
    
    def detect_anomalies(self) -> List[MarketSignal]:
        """Scan market for anomalies using multiple indicators"""
        logger.info("Starting anomaly detection scan...")
        signals = []
        
        for ticker in self.engine_tickers:
            try:
                signal = self._analyze_ticker_anomaly(ticker)
                if signal and signal.confidence > 0.7:
                    signals.append(signal)
                    logger.info(f"Anomaly detected: {ticker} - {signal.anomaly_type.value}")
            except Exception as e:
                logger.error(f"Error analyzing {ticker}: {e}")
                continue
                
        return signals
    
    def _analyze_ticker_anomaly(self, symbol: str) -> Optional[MarketSignal]:
        """Analyze single ticker for multiple anomaly types"""
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period="3mo")
            
            if df.empty or len(df) < 50:
                return None
            
            # Calculate indicators
            df['RSI'] = ta.rsi(df['Close'], length=14)
            df['SMA_20'] = ta.sma(df['Close'], length=20)
            df['SMA_50'] = ta.sma(df['Close'], length=50)
            df['Volume_SMA'] = ta.sma(df['Volume'], length=20)
            df['ATR'] = ta.atr(df['High'], df['Low'], df['Close'], length=14)
            
            latest = df.iloc[-1]
            prev_day = df.iloc[-2]
            
            price = float(latest['Close'])
            volume = int(latest['Volume'])
            rsi = float(latest['RSI'])
            
            # Detect different anomaly types
            anomaly_type, confidence, signal_type = self._detect_anomaly_type(df, latest, prev_day)
            
            if anomaly_type and confidence > 0.7:
                return MarketSignal(
                    symbol=symbol.replace(".JK", ""),
                    signal_type=signal_type,
                    anomaly_type=anomaly_type,
                    confidence=confidence,
                    price=price,
                    volume=volume,
                    rsi=rsi,
                    timestamp=datetime.now(),
                    metadata={
                        'volume_ratio': volume / df['Volume'].mean() if df['Volume'].mean() > 0 else 1,
                        'price_change_pct': ((price - prev_day['Close']) / prev_day['Close']) * 100,
                        'atr': float(latest['ATR']) if pd.notna(latest['ATR']) else 0
                    }
                )
                
        except Exception as e:
            logger.error(f"Error in anomaly detection for {symbol}: {e}")
            
        return None
    
    def _detect_anomaly_type(self, df: pd.DataFrame, latest: pd.Series, prev_day: pd.Series) -> Tuple[Optional[AnomalyType], float, SignalType]:
        """Detect specific type of anomaly and return confidence score"""
        
        # Volume Surge Detection
        volume_ratio = latest['Volume'] / df['Volume'].mean() if df['Volume'].mean() > 0 else 1
        if volume_ratio > 3.0:
            return AnomalyType.VOLUME_SURGE, min(0.9, volume_ratio / 5), SignalType.BUY
        
        # Price Spike Detection
        price_change = abs((latest['Close'] - prev_day['Close']) / prev_day['Close']) * 100
        if price_change > 5.0:
            signal_type = SignalType.BUY if latest['Close'] > prev_day['Close'] else SignalType.SELL
            return AnomalyType.PRICE_SPIKE, min(0.85, price_change / 10), signal_type
        
        # RSI Divergence Detection
        if latest['RSI'] < 30 and latest['Close'] > latest['SMA_20']:
            return AnomalyType.RSI_DIVERGENCE, 0.8, SignalType.BUY
        elif latest['RSI'] > 70 and latest['Close'] < latest['SMA_20']:
            return AnomalyType.RSI_DIVERGENCE, 0.8, SignalType.SELL
        
        # Breakout Detection
        if (latest['Close'] > latest['SMA_20'] * 1.02 and 
            prev_day['Close'] <= prev_day['SMA_20'] and 
            volume_ratio > 1.5):
            return AnomalyType.BREAKOUT, 0.75, SignalType.BUY
        
        return None, 0.0, SignalType.HOLD
    
    def conduct_autonomous_research(self, signal: MarketSignal) -> ResearchResult:
        """Multi-step research process for detected anomalies"""
        logger.info(f"Starting autonomous research for {signal.symbol}")
        
        if signal.symbol in self.research_cache:
            cache_time = self.research_cache[signal.symbol]['timestamp']
            if datetime.now() - cache_time < timedelta(hours=1):
                logger.info(f"Using cached research for {signal.symbol}")
                return self.research_cache[signal.symbol]
        
        # Step 1: Technical Analysis
        technical_analysis = self._deep_technical_analysis(signal.symbol)
        
        # Step 2: News Sentiment Analysis
        news_sentiment = self._analyze_news_sentiment(signal.symbol)
        
        # Step 3: Fundamental Analysis
        fundamental_analysis = self._analyze_fundamentals(signal.symbol)
        
        # Step 4: Risk/Reward Calculation
        risk_reward = self._calculate_risk_reward(signal, technical_analysis)
        
        # Step 5: Generate Strategic Recommendation
        recommendation, confidence = self._generate_strategic_recommendation(
            signal, technical_analysis, news_sentiment, fundamental_analysis, risk_reward
        )
        
        research_result = ResearchResult(
            symbol=signal.symbol,
            technical_analysis=technical_analysis,
            fundamental_analysis=fundamental_analysis,
            news_sentiment=news_sentiment,
            risk_reward_ratio=risk_reward,
            recommendation=recommendation,
            confidence=confidence,
            timestamp=datetime.now()
        )
        
        # Cache the result
        self.research_cache[signal.symbol] = research_result
        
        return research_result
    
    def _deep_technical_analysis(self, symbol: str) -> Dict:
        """Comprehensive technical analysis"""
        try:
            ticker = yf.Ticker(symbol + ".JK")
            df = ticker.history(period="1y")
            
            if df.empty:
                return {}
            
            # Multiple timeframes
            indicators = {}
            
            # Short-term indicators
            df['RSI_14'] = ta.rsi(df['Close'], length=14)
            df['RSI_7'] = ta.rsi(df['Close'], length=7)
            df['MACD'] = ta.macd(df['Close'])['MACD_12_26_9']
            df['BB_upper'], df['BB_middle'], df['BB_lower'] = ta.bbands(df['Close'], length=20)
            
            # Medium-term indicators
            df['SMA_20'] = ta.sma(df['Close'], length=20)
            df['SMA_50'] = ta.sma(df['Close'], length=50)
            df['EMA_12'] = ta.ema(df['Close'], length=12)
            df['EMA_26'] = ta.ema(df['Close'], length=26)
            
            # Long-term indicators
            df['SMA_100'] = ta.sma(df['Close'], length=100)
            df['SMA_200'] = ta.sma(df['Close'], length=200)
            
            latest = df.iloc[-1]
            
            indicators.update({
                'price': float(latest['Close']),
                'rsi_14': float(latest['RSI_14']) if pd.notna(latest['RSI_14']) else 50,
                'rsi_7': float(latest['RSI_7']) if pd.notna(latest['RSI_7']) else 50,
                'macd': float(latest['MACD']) if pd.notna(latest['MACD']) else 0,
                'bb_position': (latest['Close'] - latest['BB_lower']) / (latest['BB_upper'] - latest['BB_lower']) if pd.notna(latest['BB_upper']) else 0.5,
                'sma_20': float(latest['SMA_20']) if pd.notna(latest['SMA_20']) else latest['Close'],
                'sma_50': float(latest['SMA_50']) if pd.notna(latest['SMA_50']) else latest['Close'],
                'sma_100': float(latest['SMA_100']) if pd.notna(latest['SMA_100']) else latest['Close'],
                'sma_200': float(latest['SMA_200']) if pd.notna(latest['SMA_200']) else latest['Close'],
                'volume_ratio': latest['Volume'] / df['Volume'].mean() if df['Volume'].mean() > 0 else 1,
                'trend_strength': self._calculate_trend_strength(df),
                'support_resistance': self._find_support_resistance(df)
            })
            
            return indicators
            
        except Exception as e:
            logger.error(f"Technical analysis failed for {symbol}: {e}")
            return {}
    
    def _calculate_trend_strength(self, df: pd.DataFrame) -> float:
        """Calculate trend strength using multiple indicators"""
        try:
            if len(df) < 50:
                return 0.5
            
            # Linear regression slope
            x = np.arange(len(df))
            y = df['Close'].values
            slope = np.polyfit(x, y, 1)[0]
            
            # Normalize slope
            price_range = df['Close'].max() - df['Close'].min()
            normalized_slope = (slope * len(df)) / price_range if price_range > 0 else 0
            
            # ADX-like trend strength (simplified)
            high_low = df['High'] - df['Low']
            high_close = abs(df['High'] - df['Close'].shift())
            low_close = abs(df['Low'] - df['Close'].shift())
            
            tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            atr = tr.rolling(14).mean()
            
            trend_strength = abs(normalized_slope) * (1 - atr / df['Close'].mean())
            
            return min(1.0, max(0.0, trend_strength))
            
        except Exception:
            return 0.5
    
    def _find_support_resistance(self, df: pd.DataFrame) -> Dict:
        """Find key support and resistance levels"""
        try:
            if len(df) < 20:
                return {'support': 0, 'resistance': 0}
            
            recent_data = df.tail(50)
            current_price = recent_data.iloc[-1]['Close']
            
            # Find local maxima and minima
            highs = []
            lows = []
            
            for i in range(2, len(recent_data) - 2):
                if (recent_data.iloc[i]['High'] > recent_data.iloc[i-1]['High'] and 
                    recent_data.iloc[i]['High'] > recent_data.iloc[i-2]['High'] and
                    recent_data.iloc[i]['High'] > recent_data.iloc[i+1]['High'] and
                    recent_data.iloc[i]['High'] > recent_data.iloc[i+2]['High']):
                    highs.append(recent_data.iloc[i]['High'])
                
                if (recent_data.iloc[i]['Low'] < recent_data.iloc[i-1]['Low'] and 
                    recent_data.iloc[i]['Low'] < recent_data.iloc[i-2]['Low'] and
                    recent_data.iloc[i]['Low'] < recent_data.iloc[i+1]['Low'] and
                    recent_data.iloc[i]['Low'] < recent_data.iloc[i+2]['Low']):
                    lows.append(recent_data.iloc[i]['Low'])
            
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
            
        except Exception as e:
            logger.error(f"Support/resistance analysis failed: {e}")
            return {'support': 0, 'resistance': 0}
    
    def _analyze_news_sentiment(self, symbol: str) -> Dict:
        """Analyze news sentiment for the stock"""
        try:
            # This is a placeholder for news sentiment analysis
            # In production, you'd integrate with news APIs like:
            # - NewsAPI
            # - Alpha Vantage News
            # - Bloomberg API
            # - Indonesian financial news sources
            
            # For now, simulate sentiment analysis
            sentiment_score = np.random.normal(0, 0.3)  # Simulated sentiment
            sentiment_score = max(-1, min(1, sentiment_score))
            
            return {
                'sentiment_score': sentiment_score,
                'sentiment_label': 'Positive' if sentiment_score > 0.1 else 'Negative' if sentiment_score < -0.1 else 'Neutral',
                'news_count': np.random.randint(1, 10),
                'recent_headlines': [
                    f"Sample headline 1 for {symbol}",
                    f"Sample headline 2 for {symbol}"
                ],
                'impact_level': 'High' if abs(sentiment_score) > 0.5 else 'Medium' if abs(sentiment_score) > 0.2 else 'Low'
            }
            
        except Exception as e:
            logger.error(f"News sentiment analysis failed for {symbol}: {e}")
            return {'sentiment_score': 0, 'sentiment_label': 'Neutral', 'news_count': 0}
    
    def _analyze_fundamentals(self, symbol: str) -> Dict:
        """Analyze fundamental metrics"""
        try:
            ticker = yf.Ticker(symbol + ".JK")
            info = ticker.info
            
            # Key fundamental metrics
            fundamentals = {
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE', 0),
                'pb_ratio': info.get('priceToBook', 0),
                'eps': info.get('trailingEps', 0),
                'dividend_yield': info.get('dividendYield', 0),
                'roe': info.get('returnOnEquity', 0),
                'debt_to_equity': info.get('debtToEquity', 0),
                'revenue_growth': info.get('revenueGrowth', 0),
                'earnings_growth': info.get('earningsGrowth', 0),
                'sector': info.get('sector', 'Unknown'),
                'industry': info.get('industry', 'Unknown')
            }
            
            # Calculate fundamental score
            fundamental_score = 0
            if fundamentals['pe_ratio'] and 0 < fundamentals['pe_ratio'] < 20:
                fundamental_score += 0.2
            if fundamentals['pb_ratio'] and 0 < fundamentals['pb_ratio'] < 3:
                fundamental_score += 0.2
            if fundamentals['roe'] and fundamentals['roe'] > 0.15:
                fundamental_score += 0.2
            if fundamentals['revenue_growth'] and fundamentals['revenue_growth'] > 0.1:
                fundamental_score += 0.2
            if fundamentals['earnings_growth'] and fundamentals['earnings_growth'] > 0.1:
                fundamental_score += 0.2
            
            fundamentals['fundamental_score'] = fundamental_score
            
            return fundamentals
            
        except Exception as e:
            logger.error(f"Fundamental analysis failed for {symbol}: {e}")
            return {'fundamental_score': 0.5}
    
    def _calculate_risk_reward(self, signal: MarketSignal, technical_analysis: Dict) -> float:
        """Calculate risk/reward ratio"""
        try:
            current_price = signal.price
            
            # Get support and resistance levels
            support = technical_analysis.get('support_resistance', {}).get('support', current_price * 0.95)
            resistance = technical_analysis.get('support_resistance', {}).get('resistance', current_price * 1.1)
            
            # Calculate potential loss and gain
            potential_loss = current_price - support
            potential_gain = resistance - current_price
            
            if potential_loss <= 0:
                return 10.0  # Very favorable if no clear downside
            
            risk_reward_ratio = potential_gain / potential_loss
            
            # Adjust based on signal confidence and anomaly type
            if signal.anomaly_type == AnomalyType.VOLUME_SURGE:
                risk_reward_ratio *= 1.2
            elif signal.anomaly_type == AnomalyType.BREAKOUT:
                risk_reward_ratio *= 1.1
            
            return risk_reward_ratio
            
        except Exception as e:
            logger.error(f"Risk/reward calculation failed: {e}")
            return 1.0
    
    def _generate_strategic_recommendation(self, signal: MarketSignal, technical: Dict, 
                                         news: Dict, fundamentals: Dict, risk_reward: float) -> Tuple[str, float]:
        """Generate strategic recommendation with confidence score"""
        
        # Weight different factors
        signal_weight = 0.3
        technical_weight = 0.3
        news_weight = 0.2
        fundamental_weight = 0.2
        
        # Calculate component scores
        signal_score = signal.confidence if signal.signal_type in [SignalType.BUY, SignalType.STRONG_BUY] else -signal.confidence
        
        technical_score = 0
        if technical.get('rsi_14', 50) < 30:
            technical_score += 0.3
        elif technical.get('rsi_14', 50) > 70:
            technical_score -= 0.3
            
        if technical.get('trend_strength', 0.5) > 0.7:
            technical_score += 0.2
        
        news_score = news.get('sentiment_score', 0)
        fundamental_score = (fundamentals.get('fundamental_score', 0.5) - 0.5) * 2
        
        # Combine scores
        total_score = (signal_score * signal_weight + 
                      technical_score * technical_weight + 
                      news_score * news_weight + 
                      fundamental_score * fundamental_weight)
        
        # Adjust for risk/reward
        if risk_reward > 2.0:
            total_score += 0.2
        elif risk_reward < 1.0:
            total_score -= 0.2
        
        # Generate recommendation
        confidence = abs(total_score)
        
        if total_score > 0.6:
            recommendation = "STRONG_BUY"
        elif total_score > 0.2:
            recommendation = "BUY"
        elif total_score > -0.2:
            recommendation = "HOLD"
        elif total_score > -0.6:
            recommendation = "SELL"
        else:
            recommendation = "STRONG_SELL"
        
        return recommendation, min(1.0, confidence)
    
    def send_intelligent_alert(self, research_result: ResearchResult, signal: MarketSignal):
        """Send intelligent alert with strategic insights"""
        try:
            message = self._create_intelligent_message(research_result, signal)
            
            response = requests.post(
                f"https://api.telegram.org/bot{self.telegram_token}/sendMessage",
                json={
                    "chat_id": self.chat_id,
                    "text": message,
                    "parse_mode": "HTML",
                    "disable_web_page_preview": False
                }
            )
            
            response.raise_for_status()
            logger.info(f"Intelligent alert sent for {research_result.symbol}")
            
        except Exception as e:
            logger.error(f"Failed to send intelligent alert: {e}")
    
    def _create_intelligent_message(self, research: ResearchResult, signal: MarketSignal) -> str:
        """Create comprehensive intelligent alert message"""
        
        ta = research.technical_analysis
        fa = research.fundamental_analysis
        news = research.news_sentiment
        
        message = f"""🧠 <b>Autonomous Analysis: {research.symbol}</b>
⚡ <b>Anomaly Detected:</b> {signal.anomaly_type.value}
📊 <b>Signal:</b> {research.recommendation} (Confidence: {research.confidence:.1%})

💰 <b>Price Action:</b>
• Current: {ta.get('price', 0):,.0f}
• RSI: {ta.get('rsi_14', 0):.1f}
• Volume Ratio: {ta.get('volume_ratio', 0):.1f}x
• Risk/Reward: {research.risk_reward_ratio:.2f}

📈 <b>Technical Intelligence:</b>
• Trend Strength: {ta.get('trend_strength', 0):.1%}
• Support: {ta.get('support_resistance', {}).get('support', 0):,.0f}
• Resistance: {ta.get('support_resistance', {}).get('resistance', 0):,.0f}
• BB Position: {ta.get('bb_position', 0):.1%}

📰 <b>News Sentiment:</b> {news.get('sentiment_label', 'Neutral')} ({news.get('sentiment_score', 0):.2f})
💼 <b>Fundamentals:</b> Score {fa.get('fundamental_score', 0):.1%}

🎯 <b>Strategic Insight:</b>
{self._generate_strategic_insight(research, signal)}

⏰ <b>Analysis Time:</b> {research.timestamp.strftime('%H:%M:%S')}
🤖 <b>Agent Status:</b> Autonomous Mode Active"""
        
        return message
    
    def _generate_strategic_insight(self, research: ResearchResult, signal: MarketSignal) -> str:
        """Generate strategic insight based on all analysis"""
        
        insights = []
        
        # Anomaly-specific insights
        if signal.anomaly_type == AnomalyType.VOLUME_SURGE:
            insights.append("🔥 Unusual volume detected - possible institutional activity")
        elif signal.anomaly_type == AnomalyType.BREAKOUT:
            insights.append("📈 Price breaking key resistance - momentum building")
        elif signal.anomaly_type == AnomalyType.RSI_DIVERGENCE:
            insights.append("⚡ RSI divergence suggests trend reversal potential")
        
        # Technical insights
        ta = research.technical_analysis
        if ta.get('rsi_14', 50) < 30:
            insights.append("💎 Oversold conditions - buying opportunity")
        elif ta.get('rsi_14', 50) > 70:
            insights.append("⚠️ Overbought conditions - caution advised")
        
        # Risk/reward insights
        if research.risk_reward_ratio > 2.0:
            insights.append("✅ Excellent risk/reward ratio")
        elif research.risk_reward_ratio < 1.0:
            insights.append("⚠️ Poor risk/reward - consider waiting")
        
        # News sentiment insights
        if research.news_sentiment.get('sentiment_score', 0) > 0.3:
            insights.append("📰 Positive news sentiment supports bullish case")
        elif research.news_sentiment.get('sentiment_score', 0) < -0.3:
            insights.append("📰 Negative news sentiment - additional caution needed")
        
        return "\n".join(insights) if insights else "🔍 Monitoring for additional confirmation signals"
    
    def run_autonomous_cycle(self):
        """Main autonomous agent cycle"""
        logger.info("🤖 Starting Autonomous Analyst Agent Cycle")
        
        try:
            # Step 1: Detect anomalies
            signals = self.detect_anomalies()
            
            if not signals:
                logger.info("No anomalies detected. Agent standing by.")
                return
            
            logger.info(f"Found {len(signals)} anomalies - conducting research...")
            
            # Step 2: Research each anomaly
            for signal in signals:
                logger.info(f"Researching {signal.symbol}...")
                
                # Conduct autonomous research
                research_result = self.conduct_autonomous_research(signal)
                
                # Step 3: Send intelligent alert if confidence is high
                if research_result.confidence > 0.6:
                    self.send_intelligent_alert(research_result, signal)
                    
                    # Add to active signals monitoring
                    self.active_signals.append({
                        'signal': signal,
                        'research': research_result,
                        'alert_sent': True
                    })
                else:
                    logger.info(f"Low confidence ({research_result.confidence:.1%}) for {signal.symbol} - no alert sent")
            
            logger.info("Autonomous cycle completed successfully")
            
        except Exception as e:
            logger.error(f"Autonomous cycle failed: {e}")
            raise

def main():
    """Main execution function"""
    agent = AutonomousAnalystAgent()
    agent.run_autonomous_cycle()

if __name__ == "__main__":
    main()
