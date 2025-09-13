# from flask import Flask, request, jsonify 
# from flask_cors import CORS
# import tempfile
# import os
# import base64
# import joblib
# import numpy as np
# from predict_emotion import predict_emotion_from_audio

# app = Flask(__name__)
# CORS(app)

# # Set the default model path
# MODEL_PATH = os.path.join(os.path.dirname(__file__), 'emotion_detection_model.joblib')

# @app.route('/predict_emotion', methods=['POST'])
# def predict_emotion():
#     """
#     Endpoint to predict emotion from audio data
    
#     Expected input:
#     {
#         "audio_data": "base64 encoded audio data",
#         "file_format": "wav"  # Optional, defaults to wav
#     }
    
#     Returns:
#     {
#         "emotion": "predicted emotion",
#         "success": true/false,
#         "message": "error message if any"
#     }
#     """
#     try:
#         # Get request data
#         data = request.json
        
#         if not data or 'audio_data' not in data:
#             return jsonify({
#                 'success': False,
#                 'message': 'No audio data provided',
#                 'emotion': 'unknown'
#             }), 400
        
#         # Get audio data
#         audio_data = data['audio_data']
#         file_format = data.get('file_format', 'wav')
        
#         # Decode base64 audio data
#         try:
#             audio_bytes = base64.b64decode(audio_data)
#         except:
#             return jsonify({
#                 'success': False,
#                 'message': 'Invalid audio data encoding',
#                 'emotion': 'unknown'
#             }), 400
        
#         # Save audio data to temporary file
#         with tempfile.NamedTemporaryFile(suffix=f'.{file_format}', delete=False) as temp_file:
#             temp_path = temp_file.name
#             temp_file.write(audio_bytes)
        
#         try:
#             # Predict emotion
#             emotion = predict_emotion_from_audio(temp_path, MODEL_PATH)

#             # Map emotion to 'engaged' or 'distracted'
#             engaged_emotions = {'happy', 'neutral', 'surprised'}  # adjust as needed
#             if emotion.lower() in engaged_emotions:
#                 engagement = 'engaged'
#             else:
#                 engagement = 'distracted'

#             return jsonify({
#                 'success': True,
#                 'message': 'Emotion predicted successfully',
#                 'emotion': engagement
#             })
#         finally:
#             # Always clean up the temporary file
#             if os.path.exists(temp_path):
#                 os.remove(temp_path)
                
#     except Exception as e:
#         return jsonify({
#             'success': False,
#             'message': f'Error processing request: {str(e)}',
#             'emotion': 'unknown'
#         }), 500

# @app.route('/health', methods=['GET'])
# def health_check():
#     """Simple health check endpoint"""
#     return jsonify({'status': 'ok'})

# if __name__ == '__main__':
#     # Check if model exists
#     if not os.path.exists(MODEL_PATH):
#         print(f"Warning: Model file not found at {MODEL_PATH}")
#         print("You need to train a model first using train_emotion_model.py")
    
#     # Run the Flask app
#     app.run(host='0.0.0.0', port=5002)

from flask import Flask, request, jsonify 
from flask_cors import CORS
import tempfile
import os
import base64
import joblib
import numpy as np
import json
import datetime
import librosa
from predict_emotion import predict_emotion_from_audio

app = Flask(__name__)
CORS(app)

# Set the default model path
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'emotion_detection_model.joblib')
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')

# Create data directory if it doesn't exist
os.makedirs(DATA_DIR, exist_ok=True)

def write_to_json_file(data_type, data):
    """Write data to a JSON file in the data directory"""
    try:
        file_path = os.path.join(DATA_DIR, f"{data_type}.json")
        
        # Read existing data if available
        existing_data = []
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                try:
                    existing_data = json.load(f)
                except json.JSONDecodeError:
                    existing_data = []
        
        # Ensure existing_data is a list
        if not isinstance(existing_data, list):
            existing_data = []
        
        # Add timestamp to the data
        data['timestamp'] = datetime.datetime.now().isoformat()
        
        # Append new data
        existing_data.append(data)
        
        # Write updated data back to the file
        with open(file_path, 'w') as f:
            json.dump(existing_data, f, indent=2)
            
        return True
    except Exception as e:
        print(f"Error writing to JSON file: {e}")
        return False

@app.route('/predict_emotion', methods=['POST'])
def predict_emotion():
    if not request.json or 'audio_data' not in request.json:
        return jsonify({
            'success': False,
            'message': 'Missing audio_data in request',
            'emotion': 'unknown'
        }), 400
    
    try:
        # Get audio data and format
        audio_data = request.json['audio_data']
        file_format = request.json.get('file_format', 'wav')
        
        # Decode base64 audio
        try:
            audio_bytes = base64.b64decode(audio_data)
        except:
            return jsonify({
                'success': False,
                'message': 'Invalid audio data encoding',
                'emotion': 'unknown'
            }), 400
        
        # Save audio data to temporary file
        with tempfile.NamedTemporaryFile(suffix=f'.{file_format}', delete=False) as temp_file:
            temp_path = temp_file.name
            temp_file.write(audio_bytes)
        
        try:
            # Predict emotion
            emotion = predict_emotion_from_audio(temp_path, MODEL_PATH)

            # Map emotion to 'engaged' or 'distracted'
            engaged_emotions = {'happy', 'neutral', 'surprised'}  # adjust as needed
            if emotion.lower() in engaged_emotions:
                engagement = 'engaged'
            else:
                engagement = 'distracted'
            
            # Save to JSON file
            audio_data = {
                'emotion': emotion,
                'engagement': engagement,
                'userId': request.json.get('userId', 'unknown')
            }
            write_to_json_file('audio', audio_data)

            return jsonify({
                'success': True,
                'message': 'Emotion predicted successfully',
                'emotion': engagement
            })
        finally:
            # Always clean up the temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error processing request: {str(e)}',
            'emotion': 'unknown'
        }), 500

@app.route('/predict_engagement_spike', methods=['POST'])
def predict_engagement_spike():
    if not request.json or 'audio_data' not in request.json:
        return jsonify({
            'success': False,
            'message': 'Missing audio_data in request',
            'engagement': 'unknown'
        }), 400
    try:
        audio_data = request.json['audio_data']
        file_format = request.json.get('file_format', 'wav')
        try:
            audio_bytes = base64.b64decode(audio_data)
        except:
            return jsonify({
                'success': False,
                'message': 'Invalid audio data encoding',
                'engagement': 'unknown'
            }), 400
        with tempfile.NamedTemporaryFile(suffix=f'.{file_format}', delete=False) as temp_file:
            temp_path = temp_file.name
            temp_file.write(audio_bytes)
        try:
            # Load audio and calculate amplitude
            y, sr = librosa.load(temp_path, sr=None)
            rms = np.sqrt(np.mean(y**2))
            max_amp = np.max(np.abs(y))
            # Thresholds (tune as needed)
            RMS_THRESHOLD = 0.1
            MAX_AMP_THRESHOLD = 0.3
            if rms > RMS_THRESHOLD or max_amp > MAX_AMP_THRESHOLD:
                engagement = 'distracted'
            else:
                engagement = 'engaged'
            # Save to JSON file
            audio_data_obj = {
                'rms': float(rms),
                'max_amplitude': float(max_amp),
                'engagement': engagement,
                'userId': request.json.get('userId', 'unknown')
            }
            write_to_json_file('audio', audio_data_obj)
            return jsonify({
                'success': True,
                'message': 'Engagement predicted by spike logic',
                'engagement': engagement,
                'rms': float(rms),
                'max_amplitude': float(max_amp)
            })
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error processing request: {str(e)}',
            'engagement': 'unknown'
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint"""
    return jsonify({
        'status': 'ok',
        'message': 'Audio emotion detection API is running'
    })

if __name__ == '__main__':
    # Check if model exists
    if not os.path.exists(MODEL_PATH):
        print(f"Warning: Model file not found at {MODEL_PATH}")
        print("You need to train a model first using train_emotion_model.py")
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=5002)