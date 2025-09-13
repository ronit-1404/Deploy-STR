import streamlit as st
import cv2
import numpy as np
import time
import threading
import queue
from pathlib import Path
import sys
import os

# Add necessary paths
current_dir = Path(__file__).parent.parent
screen_path = current_dir / "screen-analyzer"
shared_path = screen_path / "shared"
windows_path = screen_path / "windows"

sys.path.extend([str(shared_path), str(windows_path)])

try:
    from win_capture import capture_screen
    from win_window import get_active_app
    from idle_tracker_win import get_idle_time
    from ocr import extract_text
    from context import detect_context
    from sentiment import analyze_sentiment
    from chrome_tab import get_chrome_tab_info
    SCREEN_ANALYSIS_AVAILABLE = True
except ImportError as e:
    st.warning(f"Screen analysis modules not available: {e}")
    SCREEN_ANALYSIS_AVAILABLE = False

class StreamlitScreenProcessor:
    """Screen processor adapted for Streamlit"""
    
    def __init__(self):
        self.is_monitoring = False
        self.analysis_thread = None
        self.analysis_queue = queue.Queue()
        self.update_interval = 5  # seconds
        
    def capture_and_analyze(self):
        """Capture screen and perform analysis"""
        try:
            if not SCREEN_ANALYSIS_AVAILABLE:
                return None
            
            # Get current app
            app = get_active_app()
            
            # Capture screen
            frame = capture_screen()
            if frame is None:
                return None
            
            # Extract text using OCR
            text = extract_text(frame)
            
            # Detect context
            context = detect_context(text)
            
            # Analyze sentiment
            sentiment = analyze_sentiment(text)
            
            # Get idle time
            idle_seconds = get_idle_time()
            
            # Get Chrome tab info if applicable
            title, url = None, None
            if "chrome" in app.lower():
                try:
                    title, url = get_chrome_tab_info()
                except:
                    pass
            
            return {
                'timestamp': time.time(),
                'active_app': app,
                'text_content': text[:500] if text else "",  # Limit text length
                'context': context,
                'sentiment': sentiment,
                'idle_seconds': idle_seconds,
                'chrome_title': title,
                'chrome_url': url,
                'text_length': len(text) if text else 0
            }
            
        except Exception as e:
            st.error(f"Screen analysis error: {str(e)}")
            return None
    
    def monitoring_loop(self):
        """Background monitoring loop"""
        while self.is_monitoring:
            try:
                analysis = self.capture_and_analyze()
                if analysis:
                    self.analysis_queue.put(analysis)
                
                time.sleep(self.update_interval)
                
            except Exception as e:
                print(f"Monitoring loop error: {e}")
                time.sleep(1)
    
    def start_monitoring(self, interval=5):
        """Start screen monitoring"""
        if not SCREEN_ANALYSIS_AVAILABLE:
            st.error("Screen analysis modules not available")
            return False
        
        try:
            self.update_interval = interval
            self.is_monitoring = True
            
            self.analysis_thread = threading.Thread(target=self.monitoring_loop, daemon=True)
            self.analysis_thread.start()
            
            return True
            
        except Exception as e:
            st.error(f"Error starting screen monitoring: {str(e)}")
            return False
    
    def stop_monitoring(self):
        """Stop screen monitoring"""
        self.is_monitoring = False
        if self.analysis_thread:
            self.analysis_thread.join(timeout=2)
    
    def get_latest_analysis(self):
        """Get the latest screen analysis"""
        try:
            if not self.analysis_queue.empty():
                return self.analysis_queue.get_nowait()
            return None
        except queue.Empty:
            return None
        except Exception as e:
            st.error(f"Error getting analysis: {str(e)}")
            return None

@st.cache_resource
def get_screen_processor():
    """Get cached screen processor instance"""
    return StreamlitScreenProcessor()

def render_screen_component():
    """Render the screen monitoring component"""
    if not SCREEN_ANALYSIS_AVAILABLE:
        st.error("Screen analysis not available. Please check dependencies.")
        return None
    
    processor = get_screen_processor()
    
    # Screen monitoring status
    if 'screen_active' not in st.session_state:
        st.session_state.screen_active = False
    
    # Screen controls
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🖥️ Start Screen", disabled=st.session_state.screen_active):
            if processor.start_monitoring():
                st.session_state.screen_active = True
                st.success("Screen monitoring started!")
            else:
                st.error("Failed to start screen monitoring")
    
    with col2:
        if st.button("⏹️ Stop Screen", disabled=not st.session_state.screen_active):
            processor.stop_monitoring()
            st.session_state.screen_active = False
            st.info("Screen monitoring stopped")
    
    # Display screen status
    if st.session_state.screen_active:
        st.success("🟢 Screen monitoring active")
        
        # Get latest analysis
        analysis = processor.get_latest_analysis()
        if analysis:
            # Update session state
            st.session_state.current_context = analysis['context']
            st.session_state.current_sentiment = analysis['sentiment']
            
            # Display current analysis
            st.subheader("📊 Current Screen Analysis")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Active App", analysis['active_app'])
                st.metric("Context", analysis['context'])
                st.metric("Sentiment", analysis['sentiment'])
            
            with col2:
                st.metric("Idle Time (s)", analysis['idle_seconds'])
                st.metric("Text Length", analysis['text_length'])
                
                if analysis['chrome_title']:
                    st.metric("Chrome Tab", analysis['chrome_title'][:30] + "..." if len(analysis['chrome_title']) > 30 else analysis['chrome_title'])
            
            # Show recent text content (if any)
            if analysis['text_content']:
                with st.expander("📝 Recent Text Content"):
                    st.text_area("Detected Text", analysis['text_content'], height=100)
    else:
        st.info("🔴 Screen monitoring inactive")
    
    return processor if st.session_state.screen_active else None

def render_context_insights():
    """Render context-based insights"""
    if 'session_data' not in st.session_state:
        st.session_state.session_data = []
    
    st.subheader("🧠 Context Insights")
    
    # Analyze session data for patterns
    if st.session_state.session_data:
        contexts = [item.get('context', 'Unknown') for item in st.session_state.session_data]
        sentiments = [item.get('sentiment', 'Neutral') for item in st.session_state.session_data]
        
        # Context distribution
        from collections import Counter
        context_counts = Counter(contexts)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Context Distribution:**")
            for context, count in context_counts.most_common(5):
                st.write(f"- {context}: {count}")
        
        with col2:
            st.write("**Recent Activity:**")
            recent_items = list(st.session_state.session_data)[-5:]
            for item in recent_items:
                timestamp = item.get('timestamp', time.time())
                context = item.get('context', 'Unknown')
                st.write(f"- {time.strftime('%H:%M:%S', time.localtime(timestamp))}: {context}")
    else:
        st.info("No session data available yet. Start monitoring to see insights.")

def get_productivity_score():
    """Calculate a simple productivity score based on context and engagement"""
    if 'session_data' not in st.session_state or not st.session_state.session_data:
        return 0
    
    # Define productive contexts
    productive_contexts = ['programming', 'reading', 'writing', 'learning']
    engaged_states = ['Engaged']
    
    recent_data = list(st.session_state.session_data)[-10:]  # Last 10 data points
    
    productivity_points = 0
    total_points = len(recent_data)
    
    for item in recent_data:
        context = item.get('context', '').lower()
        engagement = item.get('engagement', '')
        
        if any(prod_context in context for prod_context in productive_contexts):
            productivity_points += 0.7
        
        if engagement in engaged_states:
            productivity_points += 0.3
    
    return min(100, int((productivity_points / total_points) * 100)) if total_points > 0 else 0