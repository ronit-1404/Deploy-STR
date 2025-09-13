import streamlit as st
import pyaudio
import numpy as np
import threading
import queue
import time
import joblib
import librosa
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

class StreamlitAudioProcessor:
    """Audio processor adapted for Streamlit"""
    
    def __init__(self, model_path=None):
        if model_path is None:
            model_path = Path(__file__).parent / "audio_engage" / "emotion_detection_model.joblib"
        
        self.model_path = model_path
        self.model_data = None
        self.model = None
        self.scaler = None
        
        # Audio parameters
        self.CHUNK_SIZE = 4096
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 16000
        self.WINDOW_DURATION = 3
        self.WINDOW_SIZE = int(self.RATE * self.WINDOW_DURATION)
        
        # Engagement mapping
        self.ENGAGED_EMOTIONS = {'neutral', 'happy', 'surprised', 'calm'}
        
        # Threading and state
        self.is_recording = False
        self.audio_thread = None
        self.audio_queue = queue.Queue()
        self.audio_buffer = np.zeros(self.WINDOW_SIZE, dtype=np.float32)
        self.buffer_index = 0
        
        # PyAudio instance
        self.audio = None
        self.stream = None
        
        self.load_model()
    
    def load_model(self):
        """Load the emotion detection model"""
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
        try:
            if len(audio_data) == 0:
                return None
            
            # Ensure audio is float
            audio_data = audio_data.astype(np.float32)
            
            # Basic features
            features = []
            
            # Spectral features
            try:
                mfccs = librosa.feature.mfcc(y=audio_data, sr=self.RATE, n_mfcc=13)
                features.extend([
                    np.mean(mfccs),
                    np.std(mfccs),
                    np.max(mfccs),
                    np.min(mfccs)
                ])
            except:
                features.extend([0, 0, 0, 0])
            
            # Zero crossing rate
            try:
                zcr = librosa.feature.zero_crossing_rate(audio_data)
                features.extend([np.mean(zcr), np.std(zcr)])
            except:
                features.extend([0, 0])
            
            # Spectral centroid
            try:
                spectral_centroid = librosa.feature.spectral_centroid(y=audio_data, sr=self.RATE)
                features.extend([np.mean(spectral_centroid), np.std(spectral_centroid)])
            except:
                features.extend([0, 0])
            
            # RMS energy
            try:
                rms = librosa.feature.rms(y=audio_data)
                features.extend([np.mean(rms), np.std(rms)])
            except:
                features.extend([0, 0])
            
            # Spectral rolloff
            try:
                rolloff = librosa.feature.spectral_rolloff(y=audio_data, sr=self.RATE)
                features.extend([np.mean(rolloff), np.std(rolloff)])
            except:
                features.extend([0, 0])
            
            # Tempo
            try:
                tempo, _ = librosa.beat.beat_track(y=audio_data, sr=self.RATE)
                features.append(tempo)
            except:
                features.append(0)
            
            # Chroma features
            try:
                chroma = librosa.feature.chroma_stft(y=audio_data, sr=self.RATE)
                features.extend([np.mean(chroma), np.std(chroma)])
            except:
                features.extend([0, 0])
            
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
    
    def audio_callback(self, in_data, frame_count, time_info, status):
        """PyAudio callback function"""
        try:
            # Convert audio data to numpy array
            audio_data = np.frombuffer(in_data, dtype=np.int16).astype(np.float32) / 32768.0
            
            # Add to buffer
            samples_to_add = min(len(audio_data), self.WINDOW_SIZE - self.buffer_index)
            self.audio_buffer[self.buffer_index:self.buffer_index + samples_to_add] = audio_data[:samples_to_add]
            self.buffer_index += samples_to_add
            
            # If buffer is full, process it
            if self.buffer_index >= self.WINDOW_SIZE:
                # Put a copy of the buffer in the queue
                self.audio_queue.put(self.audio_buffer.copy())
                
                # Reset buffer
                self.audio_buffer = np.zeros(self.WINDOW_SIZE, dtype=np.float32)
                self.buffer_index = 0
            
            return (in_data, pyaudio.paContinue)
        except Exception as e:
            print(f"Audio callback error: {e}")
            return (in_data, pyaudio.paContinue)
    
    def start_recording(self):
        """Start audio recording"""
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
                stream_callback=self.audio_callback,
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
        try:
            if not self.audio_queue.empty():
                audio_data = self.audio_queue.get_nowait()
                features = self.extract_features(audio_data)
                
                if features is not None:
                    emotion, confidence = self.predict_emotion(features)
                    engagement = self.map_to_engagement(emotion)
                    
                    return {
                        'emotion': emotion,
                        'confidence': confidence,
                        'engagement': engagement,
                        'timestamp': time.time()
                    }
            
            return None
            
        except queue.Empty:
            return None
        except Exception as e:
            st.error(f"Analysis error: {str(e)}")
            return None

@st.cache_resource
def get_audio_processor():
    """Get cached audio processor instance"""
    return StreamlitAudioProcessor()

def render_audio_component():
    """Render the audio monitoring component"""
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