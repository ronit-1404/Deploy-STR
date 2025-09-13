# Streamlit Engagement Monitor Setup Script
# Run this script to set up the environment and dependencies

# Check Python version
Write-Host "Checking Python version..." -ForegroundColor Green
$pythonVersion = python --version 2>&1
if ($pythonVersion -match "Python 3\.[89]|Python 3\.1[0-9]") {
    Write-Host "✓ Python version: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "⚠ Warning: Python 3.8+ recommended. Current: $pythonVersion" -ForegroundColor Yellow
}

# Create virtual environment (optional but recommended)
Write-Host "`nCreating virtual environment..." -ForegroundColor Green
python -m venv streamlit_env
if (Test-Path "streamlit_env\Scripts\Activate.ps1") {
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
    Write-Host "To activate: .\streamlit_env\Scripts\Activate.ps1" -ForegroundColor Cyan
} else {
    Write-Host "⚠ Virtual environment creation failed" -ForegroundColor Yellow
}

# Install pip dependencies
Write-Host "`nInstalling Python dependencies..." -ForegroundColor Green
pip install --upgrade pip
pip install -r requirements.txt

# Special handling for PyAudio (common issue on Windows)
Write-Host "`nChecking PyAudio installation..." -ForegroundColor Green
python -c "import pyaudio" 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ PyAudio is working" -ForegroundColor Green
} else {
    Write-Host "⚠ PyAudio installation issue detected. Trying alternative method..." -ForegroundColor Yellow
    pip install pipwin
    pipwin install pyaudio
}

# Install spaCy model
Write-Host "`nInstalling spaCy English model..." -ForegroundColor Green
python -m spacy download en_core_web_sm

# Check Tesseract installation
Write-Host "`nChecking Tesseract OCR installation..." -ForegroundColor Green
try {
    $tesseractVersion = tesseract --version 2>&1 | Select-String "tesseract"
    Write-Host "✓ Tesseract found: $tesseractVersion" -ForegroundColor Green
} catch {
    Write-Host "⚠ Tesseract OCR not found. Please install from:" -ForegroundColor Yellow
    Write-Host "   https://github.com/UB-Mannheim/tesseract/wiki" -ForegroundColor Yellow
}

# Check if emotion model exists
Write-Host "`nChecking emotion detection model..." -ForegroundColor Green
if (Test-Path "audio_engage\emotion_detection_model.joblib") {
    Write-Host "✓ Emotion detection model found" -ForegroundColor Green
} else {
    Write-Host "⚠ Emotion detection model not found" -ForegroundColor Yellow
    Write-Host "   Run 'python audio_engage\train_emotion_model.py' to train the model" -ForegroundColor Yellow
}

# Create components directory if it doesn't exist
if (!(Test-Path "components")) {
    New-Item -ItemType Directory -Path "components"
    Write-Host "✓ Created components directory" -ForegroundColor Green
}

# Test imports
Write-Host "`nTesting critical imports..." -ForegroundColor Green
$testScript = @"
try:
    import streamlit
    print("✓ Streamlit")
    import pandas
    print("✓ Pandas") 
    import numpy
    print("✓ Numpy")
    import plotly
    print("✓ Plotly")
    import librosa
    print("✓ Librosa")
    import cv2
    print("✓ OpenCV")
    import pytesseract
    print("✓ PyTesseract")
    import spacy
    print("✓ spaCy")
    print("All critical imports successful!")
except ImportError as e:
    print(f"Import error: {e}")
    exit(1)
"@

$testScript | python
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ All critical imports successful!" -ForegroundColor Green
} else {
    Write-Host "⚠ Some imports failed. Check error messages above." -ForegroundColor Yellow
}

Write-Host "`n" + "="*50 -ForegroundColor Cyan
Write-Host "SETUP COMPLETE!" -ForegroundColor Green
Write-Host "="*50 -ForegroundColor Cyan

Write-Host "`nTo run the application:" -ForegroundColor Cyan
Write-Host "  streamlit run streamlit_app.py" -ForegroundColor White

Write-Host "`nTo activate virtual environment (if created):" -ForegroundColor Cyan
Write-Host "  .\streamlit_env\Scripts\Activate.ps1" -ForegroundColor White

Write-Host "`nIf you encounter issues:" -ForegroundColor Cyan
Write-Host "  1. Check the README.md for troubleshooting" -ForegroundColor White
Write-Host "  2. Ensure Tesseract OCR is installed and in PATH" -ForegroundColor White
Write-Host "  3. Run PowerShell as Administrator if needed" -ForegroundColor White

Write-Host "`nPress any key to continue..." -ForegroundColor Gray
$Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") | Out-Null