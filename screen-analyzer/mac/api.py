# import os
# import sys
# import time
# from datetime import datetime
# import base64
# from io import BytesIO
# from PIL import Image
# import cv2
# import numpy as np
# from flask import Flask, request, jsonify
# from flask_cors import CORS

# # Add shared directory to sys.path
# shared_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../shared'))
# sys.path.append(shared_path)

# # Import Mac-specific modules
# from mac_capture import capture_screen
# from mac_window import get_active_app
# from idle_tracker import get_idle_time

# # Import shared modules
# try:
#     from ocr import extract_text
#     from context import detect_context
#     from sentiment import analyze_sentiment
#     from chrome_tab import get_chrome_tab_info
# except ImportError:
#     def extract_text(image):
#         return "Sample text extraction (OCR module not available)"
#     def detect_context(text):
#         return "unknown"
#     def analyze_sentiment(text):
#         return "neutral"
#     def get_chrome_tab_info():
#         return "Unknown Tab", "Unknown URL"

# app = Flask(__name__)
# CORS(app)  # Enable CORS for all routes

# # Store session data
# session_data = {
#     "start_time": time.time(),
#     "contexts": {},
#     "current_context": None,
#     "current_context_start": time.time(),
#     "last_context_duration": 0,
#     "context_log": [],
#     "screenshots": []
# }

# @app.route('/api/status', methods=['GET'])
# def get_status():
#     try:
#         timestamp = datetime.utcnow().isoformat()
#         app_name = get_active_app()
#         idle_seconds = get_idle_time()
#         title, url = None, None
#         if "chrome" in app_name.lower():
#             title, url = get_chrome_tab_info()
#         session_duration = time.time() - session_data["start_time"]
#         current_context_duration = 0
#         if session_data["current_context"]:
#             current_context_duration = time.time() - session_data["current_context_start"]
#         return jsonify({
#             "timestamp": timestamp,
#             "active_app": app_name,
#             "idle_time": idle_seconds,
#             "chrome_title": title,
#             "chrome_url": url,
#             "session_duration": session_duration,
#             "current_context": session_data["current_context"],
#             "context_duration": current_context_duration
#         })
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# @app.route('/api/analyze-screen', methods=['GET'])
# def analyze_screen():
#     try:
#         # Capture screen
#         screen = capture_screen()
#         text = extract_text(screen)
#         context = detect_context(text)
#         sentiment = analyze_sentiment(text)
#         img_display = Image.fromarray(cv2.cvtColor(screen, cv2.COLOR_BGR2RGB))
#         buffered = BytesIO()
#         img_display.save(buffered, format="JPEG", quality=30)
#         img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

#         # Get active app and Chrome tab info
#         app_name = get_active_app()
#         chrome_title, chrome_url = None, None
#         if "chrome" in app_name.lower():
#             chrome_title, chrome_url = get_chrome_tab_info()

#         # Get idle time
#         idle_seconds = get_idle_time()

#         # Track context changes and log
#         context_change_duration = 0
#         if session_data["current_context"] != context:
#             if session_data["current_context"]:
#                 duration = time.time() - session_data["current_context_start"]
#                 # Add to context durations
#                 if session_data["current_context"] in session_data["contexts"]:
#                     session_data["contexts"][session_data["current_context"]] += duration
#                 else:
#                     session_data["contexts"][session_data["current_context"]] = duration
#                 session_data["last_context_duration"] = duration
#                 context_change_duration = duration
#                 # Log the context switch
#                 session_data["context_log"].append({
#                     "context": session_data["current_context"],
#                     "duration": duration,
#                     "timestamp": datetime.utcnow().isoformat()
#                 })
#                 # Limit log size
#                 if len(session_data["context_log"]) > 10:
#                     session_data["context_log"].pop(0)
#             # Update current context
#             session_data["current_context"] = context
#             session_data["current_context_start"] = time.time()
#         else:
#             context_change_duration = session_data.get("last_context_duration", 0)

#         # Store screenshot (limited to last 5)
#         timestamp = datetime.utcnow().isoformat()
#         session_data["screenshots"].append({
#             "timestamp": timestamp,
#             "context": context,
#             "app": app_name
#         })
#         if len(session_data["screenshots"]) > 5:
#             session_data["screenshots"].pop(0)

#         # Generate insights
#         insights = []
#         if idle_seconds > 90:
#             insights.append("Long period of inactivity detected")
#         if sentiment == "negative":
#             insights.append("Negative sentiment detected in screen content")
#         if "youtube.com/watch" in text.lower():
#             insights.append("Video lecture or educational content detected")

#         return jsonify({
#             "timestamp": timestamp,
#             "screenshot": f"data:image/jpeg;base64,{img_base64}",
#             "text_sample": text[:500] + ("..." if len(text) > 500 else ""),
#             "context": context,
#             "sentiment": sentiment,
#             "active_app": app_name,
#             "idle_time": idle_seconds,
#             "insights": insights,
#             "chrome_title": chrome_title,
#             "chrome_url": chrome_url,
#             "context_change_duration": context_change_duration,
#             "context_log": session_data.get("context_log", [])
#         })
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# @app.route('/api/session-stats', methods=['GET'])
# def get_session_stats():
#     try:
#         contexts_with_current = dict(session_data["contexts"])
#         if session_data["current_context"]:
#             current_duration = time.time() - session_data["current_context_start"]
#             if session_data["current_context"] in contexts_with_current:
#                 contexts_with_current[session_data["current_context"]] += current_duration
#             else:
#                 contexts_with_current[session_data["current_context"]] = current_duration
#         context_list = [
#             {"context": k, "duration": v} 
#             for k, v in sorted(contexts_with_current.items(), key=lambda x: x[1], reverse=True)
#         ]
#         return jsonify({
#             "session_duration": time.time() - session_data["start_time"],
#             "context_durations": context_list,
#             "screenshot_history": session_data["screenshots"]
#         })
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# @app.route('/api/reset-session', methods=['POST'])
# def reset_session():
#     try:
#         session_data["start_time"] = time.time()
#         session_data["contexts"] = {}
#         session_data["current_context"] = None
#         session_data["current_context_start"] = time.time()
#         session_data["last_context_duration"] = 0
#         session_data["context_log"] = []
#         session_data["screenshots"] = []
#         return jsonify({
#             "success": True,
#             "message": "Session data reset successfully"
#         })
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# if __name__ == '__main__':
#     print("Screen Analysis API Server starting...")
#     print("Running on macOS")
#     app.run(debug=True, port=5001)

import os
import sys
import time
from datetime import datetime
import base64
from io import BytesIO
from PIL import Image
import cv2
import numpy as np
import json
from flask import Flask, request, jsonify
from flask_cors import CORS

# Add shared directory to sys.path
shared_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../shared'))
sys.path.append(shared_path)

# Import Mac-specific modules
from mac_capture import capture_screen
from mac_window import get_active_app
from idle_tracker import get_idle_time

# Import shared modules
try:
    from ocr import extract_text
    from context import detect_context
    from sentiment import analyze_sentiment
    from chrome_tab import get_chrome_tab_info
except ImportError:
    def extract_text(image):
        return "Sample text extraction (OCR module not available)"
    def detect_context(text):
        return "unknown"
    def analyze_sentiment(text):
        return "neutral"
    def get_chrome_tab_info():
        return "Unknown Tab", "Unknown URL"

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Store session data
session_data = {
    "start_time": time.time(),
    "contexts": {},
    "current_context": None,
    "current_context_start": time.time(),
    "last_context_duration": 0,
    "context_log": [],
    "screenshots": []
}

# Directory to save data
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'data')

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
        data['timestamp'] = datetime.now().isoformat()
        
        # Append new data
        existing_data.append(data)
        
        # Write updated data back to the file
        with open(file_path, 'w') as f:
            json.dump(existing_data, f, indent=2)
            
        return True
    except Exception as e:
        print(f"Error writing to JSON file: {e}")
        return False

@app.route('/api/status', methods=['GET'])
def get_status():
    try:
        timestamp = datetime.utcnow().isoformat()
        app_name = get_active_app()
        idle_seconds = get_idle_time()
        title, url = None, None
        if "chrome" in app_name.lower():
            title, url = get_chrome_tab_info()
        session_duration = time.time() - session_data["start_time"]
        current_context_duration = 0
        if session_data["current_context"]:
            current_context_duration = time.time() - session_data["current_context_start"]
            
        response_data = {
            "timestamp": timestamp,
            "active_app": app_name,
            "idle_time": idle_seconds,
            "chrome_title": title,
            "chrome_url": url,
            "session_duration": session_duration,
            "current_context": session_data["current_context"],
            "context_duration": current_context_duration
        }
        
        # Save to JSON file if userId is provided
        user_id = request.args.get('userId')
        if user_id:
            status_data = {
                'userId': user_id,
                'active_app': app_name,
                'idle_time': idle_seconds,
                'chrome_title': title,
                'chrome_url': url,
                'current_context': session_data["current_context"],
            }
            write_to_json_file('status', status_data)
            
        return jsonify(response_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# @app.route('/api/analyze-screen', methods=['GET'])
# def analyze_screen():
#     try:
#         # Capture screen
#         screen = capture_screen()
#         text = extract_text(screen)
#         context = detect_context(text)
#         sentiment = analyze_sentiment(text)
#         img_display = Image.fromarray(cv2.cvtColor(screen, cv2.COLOR_BGR2RGB))
#         buffered = BytesIO()
#         img_display.save(buffered, format="JPEG", quality=30)
#         img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

#         # Get active app and Chrome tab info
#         app_name = get_active_app()
#         chrome_title, chrome_url = None, None
#         if "chrome" in app_name.lower():
#             chrome_title, chrome_url = get_chrome_tab_info()

#         # Get idle time
#         idle_seconds = get_idle_time()

#         # Track context changes and log
#         context_change_duration = 0
#         if session_data["current_context"] != context:
#             if session_data["current_context"]:
#                 duration = time.time() - session_data["current_context_start"]
#                 # Add to context durations
#                 if session_data["current_context"] in session_data["contexts"]:
#                     session_data["contexts"][session_data["current_context"]] += duration
#                 else:
#                     session_data["contexts"][session_data["current_context"]] = duration
#                 session_data["last_context_duration"] = duration
#                 context_change_duration = duration
#                 # Log the context switch
#                 session_data["context_log"].append({
#                     "context": session_data["current_context"],
#                     "duration": duration,
#                     "timestamp": datetime.utcnow().isoformat()
#                 })
#                 # Limit log size
#                 if len(session_data["context_log"]) > 10:
#                     session_data["context_log"].pop(0)
#             # Update current context
#             session_data["current_context"] = context
#             session_data["current_context_start"] = time.time()
#         else:
#             context_change_duration = session_data.get("last_context_duration", 0)

#         # Store screenshot (limited to last 5)
#         timestamp = datetime.utcnow().isoformat()
#         session_data["screenshots"].append({
#             "timestamp": timestamp,
#             "context": context,
#             "app": app_name
#         })
#         if len(session_data["screenshots"]) > 5:
#             session_data["screenshots"].pop(0)

#         # Generate insights
#         insights = []
#         if idle_seconds > 90:
#             insights.append("Long period of inactivity detected")
#         if sentiment == "negative":
#             insights.append("Negative sentiment detected in screen content")
#         if "youtube.com/watch" in text.lower():
#             insights.append("Video lecture or educational content detected")
            
#         response_data = {
#             "timestamp": timestamp,
#             "screenshot": f"data:image/jpeg;base64,{img_base64}",
#             "text_sample": text[:500] + ("..." if len(text) > 500 else ""),
#             "context": context,
#             "sentiment": sentiment,
#             "active_app": app_name,
#             "idle_time": idle_seconds,
#             "insights": insights,
#             "chrome_title": chrome_title,
#             "chrome_url": chrome_url,
#             "context_change_duration": context_change_duration,
#             "context_log": session_data.get("context_log", [])
#         }

#         # Save to JSON file if userId is provided
#         user_id = request.args.get('userId')
#         if user_id:
#             screen_data = {
#                 'userId': user_id,
#                 'context': context,
#                 'sentiment': sentiment,
#                 'active_app': app_name,
#                 'idle_time': idle_seconds,
#                 'insights': insights,
#                 'chrome_title': chrome_title,
#                 'chrome_url': chrome_url
#             }
#             write_to_json_file('screen', screen_data)
            
#         return jsonify(response_data)
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500
@app.route('/api/analyze-screen', methods=['GET'])
def analyze_screen():
    try:
        # Get user_id from request args with a default value
        user_id = request.args.get('userId', 'unknown')
        
        # Capture screen
        screen = capture_screen()
        text = extract_text(screen)
        context = detect_context(text)
        sentiment = analyze_sentiment(text)
        img_display = Image.fromarray(cv2.cvtColor(screen, cv2.COLOR_BGR2RGB))
        buffered = BytesIO()
        img_display.save(buffered, format="JPEG", quality=30)
        img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

        # Get active app and Chrome tab info
        app_name = get_active_app()
        chrome_title, chrome_url = None, None
        if "chrome" in app_name.lower():
            chrome_title, chrome_url = get_chrome_tab_info()

        # Get idle time
        idle_seconds = get_idle_time()

        # Track context changes and log
        context_change_duration = 0
        if session_data["current_context"] != context:
            if session_data["current_context"]:
                duration = time.time() - session_data["current_context_start"]
                # Add to context durations
                if session_data["current_context"] in session_data["contexts"]:
                    session_data["contexts"][session_data["current_context"]] += duration
                else:
                    session_data["contexts"][session_data["current_context"]] = duration
                session_data["last_context_duration"] = duration
                context_change_duration = duration
                # Log the context switch
                session_data["context_log"].append({
                    "context": session_data["current_context"],
                    "duration": duration,
                    "timestamp": datetime.utcnow().isoformat()
                })
                # Limit log size
                if len(session_data["context_log"]) > 10:
                    session_data["context_log"].pop(0)
            # Update current context
            session_data["current_context"] = context
            session_data["current_context_start"] = time.time()
        else:
            context_change_duration = session_data.get("last_context_duration", 0)

        # Store screenshot (limited to last 5)
        timestamp = datetime.utcnow().isoformat()
        session_data["screenshots"].append({
            "timestamp": timestamp,
            "context": context,
            "app": app_name
        })
        if len(session_data["screenshots"]) > 5:
            session_data["screenshots"].pop(0)

        # Generate insights
        insights = []
        if idle_seconds > 90:
            insights.append("Long period of inactivity detected")
        if sentiment == "negative":
            insights.append("Negative sentiment detected in screen content")
        if "youtube.com/watch" in text.lower():
            insights.append("Video lecture or educational content detected")
            
        response_data = {
            "timestamp": timestamp,
            "screenshot": f"data:image/jpeg;base64,{img_base64}",
            "text_sample": text[:500] + ("..." if len(text) > 500 else ""),
            "context": context,
            "sentiment": sentiment,
            "active_app": app_name,
            "idle_time": idle_seconds,
            "insights": insights,
            "chrome_title": chrome_title,
            "chrome_url": chrome_url,
            "context_change_duration": context_change_duration,
            "context_log": session_data.get("context_log", [])
        }

        # Always save to screen.json file (not conditional on userId being provided)
        screen_data = {
            'userId': user_id,
            'context': context,
            'sentiment': sentiment,
            'active_app': app_name,
            'idle_time': idle_seconds,
            'insights': insights,
            'chrome_title': chrome_title,
            'chrome_url': chrome_url
        }
        write_to_json_file('screen', screen_data)
            
        return jsonify(response_data)
    except Exception as e:
        print(f"Error in analyze_screen: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/session-stats', methods=['GET'])
def get_session_stats():
    try:
        contexts_with_current = dict(session_data["contexts"])
        if session_data["current_context"]:
            current_duration = time.time() - session_data["current_context_start"]
            if session_data["current_context"] in contexts_with_current:
                contexts_with_current[session_data["current_context"]] += current_duration
            else:
                contexts_with_current[session_data["current_context"]] = current_duration
        context_list = [
            {"context": k, "duration": v} 
            for k, v in sorted(contexts_with_current.items(), key=lambda x: x[1], reverse=True)
        ]
        
        response_data = {
            "session_duration": time.time() - session_data["start_time"],
            "context_durations": context_list,
            "screenshot_history": session_data["screenshots"]
        }
        
        # Save to JSON file if userId is provided
        user_id = request.args.get('userId')
        if user_id:
            stats_data = {
                'userId': user_id,
                'session_duration': time.time() - session_data["start_time"],
                'context_durations': context_list
            }
            write_to_json_file('session_stats', stats_data)
            
        return jsonify(response_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/reset-session', methods=['POST'])
def reset_session():
    try:
        session_data["start_time"] = time.time()
        session_data["contexts"] = {}
        session_data["current_context"] = None
        session_data["current_context_start"] = time.time()
        session_data["last_context_duration"] = 0
        session_data["context_log"] = []
        session_data["screenshots"] = []
        
        # Save reset event to JSON if userId is provided
        user_id = request.json.get('userId') if request.json else None
        if user_id:
            reset_data = {
                'userId': user_id,
                'action': 'reset_session'
            }
            write_to_json_file('session_events', reset_data)
            
        return jsonify({
            "success": True,
            "message": "Session data reset successfully"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("Screen Analysis API Server starting...")
    print("Running on macOS")
    app.run(debug=True, port=5001)