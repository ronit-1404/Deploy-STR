# test_live.py (Windows full version with sys.path fix)

import sys
import os

# Add shared directory to sys.path
shared_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../shared'))
sys.path.append(shared_path)

import time
from datetime import datetime

from win_capture import capture_screen
from win_window import get_active_app
from idle_tracker_win import get_idle_time

from ocr import extract_text
from context import detect_context
from sentiment import analyze_sentiment
from chrome_tab import get_chrome_tab_info

def run_analyzer(interval=5):
    print("\nLive Screen Analyzer - Windows (Ctrl+C to stop)\n")

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

        title, url = None, None
        if "chrome" in app.lower():
            title, url = get_chrome_tab_info()

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

        if sentiment == "negative" and idle_seconds > 90:
            print("⚠️  Frustration detected. Suggest break or support intervention.\n")

        time.sleep(interval)

if __name__ == "__main__":
    run_analyzer()
