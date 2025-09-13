import pyaudio
import wave
import numpy as np
import os
import time
import threading
import queue
import librosa
import joblib
from datetime import datetime
import warnings

# Suppress warnings
warnings.filterwarnings("ignore")

# Constants
CHUNK_SIZE = 4096  # Number of frames per buffer
FORMAT = pyaudio.paInt16  # Audio format
CHANNELS = 1  # Mono
RATE = 16000  # Sample rate in Hz
WINDOW_DURATION = 3  # Duration of each analysis window in seconds
WINDOW_SIZE = int(RATE * WINDOW_DURATION)  # Window size in samples
MODEL_PATH = 'emotion_detection_model.joblib'  # Path to the model

# Engagement mapping for binary output
ENGAGED_EMOTIONS = {'neutral', 'happy', 'surprised'}  # adjust as needed

def map_to_engagement(emotion):
    if emotion.lower() in ENGAGED_EMOTIONS:
        return 'Engaged'
    else:
        return 'Distracted'

class AudioProcessor:
    def __init__(self, model_path=MODEL_PATH):
        """
        Initialize the real-time audio processor        """
        print("Loading model...")
        self.model_data = joblib.load(model_path)
        self.model = self.model_data['model']
        self.scaler = self.model_data['scaler']
        print("Model loaded successfully")
        
        self.audio_buffer = np.zeros(WINDOW_SIZE, dtype=np.float32)
        self.buffer_index = 0
        self.is_recording = False
        self.audio_queue = queue.Queue()
        
    def extract_features(self, audio_data):
        """Extract audio features from numpy array"""
        try:
            y = audio_data.astype(np.float32)
            # Debug: print shape and stats
            print(f"[DEBUG] Input audio shape: {y.shape}, min: {y.min()}, max: {y.max()}, mean: {y.mean()}")
            # If the audio is silent (all zeros or near zero), return a special flag
            if np.allclose(y, 0, atol=1e-4):
                print("[DEBUG] No audio detected (silent input)")
                return 'NO_AUDIO'
            # Extract MFCCs
            mfccs = librosa.feature.mfcc(y=y, sr=RATE, n_mfcc=13)
            mfccs_mean = np.mean(mfccs, axis=1)
            # Extract Chroma
            chroma = librosa.feature.chroma_stft(y=y, sr=RATE)
            chroma_mean = np.mean(chroma, axis=1)
            # Extract Mel spectrogram
            mel = librosa.feature.melspectrogram(y=y, sr=RATE)
            mel_mean = np.mean(mel, axis=1)[:20]  # First 20 features
            # Combine features - EXACTLY matching the training features
            features = np.concatenate((mfccs_mean, chroma_mean, mel_mean))
            print(f"[DEBUG] Feature vector shape: {features.shape}, values: {features[:5]} ...")
            return features
        except Exception as e:
            print(f"Error extracting features: {e}")
            return None

    def predict_engagement(self, audio_data):
        """Predict engagement from audio data"""
        features = self.extract_features(audio_data)
        if isinstance(features, str) and features == 'NO_AUDIO':
            return "Engaged", "no_audio"
        if features is None:
            return "Error processing audio", "error"
        # Scale features
        features = features.reshape(1, -1)
        if features.shape[1] != self.scaler.mean_.shape[0]:
            print(f"[ERROR] Feature shape mismatch: got {features.shape[1]}, expected {self.scaler.mean_.shape[0]}")
            return "Feature shape mismatch", "error"
        features = self.scaler.transform(features)
        # Make prediction
        prediction = self.model.predict(features)[0]
        print(f"[DEBUG] Raw model prediction: {prediction}")
        # Map to binary engagement status
        engagement = map_to_engagement(prediction)
        return engagement, prediction
        
    def audio_callback(self, in_data, frame_count, time_info, status):
        """Callback function for PyAudio"""
        if self.is_recording:
            # Convert byte data to numpy array
            audio_data = np.frombuffer(in_data, dtype=np.int16)
            
            # Normalize
            audio_float = audio_data.astype(np.float32) / 32768.0
            
            # Add to buffer
            remaining = WINDOW_SIZE - self.buffer_index
            if remaining <= frame_count:
                # Fill buffer and process
                self.audio_buffer[self.buffer_index:] = audio_float[:remaining]
                self.audio_queue.put(np.copy(self.audio_buffer))
                
                # Reset buffer and fill with remaining data
                self.buffer_index = 0
                excess = frame_count - remaining
                if excess > 0:
                    self.audio_buffer[:excess] = audio_float[remaining:]
                    self.buffer_index = excess
            else:
                # Just add to buffer
                self.audio_buffer[self.buffer_index:self.buffer_index+frame_count] = audio_float
                self.buffer_index += frame_count
        
        # Always return empty data and continue flag
        return (b'', pyaudio.paContinue)
    
    def analysis_thread(self):
        """Thread for processing audio data"""
        while self.is_recording:
            try:
                # Get audio data from queue with timeout
                audio_data = self.audio_queue.get(timeout=1.0)
                
                # Process audio data
                engagement_status, emotion = self.predict_engagement(audio_data)
                
                # Get current time
                current_time = datetime.now().strftime("%H:%M:%S")
                
                # Print status with color based on engagement
                if engagement_status == "Engaged":
                    status_color = "\033[92m"  # Green
                elif engagement_status == "Not Fully Engaged":
                    status_color = "\033[93m"  # Yellow
                else:
                    status_color = "\033[91m"  # Red
                    
                reset_color = "\033[0m"  # Reset color
                
                print(f"{current_time} - {status_color}{engagement_status}{reset_color} (Emotion: {emotion})")
                
                # Mark task as done
                self.audio_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error in analysis thread: {e}")
    
    def start_monitoring(self):
        """Start monitoring audio"""
        print("Initializing audio stream...")
        self.p = pyaudio.PyAudio()
        
        # Open stream
        self.stream = self.p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            output=False,
            frames_per_buffer=CHUNK_SIZE,
            stream_callback=self.audio_callback
        )
        
        self.is_recording = True
        
        # Start analysis thread
        self.analyzer = threading.Thread(target=self.analysis_thread)
        self.analyzer.daemon = True
        self.analyzer.start()
        
        print("\nReal-time Engagement Monitoring Started")
        print("======================================")
        print("Press Ctrl+C to stop monitoring")
        print()
        
        try:
            # Keep main thread alive
            while self.is_recording:
                time.sleep(0.1)
        except KeyboardInterrupt:
            self.stop_monitoring()
    
    def stop_monitoring(self):
        """Stop monitoring audio"""
        print("\nStopping engagement monitoring...")
        self.is_recording = False
        
        # Wait for analysis thread to finish
        if hasattr(self, 'analyzer') and self.analyzer.is_alive():
            self.analyzer.join(timeout=1.0)
        
        # Stop and close the audio stream
        if hasattr(self, 'stream'):
            self.stream.stop_stream()
            self.stream.close()
        
        # Terminate PyAudio
        if hasattr(self, 'p'):
            self.p.terminate()
        
        print("Monitoring stopped.")

def main():
    # Create audio processor
    processor = AudioProcessor()
    
    # Start monitoring
    processor.start_monitoring()

if __name__ == "__main__":
    main()
