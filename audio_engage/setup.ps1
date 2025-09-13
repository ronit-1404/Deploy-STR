# This script will set up the environment for the Audio Emotion Detection project

# Check if the script is being run with administrative privileges
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Warning "This script should be run as Administrator to ensure proper installation. Please restart as Administrator."
    Write-Host "Press any key to continue anyway, or Ctrl+C to exit"
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

Write-Host "Setting up Audio Emotion Detection environment..." -ForegroundColor Green

# Check if Python is installed
$pythonPath = where.exe python 2>$null
if (-not $pythonPath) {
    Write-Host "Python not found. Please install Python 3.8 or newer." -ForegroundColor Red
    exit 1
}

# Get the script directory
$scriptPath = $PSScriptRoot
if (-not $scriptPath) {
    $scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
}

# Create a virtual environment
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
$venvPath = Join-Path $scriptPath "venv"
python -m venv $venvPath

# Activate the virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& "$venvPath\Scripts\Activate.ps1"

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
$scriptPath = $PSScriptRoot
if (-not $scriptPath) {
    $scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
}
$requirementsPath = Join-Path $scriptPath "requirements.txt"
Write-Host "Using requirements file at: $requirementsPath" -ForegroundColor Yellow
pip install -r $requirementsPath

# Check for PyAudio installation issues
$pyaudioCheck = pip list | Select-String -Pattern "pyaudio"
if (-not $pyaudioCheck) {
    Write-Host "PyAudio installation failed. This is common on Windows." -ForegroundColor Yellow
    Write-Host "Attempting to install from wheel file..." -ForegroundColor Yellow
    
    # Detect Python version
    $pythonVersion = python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
    $pythonVersion = $pythonVersion.Trim()
    
    Write-Host "Detected Python version: $pythonVersion" -ForegroundColor Yellow
    
    # Determine system architecture
    $is64bit = [Environment]::Is64BitOperatingSystem
    $arch = if ($is64bit) { "amd64" } else { "win32" }
    
    Write-Host "System architecture: $arch" -ForegroundColor Yellow
    
    Write-Host "Please download the appropriate PyAudio wheel file from:" -ForegroundColor Cyan
    Write-Host "https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio" -ForegroundColor Cyan
    $pyVer = $pythonVersion.Replace('.', '')
    Write-Host "Look for a file like: PyAudio-0.2.11-cp$pyVer-cp$pyVer-win_$arch.whl" -ForegroundColor Cyan
    
    $wheelPath = Read-Host -Prompt "Enter the path to the downloaded wheel file, or press Enter to skip"
    
    if ($wheelPath -and (Test-Path $wheelPath)) {
        pip install $wheelPath
        Write-Host "PyAudio installed successfully from wheel file." -ForegroundColor Green
    } else {
        Write-Host "PyAudio installation skipped. Audio recording functionality will not work." -ForegroundColor Yellow
    }
}

Write-Host "Environment setup completed!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Download a dataset like RAVDESS or CREMA-D" -ForegroundColor Cyan
Write-Host "2. Train the model: python train_emotion_model.py" -ForegroundColor Cyan
Write-Host "3. Run the API server: python api_server.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "For more information, refer to the README.md file." -ForegroundColor Cyan
