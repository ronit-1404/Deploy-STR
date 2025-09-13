# test_live.py (MAC full version with sys.path fix)

import sys
import os

# Add shared directory to sys.path
shared_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../shared'))
sys.path.append(shared_path)

import time
from datetime import datetime
from mac_capture import capture_screen
from ocr import extract_text
from context import detect_context
from mac_window import get_active_app
from chrome_tab import get_chrome_tab_info
from sentiment import analyze_sentiment
from idle_tracker import get_idle_time  # Mac idle tracker (Quartz)

def run_analyzer(interval=5):
    print("\nLive Screen Analyzer - MacOS (Ctrl+C to stop)\n")

    last_context = None
    context_start_time = time.time()

    while True:
        timestamp = datetime.utcnow().isoformat()
        app = get_active_app()
        frame = capture_screen()
        text = extract_text(frame)
        context = detect_context(text)
        sentiment = analyze_sentiment(text)
        idle_seconds = get_idle_time()

        # YouTube tab detection (ONLY if Chrome active)
        title, url = None, None
        if app.lower() == "google chrome":
            title, url = get_chrome_tab_info()
            if url and "youtube.com/watch" in url:
                context = "video_lecture"

        # Context change duration tracking
        if context != last_context:
            if last_context:
                duration = time.time() - context_start_time
                print(f"--- Context '{last_context}' lasted {duration:.1f} seconds ---\n")
            last_context = context
            context_start_time = time.time()

        print("=========================================")
        print(f"[{timestamp}]")
        print(f"Active App: {app}")
        print(f"Detected Context: {context}")
        print(f"Sentiment: {sentiment}")
        print(f"Idle Time: {idle_seconds} sec")

        if title and url:
            print(f"Chrome Title: {title}")
            print(f"Chrome URL: {url}")

        print(f"Text Sample: {text[:150]}")
        print("=========================================\n")

        # Simple trigger logic
        if sentiment == "negative" and idle_seconds > 90:
            print("⚠️  User shows frustration with inactivity — Suggest break or intervention.\n")
        if context == "video_lecture" and idle_seconds > 120:
            print("⚠️  Possible passive watching — Suggest quick recap quiz.\n")

        time.sleep(interval)

if __name__ == "__main__":
    run_analyzer()
