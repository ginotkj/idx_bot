# 🤖 Autonomous IDX Analyst Agent

Transform your market analysis from simple reporting to intelligent, autonomous decision-making.

## 🚀 What This Agent Does

**After**: An autonomous analyst that detects anomalies, conducts multi-step research, and provides strategic recommendations without human intervention

### Key Features

- **🔍 Anomaly Detection**: Automatically scans 100+ IDX stocks for unusual patterns
- **🧠 Intelligent Research**: Conducts 30-minute research cycles including:
  - Deep technical analysis across multiple timeframes
  - News sentiment analysis
  - Fundamental analysis
  - Risk/reward calculations
- **📊 Strategic Recommendations**: Generates actionable insights with confidence scores
- **⚡ Real-time Alerts**: Sends intelligent alerts only when high-confidence opportunities arise
- **🔄 Continuous Learning**: Caches research results and learns from market patterns

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Anomaly       │    │   Multi-Step     │    │   Strategic     │
│   Detection     │───▶│   Research       │───▶│   Intelligence  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Volume Spikes   │    │ Technical        │    │ Risk/Reward     │
│ Price Movements │    │ Fundamental      │    │ Decision Logic  │
│ RSI Divergence  │    │ News Sentiment   │    │ Confidence      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 📋 Anomaly Types Detected

1. **Volume Surge** - Unusual trading volume (3x+ average)
2. **Price Spike** - Significant price movements (5%+)
3. **RSI Divergence** - Price/RSI divergence signals
4. **Breakout** - Price breaking key resistance levels
5. **News-Driven** - Sentiment-based opportunities

## 🛠️ Setup Instructions

### 1. Environment Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd autonomous-idx-agent

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your credentials
TELEGRAM_TOKEN=your_bot_token
CHAT_ID=your_chat_id
NEWS_API_KEY=your_news_api_key  # Optional
```

### 3. GitHub Secrets Setup

In your GitHub repository, go to Settings → Secrets and add:
- `TELEGRAM_TOKEN`: Your Telegram bot token
- `CHAT_ID`: Your Telegram chat ID
- `NEWS_API_KEY`: News API key (optional)

### 4. Deploy to GitHub Actions

Push your code to GitHub, and the agent will automatically:
- Run every 30 minutes during market hours (9:00 AM - 4:00 PM WIB)
- Run every hour outside market hours
- Send intelligent alerts when opportunities are detected

## 📊 How It Works

### Step 1: Anomaly Detection
The agent continuously scans 100 top IDX stocks for:
- Volume anomalies (3x+ normal volume)
- Price spikes (5%+ movements)
- Technical divergences
- Breakout patterns

### Step 2: Autonomous Research
When an anomaly is detected, the agent automatically:
1. **Technical Analysis**: Multi-timeframe analysis with 15+ indicators
2. **News Sentiment**: Scans news sources for market sentiment
3. **Fundamentals**: Analyzes financial health and valuation
4. **Risk/Reward**: Calculates optimal entry/exit points

### Step 3: Strategic Intelligence
The agent synthesizes all data to provide:
- **Recommendation**: BUY/SELL/HOLD with confidence score
- **Risk/Reward**: Quantified opportunity assessment
- **Strategic Insight**: Contextual market intelligence
- **Actionable Intelligence**: Clear next steps

## 📱 Sample Alert Output

```
🧠 Autonomous Analysis: BBCA
⚡ Anomaly Detected: VOLUME_SURGE
📊 Signal: BUY (Confidence: 78%)

💰 Price Action:
• Current: 8,750
• RSI: 28.5
• Volume Ratio: 4.2x
• Risk/Reward: 2.8

📈 Technical Intelligence:
• Trend Strength: 85%
• Support: 8,500
• Resistance: 9,200
• BB Position: 15%

📰 News Sentiment: Positive (0.45)
💼 Fundamentals: Score 75%

🎯 Strategic Insight:
🔥 Unusual volume detected - possible institutional activity
💎 Oversold conditions - buying opportunity
✅ Excellent risk/reward ratio

⏰ Analysis Time: 14:35:22
🤖 Agent Status: Autonomous Mode Active
```

## 🔧 Configuration

### Agent Behavior
Edit `config.yaml` to customize:
- Anomaly detection thresholds
- Technical indicator parameters
- Alert frequency limits
- Research cache duration

### Market Hours
The agent automatically adjusts frequency:
- **Market Hours**: Every 30 minutes (9:00 AM - 4:00 PM WIB)
- **After Hours**: Every hour
- **Weekends**: Reduced frequency

## 📈 Performance Monitoring

The agent tracks:
- Anomaly detection accuracy
- Alert success rate
- Research completion time
- Signal performance over time

Logs are automatically archived and available in GitHub Actions artifacts.

## 🚀 Advanced Features

### Research Caching
- Caches research results for 1 hour
- Avoids duplicate analysis
- Improves response time

### Confidence Scoring
- Multi-factor confidence calculation
- Weighted signal analysis
- Adjustable thresholds

### Risk Management
- Automatic risk/reward calculation
- Position sizing suggestions
- Stop-loss recommendations

## 🛡️ Safety Features

- **Rate Limiting**: Prevents alert spam
- **Confidence Thresholds**: Only high-confidence signals
- **Error Handling**: Robust error recovery
- **Logging**: Comprehensive activity tracking

## 📞 Support

This agent transforms market monitoring from passive reporting to active intelligence. By the time you check your phone, the agent has already:
- ✅ Scanned 100+ stocks for anomalies
- ✅ Conducted comprehensive research
- ✅ Analyzed news sentiment
- ✅ Calculated risk/reward ratios
- ✅ Generated strategic recommendations

**No more manual analysis - just actionable intelligence delivered to your phone.**

---

## 🔄 Migration from Simple Script

To upgrade from your existing script:
1. Replace your current script with `autonomous_agent.py`
2. Add the new configuration files
3. Update your GitHub Actions workflow
4. Add the new secrets to GitHub

The agent maintains backward compatibility while adding powerful autonomous capabilities.
