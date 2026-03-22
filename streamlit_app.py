"""
Streamlit Dashboard for Autonomous IDX Analyst Agent
Real-time monitoring and visualization of agent activities
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import json
import os

# Page configuration
st.set_page_config(
    page_title="🤖 Autonomous IDX Analyst",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .status-active {
        color: #00cc00;
        font-weight: bold;
    }
    .status-inactive {
        color: #ff6b6b;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">🤖 Autonomous IDX Analyst Dashboard</div>', unsafe_allow_html=True)

# Sidebar
st.sidebar.markdown("## 🎛️ Agent Control Panel")

# Mock data for demonstration (replace with real agent data)
def get_mock_agent_status():
    return {
        'status': 'Active',
        'last_run': datetime.now() - timedelta(minutes=15),
        'anomalies_detected': 3,
        'alerts_sent': 2,
        'confidence_avg': 0.78,
        'uptime': '99.2%'
    }

def get_mock_signals():
    return [
        {
            'symbol': 'BBCA',
            'signal': 'BUY',
            'confidence': 0.85,
            'anomaly_type': 'VOLUME_SURGE',
            'price': 8750,
            'rsi': 28.5,
            'volume_ratio': 4.2,
            'risk_reward': 2.8,
            'timestamp': datetime.now() - timedelta(minutes=45)
        },
        {
            'symbol': 'TLKM',
            'signal': 'BUY',
            'confidence': 0.72,
            'anomaly_type': 'RSI_DIVERGENCE',
            'price': 3250,
            'rsi': 32.1,
            'volume_ratio': 1.8,
            'risk_reward': 2.1,
            'timestamp': datetime.now() - timedelta(hours=2)
        },
        {
            'symbol': 'ASII',
            'signal': 'HOLD',
            'confidence': 0.45,
            'anomaly_type': 'PRICE_SPIKE',
            'price': 6200,
            'rsi': 65.3,
            'volume_ratio': 2.1,
            'risk_reward': 1.2,
            'timestamp': datetime.now() - timedelta(hours=3)
        }
    ]

def get_mock_performance_data():
    dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
    return pd.DataFrame({
        'date': dates,
        'anomalies_detected': [3, 5, 2, 8, 4, 6, 3, 7, 5, 4, 6, 8, 5, 3, 6, 4, 7, 5, 6, 4, 3, 5, 6, 4, 7, 5, 4, 6, 3, 5],
        'alerts_sent': [2, 3, 1, 5, 2, 4, 2, 4, 3, 2, 4, 5, 3, 2, 4, 2, 4, 3, 4, 2, 1, 3, 4, 2, 4, 3, 2, 4, 1, 3],
        'avg_confidence': [0.75, 0.78, 0.72, 0.82, 0.76, 0.79, 0.74, 0.81, 0.77, 0.75, 0.78, 0.83, 0.76, 0.74, 0.79, 0.75, 0.80, 0.77, 0.78, 0.75, 0.73, 0.77, 0.78, 0.75, 0.80, 0.77, 0.75, 0.78, 0.72, 0.77]
    })

# Agent Status
agent_status = get_mock_agent_status()

# Main dashboard
col1, col2, col3, col4 = st.columns(4)

with col1:
    status_class = "status-active" if agent_status['status'] == 'Active' else "status-inactive"
    st.markdown(f"""
    <div class="metric-card">
        <h4>Agent Status</h4>
        <p class="{status_class}">{agent_status['status']}</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <h4>Last Run</h4>
        <p>{agent_status['last_run'].strftime('%H:%M:%S')}</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <h4>Anomalies Today</h4>
        <p>{agent_status['anomalies_detected']}</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <h4>Avg Confidence</h4>
        <p>{agent_status['confidence_avg']:.1%}</p>
    </div>
    """, unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 Active Signals", "📈 Performance", "🧠 Research Insights", "⚙️ Configuration"])

with tab1:
    st.markdown("## 🚨 Current Active Signals")
    
    signals = get_mock_signals()
    
    if signals:
        for signal in signals:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                signal_color = "🟢" if signal['signal'] == 'BUY' else "🟡" if signal['signal'] == 'HOLD' else "🔴"
                
                st.markdown(f"""
                <div style="border: 1px solid #ddd; padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem;">
                    <h3>{signal_color} <strong>{signal['symbol']}</strong> - {signal['signal']} (Confidence: {signal['confidence']:.1%})</h3>
                    <p><strong>Anomaly:</strong> {signal['anomaly_type']}</p>
                    <p><strong>Price:</strong> {signal['price']:,.0f} | <strong>RSI:</strong> {signal['rsi']:.1f} | <strong>Volume:</strong> {signal['volume_ratio']:.1f}x</p>
                    <p><strong>Risk/Reward:</strong> {signal['risk_reward']:.2f} | <strong>Detected:</strong> {signal['timestamp'].strftime('%H:%M')}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                # Mini chart
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=[1, 2, 3, 4, 5],
                    y=[signal['price'] * 0.98, signal['price'] * 0.99, signal['price'], signal['price'] * 1.01, signal['price'] * 1.02],
                    mode='lines+markers',
                    line=dict(color='green' if signal['signal'] == 'BUY' else 'orange' if signal['signal'] == 'HOLD' else 'red')
                ))
                fig.update_layout(
                    height=150,
                    showlegend=False,
                    margin=dict(l=0, r=0, t=0, b=0),
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
                )
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No active signals detected. Agent is monitoring...")

with tab2:
    st.markdown("## 📈 Agent Performance Analytics")
    
    perf_data = get_mock_performance_data()
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=perf_data['date'],
            y=perf_data['anomalies_detected'],
            mode='lines+markers',
            name='Anomalies Detected',
            line=dict(color='#1f77b4')
        ))
        fig.add_trace(go.Scatter(
            x=perf_data['date'],
            y=perf_data['alerts_sent'],
            mode='lines+markers',
            name='Alerts Sent',
            line=dict(color='#ff7f0e')
        ))
        fig.update_layout(
            title='Detection Performance Over Time',
            xaxis_title='Date',
            yaxis_title='Count',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=perf_data['date'],
            y=perf_data['avg_confidence'],
            mode='lines+markers',
            name='Average Confidence',
            line=dict(color='#2ca02c')
        ))
        fig.update_layout(
            title='Average Confidence Score',
            xaxis_title='Date',
            yaxis_title='Confidence',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Performance metrics
    st.markdown("### 📊 Performance Summary")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_anomalies = perf_data['anomalies_detected'].sum()
        st.metric("Total Anomalies", total_anomalies)
    
    with col2:
        total_alerts = perf_data['alerts_sent'].sum()
        st.metric("Total Alerts", total_alerts)
    
    with col3:
        avg_conf = perf_data['avg_confidence'].mean()
        st.metric("Avg Confidence", f"{avg_conf:.1%}")
    
    with col4:
        alert_rate = total_alerts / total_anomalies if total_anomalies > 0 else 0
        st.metric("Alert Rate", f"{alert_rate:.1%}")

with tab3:
    st.markdown("## 🧠 Research Intelligence")
    
    st.markdown("### 🔬 Recent Research Analysis")
    
    # Mock research insights
    research_insights = [
        {
            'symbol': 'BBCA',
            'research_time': datetime.now() - timedelta(minutes=30),
            'technical_score': 0.85,
            'fundamental_score': 0.78,
            'sentiment_score': 0.65,
            'final_recommendation': 'BUY',
            'key_insights': [
                'Volume surge suggests institutional accumulation',
                'RSI divergence indicates bullish momentum',
                'Strong support at 8,500 level'
            ]
        },
        {
            'symbol': 'TLKM',
            'research_time': datetime.now() - timedelta(hours=2),
            'technical_score': 0.72,
            'fundamental_score': 0.80,
            'sentiment_score': 0.45,
            'final_recommendation': 'HOLD',
            'key_insights': [
                'Mixed technical signals',
                'Strong fundamentals support long-term value',
                'Neutral sentiment from recent news'
            ]
        }
    ]
    
    for research in research_insights:
        with st.expander(f"📋 {research['symbol']} - {research['final_recommendation']} ({research['research_time'].strftime('%H:%M')})"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Technical Score", f"{research['technical_score']:.1%}")
            
            with col2:
                st.metric("Fundamental Score", f"{research['fundamental_score']:.1%}")
            
            with col3:
                st.metric("Sentiment Score", f"{research['sentiment_score']:.1%}")
            
            st.markdown("**Key Insights:**")
            for insight in research['key_insights']:
                st.markdown(f"• {insight}")

with tab4:
    st.markdown("## ⚙️ Agent Configuration")
    
    st.markdown("### 🎛️ Current Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Detection Parameters**")
        st.text("Volume Threshold: 3.0x")
        st.text("Price Spike: 5.0%")
        st.text("RSI Oversold: 30")
        st.text("RSI Overbought: 70")
        st.text("Min Confidence: 60%")
    
    with col2:
        st.markdown("**Operational Settings**")
        st.text("Market Hours: 09:00-16:00 WIB")
        st.text("Scan Frequency: 30 min")
        st.text("Cache Duration: 1 hour")
        st.text("Max Alerts/Hour: 10")
        st.text("Cooldown: 15 min")
    
    st.markdown("### 📊 Agent Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Uptime", agent_status['uptime'])
    
    with col2:
        st.metric("Stocks Monitored", "100")
    
    with col3:
        st.metric("Research Cache", "12 items")
    
    with col4:
        st.metric("Error Rate", "0.2%")

# Sidebar controls
st.sidebar.markdown("---")
st.sidebar.markdown("### 🎯 Quick Actions")

if st.sidebar.button("🔄 Force Scan Now"):
    st.sidebar.success("Manual scan initiated!")
    # In real implementation, this would trigger the agent

if st.sidebar.button("📊 Generate Report"):
    st.sidebar.info("Generating comprehensive report...")

if st.sidebar.button("🔧 Test Alert"):
    st.sidebar.info("Test alert sent to Telegram!")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>"
    "🤖 Autonomous IDX Analyst Agent - Real-time Market Intelligence"
    "</div>",
    unsafe_allow_html=True
)
