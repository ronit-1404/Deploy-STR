import os
import numpy as np
import librosa
import joblib
import argparse

def extract_features(file_path, n_mfcc=13, n_chroma=12, n_mel=128):
    """
    Extract audio features from a file using librosa
    
    Parameters:
        file_path (str): Path to the audio file
        n_mfcc (int): Number of MFCCs to extract
        n_chroma (int): Number of chroma features
        n_mel (int): Number of mel bands
        
    Returns:
        np.array: Feature vector
    """
    try:
        # Load audio file
        y, sr = librosa.load(file_path, sr=None)
        
        # Extract features
        # MFCCs
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)
        mfcc_mean = np.mean(mfccs, axis=1)
        mfcc_std = np.std(mfccs, axis=1)
        
        # Chroma
        chroma = librosa.feature.chroma_stft(y=y, sr=sr, n_chroma=n_chroma)
        chroma_mean = np.mean(chroma, axis=1)
        chroma_std = np.std(chroma, axis=1)
        
        # Mel spectrogram
        mel_spec = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=n_mel)
        mel_mean = np.mean(mel_spec, axis=1)
        mel_std = np.std(mel_spec, axis=1)
        
        # Combine all features into a single vector
        features = np.concatenate([
            mfcc_mean, mfcc_std,
            chroma_mean, chroma_std,
            mel_mean, mel_std
        ])
        
        return features
    
    except Exception as e:
        print(f"Error extracting features from {file_path}: {e}")
        return None

# Map model output to 'Engaged' or 'Distracted'
ENGAGED_EMOTIONS = {'neutral', 'happy', 'surprised'}  # adjust as needed

def map_to_engagement(emotion):
    if emotion.lower() in ENGAGED_EMOTIONS:
        return 'Engaged'
    else:
        return 'Distracted'

def predict_emotion_from_audio(audio_file_path, model_path='emotion_detection_model.joblib'):
    """
    Predict emotion from an audio file using the trained model
    
    Parameters:
        audio_file_path (str): Path to the audio file
        model_path (str): Path to the saved model file
        
    Returns:
        str: Predicted emotion ('distress', 'confusion', 'boredom', or 'neutral')
    """
    # Load the model dict
    model_data = joblib.load(model_path)
    model = model_data['model']
    scaler = model_data['scaler']
    
    # Extract features from the audio file
    features = extract_features(audio_file_path)
    
    if features is None:
        return "Error processing audio"
    
    # Reshape and scale features for prediction
    features = features.reshape(1, -1)
    features = scaler.transform(features)
    
    # Make prediction
    prediction = model.predict(features)[0]
    # Map to engagement
    engagement = map_to_engagement(prediction)
    return engagement

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Predict emotion from audio file')
    parser.add_argument('audio_file', type=str, help='Path to the audio file')
    parser.add_argument('--model', type=str, default='emotion_detection_model.joblib', 
                        help='Path to the model file')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.audio_file):
        print(f"Error: Audio file '{args.audio_file}' not found")
        exit(1)
        
    if not os.path.exists(args.model):
        print(f"Error: Model file '{args.model}' not found")
        exit(1)
    
    emotion = predict_emotion_from_audio(args.audio_file, args.model)
    print(f"Detected engagement: {emotion}")
