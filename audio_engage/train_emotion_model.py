import os
import numpy as np
import pandas as pd
import librosa
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report
from tqdm import tqdm

# Mapping of emotions to our four classes
EMOTION_MAPPING = {
    'neutral': 'neutral',
    'calm': 'neutral',
    'happy': 'neutral',
    'sad': 'boredom',
    'angry': 'distress',
    'fearful': 'distress',
    'disgust': 'distress',
    'surprised': 'confusion',
    'confused': 'confusion'
}

# RAVDESS emotion code to label mapping
RAVDESS_EMOTION_MAP = {
    '01': 'neutral',      # neutral
    '02': 'calm',        # calm
    '03': 'happy',       # happy
    '04': 'sad',         # sad
    '05': 'angry',       # angry
    '06': 'fearful',     # fearful
    '07': 'disgust',     # disgust
    '08': 'surprised'    # surprised
}

def extract_features(file_path):
    """Extract audio features from an audio file."""
    try:
        # Load the audio file
        y, sr = librosa.load(file_path, sr=None)
        
        # Extract MFCCs
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        mfccs_mean = np.mean(mfccs, axis=1)
        
        # Extract Chroma features
        chroma = librosa.feature.chroma_stft(y=y, sr=sr)
        chroma_mean = np.mean(chroma, axis=1)
        
        # Extract Mel spectrogram
        mel = librosa.feature.melspectrogram(y=y, sr=sr)
        mel_mean = np.mean(mel, axis=1)[:20]  # First 20 features
        
        # Combine all features
        features = np.concatenate((mfccs_mean, chroma_mean, mel_mean))
        return features
    
    except Exception as e:
        print(f"Error extracting features from {file_path}: {e}")
        return None

def get_ravdess_emotion_label(file_name):
    """Extract emotion label from RAVDESS filename and map to engagement class."""
    try:
        parts = file_name.split('-')
        if len(parts) >= 3:
            emotion_code = parts[2]
            base_emotion = RAVDESS_EMOTION_MAP.get(emotion_code)
            if base_emotion:
                return EMOTION_MAPPING.get(base_emotion)
    except Exception as e:
        print(f"Error parsing emotion from {file_name}: {e}")
    return None

def main():
    print("Simple Audio Emotion Detection Model Training")
    print("===========================================")
    
    # Get dataset path
    data_dir = input("Enter the path to your dataset directory: ") or "datasets/ravdess"
    if not os.path.exists(data_dir):
        print(f"Error: Directory {data_dir} does not exist.")
        return
    
    # Get model type
    model_type = input("Which model would you like to train (randomforest or svm): ") or "randomforest"
    
    # Find all audio files
    audio_files = []
    for root, _, files in os.walk(data_dir):
        for file in files:
            if file.endswith(('.wav', '.mp3')):
                audio_files.append(os.path.join(root, file))
    
    if not audio_files:
        print("No audio files found in the specified directory.")
        return
    
    print(f"Found {len(audio_files)} audio files.")
    
    # Extract features and assign labels
    features = []
    labels = []
    
    for file_path in tqdm(audio_files, desc="Extracting features"):
        file_name = os.path.basename(file_path)
        mapped_emotion = get_ravdess_emotion_label(file_name)
        if mapped_emotion:
            feature = extract_features(file_path)
            if feature is not None:
                features.append(feature)
                labels.append(mapped_emotion)
        else:
            print(f"Warning: Could not determine emotion for {file_path}. Skipping.")
    
    if not features:
        print("No features were extracted. Please check your dataset.")
        return
    
    # Convert to numpy arrays
    X = np.array(features)
    y = np.array(labels)
    
    # Print dataset summary
    unique_emotions, counts = np.unique(y, return_counts=True)
    print("\nEmotion distribution in the dataset:")
    for emotion, count in zip(unique_emotions, counts):
        print(f"  {emotion}: {count}")
    # Warn if data is imbalanced
    if np.min(counts) / np.max(counts) < 0.5:
        print("[WARNING] Your dataset is imbalanced. Consider adding more samples for underrepresented classes.")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train model
    print(f"\nTraining {model_type} model...")
    if model_type.lower() == 'randomforest':
        model = RandomForestClassifier(n_estimators=100, random_state=42)
    else:
        model = SVC(kernel='rbf', probability=True, random_state=42)
    
    model.fit(X_train_scaled, y_train)
    
    # Evaluate model
    print("\nEvaluating model...")
    y_pred = model.predict(X_test_scaled)
    print(classification_report(y_test, y_pred))
    
    # Save model and feature extraction info
    feature_info = {
        'n_mfcc': 13,
        'mel_features': 20,
        'feature_order': ['mfccs_mean', 'chroma_mean', 'mel_mean']
    }
    model_data = {
        'model': model,
        'scaler': scaler,
        'emotion_mapping': EMOTION_MAPPING,
        'feature_info': feature_info,
        'classes': list(unique_emotions)
    }
    joblib.dump(model_data, 'emotion_detection_model.joblib')
    print("Model saved as 'emotion_detection_model.joblib'")

if __name__ == "__main__":
    main()