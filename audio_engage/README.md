# Audio Emotion Detection

This is a Python-based machine learning pipeline for detecting emotions from short audio samples (2-3 seconds). The model can classify audio into four emotion categories:

- **Distress**: Includes angry, fearful, and disgust emotions
- **Confusion**: Includes confused and surprised emotions
- **Boredom**: Includes sad emotion
- **Neutral**: Includes calm and neutral emotions

## Project Structure

```
emotion_detection/
├── train_emotion_model.py     # Script for feature extraction and model training
├── predict_emotion.py         # Script for making predictions on new audio samples
├── api_server.py              # Flask API for integrating with browser extension
├── evaluate_model.py          # Script for evaluating model performance
├── record_and_predict.py      # Utility for recording audio and making predictions
├── requirements.txt           # Project dependencies
└── emotion_detection_model.joblib    # Trained model file (generated after training)
```

## Installation

1. Clone the repository
2. Install the required dependencies:

```
pip install -r requirements.txt
```

Note: PyAudio installation might require additional steps depending on your operating system:

- On Windows, you might need to install a wheel file from https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
- On Linux: `sudo apt-get install portaudio19-dev python-pyaudio`
- On macOS: `brew install portaudio`

## Usage

### Training the Model

1. Download a dataset like RAVDESS or CREMA-D
2. Run the training script:

```
python train_emotion_model.py
```

Follow the prompts to specify the dataset location and model type (RandomForest or SVM).

### Making Predictions

To predict emotions from an audio file:

```
python predict_emotion.py path/to/audio_file.wav
```

### Recording and Predicting

To record audio and immediately predict the emotion:

```
python record_and_predict.py --duration 3
```

### Evaluating the Model

To evaluate the model on a test dataset:

```
python evaluate_model.py
```

### Running the API Server

To start the Flask API server for integration with a browser extension:

```
python api_server.py
```

The API will be available at `http://localhost:5000/predict_emotion`.

## API Usage

Send a POST request to `/predict_emotion` with the following JSON payload:

```json
{
    "audio_data": "base64_encoded_audio_data",
    "file_format": "wav"
}
```

Response:

```json
{
    "success": true,
    "message": "Emotion predicted successfully",
    "emotion": "neutral"
}
```

## Integration with Browser Extension

To integrate this with a browser extension:

1. Run the API server locally
2. From your extension, capture audio using the browser's MediaRecorder API
3. Convert the audio to base64 and send it to the API
4. Process the API response to get the emotion prediction

Example JavaScript for a browser extension:

```javascript
// Capture audio from microphone
navigator.mediaDevices.getUserMedia({ audio: true })
  .then(stream => {
    const mediaRecorder = new MediaRecorder(stream);
    const audioChunks = [];
    
    mediaRecorder.addEventListener("dataavailable", event => {
      audioChunks.push(event.data);
    });
    
    mediaRecorder.addEventListener("stop", () => {
      const audioBlob = new Blob(audioChunks);
      const reader = new FileReader();
      
      reader.readAsDataURL(audioBlob);
      reader.onloadend = () => {
        const base64data = reader.result.split(',')[1];
        
        // Send to API
        fetch("http://localhost:5000/predict_emotion", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            audio_data: base64data,
            file_format: "wav"
          }),
        })
        .then(response => response.json())
        .then(data => {
          console.log("Detected emotion:", data.emotion);
          // Use the emotion data in your extension
        });
      };
    });
    
    // Record for 3 seconds
    mediaRecorder.start();
    setTimeout(() => mediaRecorder.stop(), 3000);
  });
```

## Future Improvements

- Implement a more sophisticated deep learning model (e.g., CNN or RNN)
- Add real-time streaming emotion detection
- Package the model for WebAssembly to run directly in the browser
- Add confidence scores for emotion predictions
