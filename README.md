# Streamlit Engagement Monitor

A comprehensive real-time engagement monitoring system built with Streamlit that combines audio emotion detection and screen activity analysis.

## 🌐 Live Demo

**Try the live demo:** [Streamlit Cloud Demo](https://your-app-url.streamlit.app)

*Note: The cloud version runs in demo mode with simulated data due to browser security limitations.*

## Features

### 🎤 Audio Emotion Detection
- Real-time emotion detection from microphone input
- Engagement mapping based on emotional states
- Support for multiple emotion categories
- Confidence scoring
- **Local only** - Requires PyAudio and librosa

### 🖥️ Screen Activity Analysis
- Real-time screen capture and OCR
- Context detection (Programming, Reading, Video, etc.)
- Sentiment analysis of screen content
- Idle time tracking
- Chrome tab monitoring
- **Local only** - Requires system permissions

### 📊 Live Dashboard
- Real-time metrics visualization
- Interactive charts and graphs
- Session analytics and insights
- Data export capabilities
- Productivity scoring

## Deployment Options

### 🌐 Cloud Deployment (Streamlit Cloud)

**Pros:**
- Easy to share and demo
- No local setup required
- Automatic deployment from GitHub

**Cons:**
- Audio features disabled (browser security)
- Screen capture not available
- Runs in simulation mode

**Deploy to Cloud:**
1. Fork this repository
2. Connect to Streamlit Cloud
3. Deploy automatically

### 💻 Local Deployment (Full Features)

**Pros:**
- Full audio emotion detection
- Complete screen analysis
- Real-time monitoring
- Privacy-first (all data stays local)

**Cons:**
- Requires setup and dependencies
- Platform-specific requirements

## Installation

### Prerequisites

1. **Python 3.8 or higher**
2. **For full features (local only):**
   - Tesseract OCR
   - Audio drivers
   - System permissions for screen capture

### Quick Setup (Local)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/deploy-str.git
   cd deploy-str
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **For full audio features:**
   ```bash
   # Install additional audio dependencies
   pip install pyaudio librosa soundfile
   
   # Install spaCy model
   python -m spacy download en_core_web_sm
   ```

4. **Run the app:**
   ```bash
   streamlit run streamlit_app.py
   ```

### Windows Setup Script

```powershell
# Run the automated setup
.\setup.ps1
```

## Usage

### Cloud Demo Mode
- Visit the live demo link
- Click "Demo Mode" buttons to generate simulated data
- Explore the dashboard and analytics features
- Export sample data to understand the format

### Local Full Mode
1. **Configure Settings:** Use the sidebar to enable/disable features
2. **Start Monitoring:** 
   - Audio Tab: Click "Start Audio" for emotion detection
   - Screen Tab: Click "Start Screen" for screen analysis
3. **View Data:** Monitor real-time metrics in the Dashboard
4. **Analyze:** Use Analytics tab for detailed insights
5. **Export:** Download session data as CSV

## Configuration

### Environment Detection
The app automatically detects the environment:
- **Cloud Mode:** Simulated data and demo features
- **Local Mode:** Full audio and screen analysis

### Settings
- **Update Interval:** Data refresh rate (1-10 seconds)
- **Audio Window:** Sample duration for emotion analysis
- **Confidence Threshold:** Minimum confidence for predictions
- **Data Retention:** Maximum data points to keep in memory

## Data Export

Session data includes:
- `timestamp`: Unix timestamp
- `emotion`: Detected emotion (local) or simulated
- `engagement`: Engagement level (Engaged/Distracted)
- `context`: Screen context (Programming, Reading, etc.)
- `sentiment`: Content sentiment analysis
- `productivity_score`: Calculated productivity percentage

## Architecture

### Cloud-Compatible Design
```
streamlit_app.py          # Main application
├── components/
│   ├── audio_monitor.py  # Audio processing (with cloud fallback)
│   └── screen_monitor.py # Screen analysis (with cloud fallback)
├── requirements.txt      # Cloud-compatible dependencies
├── packages.txt          # System packages for Streamlit Cloud
└── .streamlit/
    ├── config.toml       # Streamlit configuration
    └── secrets.toml      # Cloud environment detection
```

### Dependency Management
- **Core:** Always available (Streamlit, pandas, plotly)
- **Optional:** Graceful degradation (audio, screen capture)
- **Platform-specific:** Conditional imports

## Development

### Local Development
```bash
# Install full dependencies
pip install -r requirements.txt
pip install pyaudio librosa soundfile

# Run with hot reload
streamlit run streamlit_app.py
```

### Cloud Development
```bash
# Use cloud-compatible requirements only
pip install streamlit pandas numpy plotly opencv-python-headless

# Test cloud mode
CLOUD_DEPLOYMENT=true streamlit run streamlit_app.py
```

## Troubleshooting

### Cloud Deployment Issues
1. **Import Errors:** Check `requirements.txt` for cloud compatibility
2. **Package Issues:** Verify `packages.txt` system dependencies
3. **Memory Limits:** Reduce data retention settings

### Local Installation Issues
1. **PyAudio Fails:** 
   ```bash
   pip install pipwin
   pipwin install pyaudio
   ```
2. **Tesseract Not Found:** Install and add to PATH
3. **Permission Denied:** Run as administrator (Windows)

## Privacy & Security

- **Local Processing:** All analysis done on your machine
- **No Data Upload:** Audio/screen data never leaves your device
- **Cloud Demo:** Uses only simulated data
- **Optional Export:** Manual data export only

## Contributing

1. Fork the repository
2. Create a feature branch
3. Test both local and cloud compatibility
4. Submit a pull request

## License

MIT License - See LICENSE file for details

## Support

- **Documentation:** Check this README and inline comments
- **Issues:** Create GitHub issues for bugs
- **Discussions:** Use GitHub Discussions for questions

---

**🌟 Star this repository if you find it useful!**