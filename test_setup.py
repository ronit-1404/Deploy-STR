#!/usr/bin/env python3
"""
Test script for Streamlit Engagement Monitor
This script validates that all components can be imported and basic functionality works
"""

import sys
import importlib
from pathlib import Path

def test_imports():
    """Test critical imports"""
    print("Testing critical imports...")
    
    # Core dependencies
    modules_to_test = [
        'streamlit',
        'pandas', 
        'numpy',
        'plotly.graph_objects',
        'plotly.express',
        'time',
        'datetime',
        'pathlib'
    ]
    
    failed_imports = []
    
    for module in modules_to_test:
        try:
            importlib.import_module(module)
            print(f"✓ {module}")
        except ImportError as e:
            print(f"✗ {module}: {e}")
            failed_imports.append(module)
    
    # Audio dependencies
    print("\nTesting audio dependencies...")
    audio_modules = ['pyaudio', 'librosa', 'joblib', 'sklearn']
    
    for module in audio_modules:
        try:
            importlib.import_module(module)
            print(f"✓ {module}")
        except ImportError as e:
            print(f"✗ {module}: {e}")
            failed_imports.append(module)
    
    # Screen analysis dependencies  
    print("\nTesting screen analysis dependencies...")
    screen_modules = ['cv2', 'pytesseract', 'PIL', 'spacy', 'vaderSentiment']
    
    for module in screen_modules:
        try:
            if module == 'PIL':
                importlib.import_module('PIL.Image')
            else:
                importlib.import_module(module)
            print(f"✓ {module}")
        except ImportError as e:
            print(f"✗ {module}: {e}")
            failed_imports.append(module)
    
    return failed_imports

def test_file_structure():
    """Test that required files exist"""
    print("\nTesting file structure...")
    
    current_dir = Path(__file__).parent
    
    required_files = [
        'streamlit_app.py',
        'requirements.txt',
        'README.md',
        'setup.ps1',
        '.streamlit/config.toml',
        'components/audio_monitor.py',
        'components/screen_monitor.py'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        full_path = current_dir / file_path
        if full_path.exists():
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path}")
            missing_files.append(file_path)
    
    return missing_files

def test_model_files():
    """Test that model files exist"""
    print("\nTesting model files...")
    
    current_dir = Path(__file__).parent
    model_files = [
        'audio_engage/emotion_detection_model.joblib'
    ]
    
    missing_models = []
    
    for model_path in model_files:
        full_path = current_dir / model_path
        if full_path.exists():
            print(f"✓ {model_path}")
        else:
            print(f"⚠ {model_path} (can be trained)")
            missing_models.append(model_path)
    
    return missing_models

def test_components():
    """Test component imports"""
    print("\nTesting component imports...")
    
    # Add components to path
    current_dir = Path(__file__).parent
    components_path = current_dir / "components"
    sys.path.append(str(components_path))
    
    try:
        from audio_monitor import StreamlitAudioProcessor
        print("✓ AudioProcessor can be imported")
    except Exception as e:
        print(f"✗ AudioProcessor: {e}")
        return False
    
    try:
        from screen_monitor import StreamlitScreenProcessor
        print("✓ ScreenProcessor can be imported")
    except Exception as e:
        print(f"✗ ScreenProcessor: {e}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("="*50)
    print("STREAMLIT ENGAGEMENT MONITOR - VALIDATION TEST")
    print("="*50)
    
    # Test imports
    failed_imports = test_imports()
    
    # Test file structure
    missing_files = test_file_structure()
    
    # Test model files
    missing_models = test_model_files()
    
    # Test components
    components_ok = test_components()
    
    # Summary
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    
    if not failed_imports and not missing_files and components_ok:
        print("✓ ALL TESTS PASSED!")
        print("\nYou can run the application with:")
        print("  streamlit run streamlit_app.py")
    else:
        print("⚠ SOME TESTS FAILED:")
        
        if failed_imports:
            print(f"\nFailed imports: {', '.join(failed_imports)}")
            print("Run: pip install -r requirements.txt")
        
        if missing_files:
            print(f"\nMissing files: {', '.join(missing_files)}")
            print("Ensure all files are in the correct location")
        
        if missing_models:
            print(f"\nMissing models: {', '.join(missing_models)}")
            print("Train the emotion model with: python audio_engage/train_emotion_model.py")
        
        if not components_ok:
            print("\nComponent import failed")
            print("Check component files and dependencies")
    
    print("\nFor detailed setup instructions, see README.md")

if __name__ == "__main__":
    main()