# 🎯 Real-time Engagement Monitor

A comprehensive Streamlit application for monitoring audio emotions and screen engagement in real-time.

## 🚀 Cloud Deployment (Streamlit Cloud)

### Prerequisites
1. **GitHub Repository**: Push your code to a GitHub repository
2. **Streamlit Cloud Account**: Sign up at [share.streamlit.io](https://share.streamlit.io)

### Deployment Steps

#### 1. **Prepare Your Repository**
Make sure your repository contains:
- `streamlit_app.py` (main application file)
- `requirements.txt` (cloud-compatible dependencies)
- `packages.txt` (system packages for Ubuntu)
- `.streamlit/config.toml` (Streamlit configuration)
- `components/` folder with audio and screen monitoring modules

#### 2. **Deploy to Streamlit Cloud**

1. **Connect GitHub**: 
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Click "New app"
   - Connect your GitHub account

2. **Configure Deployment**:
   - Repository: `your-username/Deploy-STR`
   - Branch: `main`
   - Main file path: `streamlit_app.py`

3. **Advanced Settings** (Optional):
   - Python version: `3.9` (recommended for compatibility)
   - Custom domain: Add if you have one

4. **Deploy**: Click "Deploy!" button

#### 3. **Expected Behavior**

**Cloud Environment (Demo Mode)**:
- ✅ Audio monitoring shows demo emotions (Happy/Neutral modes)
- ✅ Screen monitoring shows simulated context analysis
- ✅ All visualizations and analytics work
- ❌ Real microphone/screen capture (not available in cloud)

**Local Environment**:
- ✅ Full real-time audio emotion detection
- ✅ Live screen capture and analysis
- ✅ All features fully functional

## 🛠️ Local Development

### Installation
```bash
# Clone the repository
git clone https://github.com/your-username/Deploy-STR.git
cd Deploy-STR

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm

# Run the application
streamlit run streamlit_app.py
```

## 📁 Project Structure

```
Deploy-STR/
├── streamlit_app.py           # Main Streamlit application
├── requirements.txt           # Cloud-compatible dependencies
├── packages.txt              # System packages for deployment
├── components/
│   ├── audio_monitor.py       # Audio emotion detection
│   └── screen_monitor.py      # Screen analysis and OCR
├── audio_engage/
│   ├── emotion_detection_model.joblib  # Pre-trained model
│   └── ...                   # Original audio engagement code
├── screen-analyzer/
│   └── ...                   # Original screen analysis code
└── .streamlit/
    └── config.toml           # Streamlit configuration
```

## 🎛️ Features

### Audio Monitoring
- **Real-time emotion detection** from microphone input
- **Engagement level analysis** (Engaged/Distracted)
- **Confidence scoring** for predictions
- **Demo mode** for cloud deployment

### Screen Monitoring  
- **Live screen capture** and OCR text extraction
- **Context detection** (Programming, Reading, etc.)
- **Sentiment analysis** of screen content
- **Activity tracking** and idle time monitoring
- **Chrome tab detection** for web browsing analysis

### Analytics Dashboard
- **Real-time metrics** and visualizations
- **Historical data** tracking and trends
- **Productivity scoring** based on engagement
- **Session insights** and patterns

## 🔧 Configuration

### Environment Detection
The app automatically detects if it's running in:
- **Local environment**: Full functionality with hardware access
- **Cloud environment**: Demo mode with simulated data

### Customization
- Modify `requirements.txt` for different dependencies
- Update `.streamlit/config.toml` for UI customization
- Adjust monitoring intervals in component files

## 🚨 Troubleshooting

### Common Issues

1. **spaCy Model Error**:
   ```bash
   python -m spacy download en_core_web_sm
   ```

2. **Audio Issues (Local)**:
   - Check microphone permissions
   - Install PyAudio: `pip install pyaudio`

3. **Screen Capture Issues**:
   - Install system dependencies from `packages.txt`
   - Check display permissions on macOS

4. **Cloud Deployment Fails**:
   - Verify `requirements.txt` has no local-only packages
   - Check `packages.txt` format (no comments)
   - Ensure Python 3.9 compatibility

## 📊 Demo Data

In cloud mode, the application provides:
- **Simulated emotions**: Happy, Neutral, Focused states
- **Mock screen analysis**: Programming, Learning contexts
- **Sample metrics**: Productivity scores and engagement levels

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test locally and in cloud
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.