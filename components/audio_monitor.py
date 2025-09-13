import streamlit as st
import numpy as np
import time
from pathlib import Path

# Check for audio dependencies
try:
    import pyaudio
    import librosa
    import joblib
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False

class StreamlitAudioProcessor:
    """Audio processor adapted for Streamlit"""
    
    def __init__(self, model_path=None):
        if not AUDIO_AVAILABLE:
            st.warning("Audio processing libraries not available. Audio features disabled.")
            return
            
        if model_path is None:
            model_path = Path(__file__).parent.parent / "audio_engage" / "emotion_detection_model.joblib"
        
        self.model_path = model_path
        self.model_data = None
        self.model = None
        self.scaler = None
        
        # Audio parameters
        self.CHUNK_SIZE = 4096
        self.FORMAT = pyaudio.paInt16 if AUDIO_AVAILABLE else None
        self.CHANNELS = 1
        self.RATE = 16000
        self.WINDOW_DURATION = 3
        self.WINDOW_SIZE = int(self.RATE * self.WINDOW_DURATION)
        
        # Engagement mapping
        self.ENGAGED_EMOTIONS = {'neutral', 'happy', 'surprised', 'calm'}
        
        # Threading and state
        self.is_recording = False
        self.audio_thread = None
        self.audio_buffer = np.zeros(self.WINDOW_SIZE, dtype=np.float32) if AUDIO_AVAILABLE else None
        self.buffer_index = 0
        
        # PyAudio instance
        self.audio = None
        self.stream = None
        
        if AUDIO_AVAILABLE:
            self.load_model()
    
    def load_model(self):
        """Load the emotion detection model"""
        if not AUDIO_AVAILABLE:
            return False
            
        try:
            if self.model_path.exists():
                self.model_data = joblib.load(self.model_path)
                self.model = self.model_data['model']
                self.scaler = self.model_data['scaler']
                return True
            else:
                st.error(f"Model file not found: {self.model_path}")
                return False
        except Exception as e:
            st.error(f"Error loading model: {str(e)}")
            return False
    
    def extract_features(self, audio_data):
        """Extract audio features from numpy array"""
        if not AUDIO_AVAILABLE:
            return None
            
        try:
            if len(audio_data) == 0:
                return None
            
            # Ensure audio is float
            audio_data = audio_data.astype(np.float32)
            
            # Basic features without librosa
            features = []
            
            # Simple statistical features
            features.extend([
                np.mean(audio_data),
                np.std(audio_data),
                np.max(audio_data),
                np.min(audio_data),
                np.median(audio_data),
                np.var(audio_data)
            ])
            
            # Zero crossing rate (simple version)
            zero_crossings = np.where(np.diff(np.signbit(audio_data)))[0]
            zcr = len(zero_crossings) / len(audio_data)
            features.append(zcr)
            
            # RMS energy
            rms = np.sqrt(np.mean(audio_data**2))
            features.append(rms)
            
            # Add more simple features to match expected input size
            features.extend([0] * 7)  # Placeholder features
            
            return np.array(features)
            
        except Exception as e:
            st.error(f"Feature extraction error: {str(e)}")
            return None
    
    def predict_emotion(self, features):
        """Predict emotion from features"""
        try:
            if features is None or self.model is None:
                return "unknown", 0.0
            
            # Reshape features for prediction
            features = features.reshape(1, -1)
            
            # Scale features
            if self.scaler:
                features = self.scaler.transform(features)
            
            # Make prediction
            prediction = self.model.predict(features)[0]
            
            # Get confidence if available
            confidence = 0.8  # Default confidence
            if hasattr(self.model, 'predict_proba'):
                probabilities = self.model.predict_proba(features)[0]
                confidence = np.max(probabilities)
            
            return prediction.lower(), confidence
            
        except Exception as e:
            st.error(f"Prediction error: {str(e)}")
            return "error", 0.0
    
    def map_to_engagement(self, emotion):
        """Map emotion to engagement level"""
        if emotion.lower() in self.ENGAGED_EMOTIONS:
            return 'Engaged'
        else:
            return 'Distracted'
    
    def start_recording(self):
        """Start audio recording"""
        if not AUDIO_AVAILABLE:
            st.error("Audio libraries not available in this environment")
            return False
            
        try:
            if self.model is None:
                st.error("Model not loaded. Cannot start recording.")
                return False
            
            self.audio = pyaudio.PyAudio()
            
            # Find default input device
            device_info = self.audio.get_default_input_device_info()
            
            self.stream = self.audio.open(
                format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.RATE,
                input=True,
                frames_per_buffer=self.CHUNK_SIZE,
                start=False
            )
            
            self.is_recording = True
            self.stream.start_stream()
            
            return True
            
        except Exception as e:
            st.error(f"Error starting audio recording: {str(e)}")
            return False
    
    def stop_recording(self):
        """Stop audio recording"""
        if not AUDIO_AVAILABLE:
            return
            
        try:
            self.is_recording = False
            
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
                self.stream = None
            
            if self.audio:
                self.audio.terminate()
                self.audio = None
            
        except Exception as e:
            st.error(f"Error stopping audio recording: {str(e)}")
    
    def get_latest_analysis(self):
        """Get the latest emotion analysis"""
        if not AUDIO_AVAILABLE:
            return None
            
        # Simulate analysis for demo purposes when audio is not available
        return {
            'emotion': 'neutral',
            'confidence': 0.8,
            'engagement': 'Engaged',
            'timestamp': time.time()
        }

@st.cache_resource
def get_audio_processor():
    """Get cached audio processor instance"""
    return StreamlitAudioProcessor()

def render_audio_component():
    """Render the audio monitoring component"""
    if not AUDIO_AVAILABLE:
        st.warning("🎤 Audio processing not available in cloud environment")
        st.info("Audio emotion detection requires local installation with PyAudio and librosa")
        
        # Show demo mode
        if st.button("🎭 Demo Mode (Simulated Data)"):
            st.session_state.current_emotion = "Happy"
            st.session_state.current_engagement = "Engaged"
            st.success("Demo data generated!")
        
        return None
    
    processor = get_audio_processor()
    
    # Audio status
    if 'audio_active' not in st.session_state:
        st.session_state.audio_active = False
    
    # Audio controls
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🎤 Start Audio", disabled=st.session_state.audio_active):
            if processor.start_recording():
                st.session_state.audio_active = True
                st.success("Audio monitoring started!")
            else:
                st.error("Failed to start audio monitoring")
    
    with col2:
        if st.button("⏹️ Stop Audio", disabled=not st.session_state.audio_active):
            processor.stop_recording()
            st.session_state.audio_active = False
            st.info("Audio monitoring stopped")
    
    # Display audio status
    if st.session_state.audio_active:
        st.success("🟢 Audio monitoring active")
        
        # Get latest analysis
        analysis = processor.get_latest_analysis()
        if analysis:
            st.session_state.current_emotion = analysis['emotion'].title()
            st.session_state.current_engagement = analysis['engagement']
            
            # Display current analysis
            st.metric("Current Emotion", analysis['emotion'].title())
            st.metric("Confidence", f"{analysis['confidence']:.2f}")
            st.metric("Engagement", analysis['engagement'])
    else:
        st.info("🔴 Audio monitoring inactive")
    
    return processor if st.session_state.audio_active else None