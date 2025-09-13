import streamlit as st
import pandas as pd
import numpy as np
import time
from datetime import datetime
import threading
import queue
import io
import base64
import tempfile
import os
import sys
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px
from collections import deque, Counter

# Add the necessary paths for imports
current_dir = Path(__file__).parent
components_path = current_dir / "components"
sys.path.append(str(components_path))

# Import custom components
try:
    from audio_monitor import render_audio_component, get_audio_processor
    from screen_monitor import render_screen_component, get_screen_processor, render_context_insights, get_productivity_score
    COMPONENTS_AVAILABLE = True
except ImportError as e:
    st.warning(f"Some components not available: {e}")
    COMPONENTS_AVAILABLE = False

# Check if running in cloud environment
CLOUD_MODE = hasattr(st, 'secrets') and st.secrets.get('CLOUD_DEPLOYMENT', False)

# Set page config
st.set_page_config(
    page_title="Real-time Engagement Monitor",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .engagement-engaged {
        color: #28a745;
        font-weight: bold;
        font-size: 1.2rem;
    }
    .engagement-distracted {
        color: #dc3545;
        font-weight: bold;
        font-size: 1.2rem;
    }
    .status-running {
        color: #28a745;
    }
    .status-stopped {
        color: #dc3545;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Main Streamlit application"""
    
    # Title and description
    st.markdown('<h1 class="main-header">🎯 Real-time Engagement Monitor</h1>', unsafe_allow_html=True)
    
    if CLOUD_MODE:
        st.info("🌐 **Cloud Demo Mode** - Running with simulated data for demonstration")
    
    st.markdown("""
    ### A comprehensive engagement monitoring system that combines:
    - 🎤 **Audio Emotion Detection** - Real-time analysis of emotional state through voice
    - 🖥️ **Screen Activity Analysis** - Context detection, sentiment analysis, and productivity monitoring
    - 📊 **Live Dashboard** - Real-time visualization of engagement metrics
    """)
    
    if CLOUD_MODE:
        st.markdown("""
        **Note:** This cloud version uses simulated data for demonstration. 
        For full functionality with real audio and screen capture, please run locally.
        """)
    
    # Check if components are available
    if not COMPONENTS_AVAILABLE:
        st.error("Required components are not available. Please check the installation.")
        return
    
    # Sidebar for controls
    with st.sidebar:
        st.header("🔧 Controls")
        
        # Monitoring toggles
        st.subheader("📊 Monitoring")
        audio_enabled = st.checkbox("🎤 Audio Emotion Detection", value=True)
        screen_enabled = st.checkbox("🖥️ Screen Analysis", value=True)
        
        # Settings
        st.subheader("⚙️ Settings")
        update_interval = st.slider("Update Interval (seconds)", 1, 10, 3)
        audio_window = st.slider("Audio Analysis Window (seconds)", 2, 5, 3)
        
        # Model settings
        st.subheader("🤖 Model Settings")
        confidence_threshold = st.slider("Confidence Threshold", 0.1, 1.0, 0.6)
        
        # Data retention
        max_data_points = st.slider("Max Data Points", 50, 500, 100)
        
        # Export data
        st.subheader("💾 Data Export")
        if st.button("📥 Export Session Data", use_container_width=True):
            if 'session_data' in st.session_state and st.session_state.session_data:
                df = pd.DataFrame(st.session_state.session_data)
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"engagement_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            else:
                st.warning("No data to export")
    
    # Initialize session state
    if 'monitoring_active' not in st.session_state:
        st.session_state.monitoring_active = False
    if 'session_data' not in st.session_state:
        st.session_state.session_data = deque(maxlen=max_data_points)
    if 'current_emotion' not in st.session_state:
        st.session_state.current_emotion = "Unknown"
    if 'current_engagement' not in st.session_state:
        st.session_state.current_engagement = "Unknown"
    if 'current_context' not in st.session_state:
        st.session_state.current_context = "Unknown"
    if 'current_sentiment' not in st.session_state:
        st.session_state.current_sentiment = "Neutral"
    if 'productivity_score' not in st.session_state:
        st.session_state.productivity_score = 0
    
    # Status indicator
    status_indicator = st.empty()
    
    # Create main layout
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "🎤 Audio Monitor", "🖥️ Screen Monitor", "📈 Analytics"])
    
    with tab1:
        # Real-time metrics dashboard
        st.subheader("� Real-time Metrics")
        
        # Main metrics row
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            engagement_color = "#28a745" if st.session_state.current_engagement == "Engaged" else "#dc3545"
            st.metric(
                "🎯 Engagement", 
                st.session_state.current_engagement,
                delta=None
            )
        
        with col2:
            st.metric("😊 Emotion", st.session_state.current_emotion)
        
        with col3:
            st.metric("📱 Context", st.session_state.current_context)
        
        with col4:
            st.metric("💭 Sentiment", st.session_state.current_sentiment)
        
        with col5:
            st.metric("� Productivity", f"{st.session_state.productivity_score}%")
        
        # Live charts
        if st.session_state.session_data:
            col1, col2 = st.columns(2)
            
            with col1:
                # Engagement over time
                df = pd.DataFrame(list(st.session_state.session_data))
                if 'timestamp' in df.columns and 'engagement' in df.columns:
                    df['time'] = pd.to_datetime(df['timestamp'], unit='s')
                    df['engaged_binary'] = df['engagement'].map({'Engaged': 1, 'Distracted': 0}).fillna(0)
                    
                    fig = px.line(df, x='time', y='engaged_binary', 
                                title='Engagement Over Time',
                                labels={'engaged_binary': 'Engaged (1) / Distracted (0)'})
                    fig.update_layout(height=300)
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Context distribution
                if 'context' in df.columns:
                    context_counts = df['context'].value_counts()
                    fig = px.pie(values=context_counts.values, names=context_counts.index,
                               title='Context Distribution')
                    fig.update_layout(height=300)
                    st.plotly_chart(fig, use_container_width=True)
        
        # Session summary
        st.subheader("� Session Summary")
        if st.session_state.session_data:
            total_time = len(st.session_state.session_data) * update_interval
            engaged_count = sum(1 for item in st.session_state.session_data 
                              if item.get('engagement') == 'Engaged')
            engagement_rate = (engaged_count / len(st.session_state.session_data)) * 100
            
            summary_col1, summary_col2, summary_col3 = st.columns(3)
            with summary_col1:
                st.metric("Total Session Time", f"{total_time//60:.0f}m {total_time%60:.0f}s")
            with summary_col2:
                st.metric("Engagement Rate", f"{engagement_rate:.1f}%")
            with summary_col3:
                st.metric("Data Points", len(st.session_state.session_data))
        else:
            st.info("Start monitoring to see session summary")
    
    with tab2:
        # Audio monitoring tab
        if audio_enabled:
            audio_processor = render_audio_component()
        else:
            st.info("Audio monitoring disabled in settings")
    
    with tab3:
        # Screen monitoring tab
        if screen_enabled:
            screen_processor = render_screen_component()
            render_context_insights()
        else:
            st.info("Screen monitoring disabled in settings")
    
    with tab4:
        # Analytics tab
        st.subheader("📈 Advanced Analytics")
        
        if st.session_state.session_data:
            df = pd.DataFrame(list(st.session_state.session_data))
            
            # Time-based analysis
            st.subheader("⏰ Time-based Analysis")
            if 'timestamp' in df.columns:
                df['time'] = pd.to_datetime(df['timestamp'], unit='s')
                df['hour'] = df['time'].dt.hour
                
                # Engagement by hour
                if 'engagement' in df.columns:
                    hourly_engagement = df.groupby('hour')['engagement'].apply(
                        lambda x: (x == 'Engaged').mean() * 100
                    ).reset_index()
                    
                    fig = px.bar(hourly_engagement, x='hour', y='engagement',
                               title='Engagement Rate by Hour',
                               labels={'engagement': 'Engagement Rate (%)'})
                    st.plotly_chart(fig, use_container_width=True)
            
            # Correlation analysis
            st.subheader("🔗 Pattern Analysis")
            if len(df) > 10:
                # Create correlation matrix for categorical variables
                patterns = {}
                
                if 'context' in df.columns and 'engagement' in df.columns:
                    context_engagement = pd.crosstab(df['context'], df['engagement'], normalize='index') * 100
                    st.write("**Context vs Engagement (%)**")
                    st.dataframe(context_engagement)
                
                if 'emotion' in df.columns and 'engagement' in df.columns:
                    emotion_engagement = pd.crosstab(df['emotion'], df['engagement'], normalize='index') * 100
                    st.write("**Emotion vs Engagement (%)**")
                    st.dataframe(emotion_engagement)
        else:
            st.info("No data available for analytics. Start monitoring to collect data.")
    
    # Update session data if monitoring is active
    if st.session_state.get('audio_active') or st.session_state.get('screen_active'):
        current_data = {
            'timestamp': time.time(),
            'emotion': st.session_state.current_emotion,
            'engagement': st.session_state.current_engagement,
            'context': st.session_state.current_context,
            'sentiment': st.session_state.current_sentiment
        }
        
        # Add to session data
        st.session_state.session_data.append(current_data)
        
        # Update productivity score
        st.session_state.productivity_score = get_productivity_score()
        
        # Show status
        status_indicator.success("🟢 Monitoring Active - Data being collected")
        
        # Auto-refresh
        time.sleep(update_interval)
        st.rerun()
    else:
        status_indicator.info("🔴 Monitoring Inactive - Start audio or screen monitoring")

if __name__ == "__main__":
    main()