# Streamlit Engagement Monitor

A comprehensive real-time engagement monitoring system built with Streamlit that combines audio emotion detection and screen activity analysis.

## Features

### 🎤 Audio Emotion Detection
- Real-time emotion detection from microphone input
- Engagement mapping based on emotional states
- Support for multiple emotion categories
- Confidence scoring

### 🖥️ Screen Activity Analysis
- Real-time screen capture and OCR
- Context detection (Programming, Reading, Video, etc.)
- Sentiment analysis of screen content
- Idle time tracking
- Chrome tab monitoring

### 📊 Live Dashboard
- Real-time metrics visualization
- Interactive charts and graphs
- Session analytics and insights
- Data export capabilities
- Productivity scoring

## Installation

### Prerequisites

1. **Python 3.8 or higher**
2. **Tesseract OCR** (for screen text analysis)
   - Download from: https://github.com/UB-Mannheim/tesseract/wiki
   - Add to PATH environment variable
3. **Audio drivers** (for microphone access)

### Setup

1. **Clone or download this repository**

2. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

3. **Install spaCy model:**
   ```powershell
   python -m spacy download en_core_web_sm
   ```

4. **For audio processing on Windows:**
   ```powershell
   # If PyAudio installation fails, try:
   pip install pipwin
   pipwin install pyaudio
   ```

## Usage

### Running the Streamlit App

```powershell
streamlit run streamlit_app.py
```

The app will open in your default web browser at `http://localhost:8501`

### Using the Interface

1. **Configure Settings:** Use the sidebar to enable/disable features and adjust settings
2. **Start Monitoring:** 
   - Click "Start Audio" in the Audio Monitor tab to begin emotion detection
   - Click "Start Screen" in the Screen Monitor tab to begin screen analysis
3. **View Real-time Data:** Monitor engagement metrics in the Dashboard tab
4. **Analyze Patterns:** Use the Analytics tab to view detailed insights
5. **Export Data:** Download session data as CSV from the sidebar

### Components

#### Audio Monitor (`components/audio_monitor.py`)
- Captures microphone input in real-time
- Extracts audio features (MFCC, spectral features, etc.)
- Predicts emotions using pre-trained model
- Maps emotions to engagement levels

#### Screen Monitor (`components/screen_monitor.py`)
- Captures screenshots at regular intervals
- Performs OCR to extract text content
- Analyzes context and sentiment
- Tracks application usage and idle time

## Configuration

### Audio Settings
- **Update Interval:** How often to refresh data (1-10 seconds)
- **Audio Window:** Duration of audio samples for analysis (2-5 seconds)
- **Confidence Threshold:** Minimum confidence for emotion predictions

### Screen Settings
- **Monitoring Interval:** How often to capture and analyze screen
- **Text Analysis:** OCR and sentiment analysis settings
- **Context Detection:** Application and content type recognition

## Data Export

Session data can be exported as CSV with the following columns:
- `timestamp`: Unix timestamp of the data point
- `emotion`: Detected emotion from audio
- `engagement`: Engagement level (Engaged/Distracted)
- `context`: Screen context (Programming, Reading, etc.)
- `sentiment`: Sentiment of screen content
- `productivity_score`: Calculated productivity percentage

## Deployment

### Local Deployment

The app runs locally and all processing is done on your machine for privacy.

### Cloud Deployment (Optional)

For cloud deployment, consider:
1. **Streamlit Cloud:** Easy deployment for public apps
2. **Heroku:** For more control over the environment
3. **Docker:** For containerized deployment

**Note:** Audio and screen capture may have limitations in cloud environments due to privacy and security restrictions.

## Privacy and Security

- **Local Processing:** All analysis is performed locally on your machine
- **No Data Upload:** Audio and screen data never leave your device
- **Optional Export:** Data export is manual and user-controlled
- **Secure Storage:** Session data is stored only in memory during runtime

## Troubleshooting

### Common Issues

1. **PyAudio Installation Fails:**
   ```powershell
   pip install pipwin
   pipwin install pyaudio
   ```

2. **Tesseract Not Found:**
   - Ensure Tesseract is installed and in PATH
   - Set TESSDATA_PREFIX environment variable if needed

3. **Permission Denied (Screen Capture):**
   - Run PowerShell as Administrator
   - Grant screen recording permissions on macOS

4. **Model File Missing:**
   - Ensure `emotion_detection_model.joblib` is in the `audio_engage` folder
   - Train the model using `train_emotion_model.py` if needed

5. **Import Errors:**
   - Verify all dependencies are installed
   - Check Python path configuration

### Performance Optimization

- Adjust update intervals based on your system performance
- Reduce audio window size for faster processing
- Limit data retention for memory optimization

## Development

### Project Structure
```
strem/
├── streamlit_app.py              # Main Streamlit application
├── components/
│   ├── audio_monitor.py          # Audio processing component
│   └── screen_monitor.py         # Screen analysis component
├── audio_engage/                 # Audio emotion detection module
├── screen-analyzer/              # Screen analysis module
└── requirements.txt              # Dependencies
```

### Adding Features

1. **Custom Emotions:** Modify emotion mapping in `audio_monitor.py`
2. **New Contexts:** Extend context detection in `screen_monitor.py`
3. **Additional Metrics:** Add new metrics to the dashboard
4. **Export Formats:** Support additional export formats

## License

This project is for educational and personal use. Please ensure compliance with local privacy laws and regulations when using screen capture and audio recording features.

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Verify system requirements and dependencies
3. Test individual components separately if needed