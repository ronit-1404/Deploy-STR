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
# shared_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'shared'))
# sys.path.append(shared_path)

# # Import platform-specific modules based on OS
# import platform
# if platform.system() == "Windows":
#     from windows.win_capture import capture_screen
#     from windows.win_window import get_active_app
#     from windows.idle_tracker_win import get_idle_time
# else:  # macOS
#     from mac.mac_capture import capture_screen
#     from mac.mac_window import get_active_app
#     from mac.idle_tracker import get_idle_time

# # Import shared modules
# try:
#     from shared.ocr import extract_text
#     from shared.context import detect_context
#     from shared.sentiment import analyze_sentiment
#     from shared.chrome_tab import get_chrome_tab_info
# except ImportError:
#     # Fallback implementations if shared modules aren't available
#     def extract_text(image):
#         """Extract text from image using OCR"""
#         # Simplified implementation
#         return "Sample text extraction (OCR module not available)"
    
#     def detect_context(text):
#         """Detect the context from text"""
#         # Simplified implementation
#         contexts = ["coding", "reading", "video_lecture", "browsing", "writing", "unknown"]
#         # Just return a default value
#         return "unknown"
    
#     def analyze_sentiment(text):
#         """Analyze sentiment of text"""
#         # Simplified implementation
#         return "neutral"
    
#     def get_chrome_tab_info():
#         """Get Chrome tab info"""
#         # Simplified implementation
#         return "Unknown Tab", "Unknown URL"

# app = Flask(__name__)
# CORS(app)  # Enable CORS for all routes

# # Store session data
# session_data = {
#     "start_time": time.time(),
#     "contexts": {},
#     "current_context": None,
#     "current_context_start": time.time(),
#     "screenshots": []
# }

# @app.route('/api/status', methods=['GET'])
# def get_status():
#     """Get current system status"""
#     try:
#         timestamp = datetime.utcnow().isoformat()
#         app_name = get_active_app()
#         idle_seconds = get_idle_time()
        
#         # Chrome-specific info
#         title, url = None, None
#         if "chrome" in app_name.lower():
#             title, url = get_chrome_tab_info()
            
#         # Session duration
#         session_duration = time.time() - session_data["start_time"]
        
#         # Current context duration
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
#     """Capture and analyze current screen"""
#     try:
#         # Capture screen
#         screen = capture_screen()
        
#         # Convert to format suitable for OCR
#         if platform.system() == "Windows":
#             # Windows capture returns a PIL Image
#             img_np = np.array(screen)
#             img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
#             screen_for_ocr = img_bgr
#         else:
#             # Mac capture already returns a cv2/numpy array
#             screen_for_ocr = screen
            
#         # Extract text using OCR
#         text = extract_text(screen_for_ocr)
        
#         # Detect context
#         context = detect_context(text)
        
#         # Analyze sentiment
#         sentiment = analyze_sentiment(text)
        
#         # Convert screen to base64 for frontend display
#         # Convert to RGB for consistent display
#         if platform.system() == "Windows":
#             img_display = screen
#         else:
#             img_display = Image.fromarray(cv2.cvtColor(screen, cv2.COLOR_BGR2RGB))
        
#         buffered = BytesIO()
#         img_display.save(buffered, format="JPEG", quality=30)  # Lower quality for faster transfer
#         img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
        
#         # Track context changes
#         if session_data["current_context"] != context:
#             if session_data["current_context"]:
#                 duration = time.time() - session_data["current_context_start"]
#                 # Add to context durations
#                 if session_data["current_context"] in session_data["contexts"]:
#                     session_data["contexts"][session_data["current_context"]] += duration
#                 else:
#                     session_data["contexts"][session_data["current_context"]] = duration
            
#             # Update current context
#             session_data["current_context"] = context
#             session_data["current_context_start"] = time.time()
        
#         # Get active app
#         app_name = get_active_app()
        
#         # Get idle time
#         idle_seconds = get_idle_time()
        
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
#             "insights": insights
#         })
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# @app.route('/api/session-stats', methods=['GET'])
# def get_session_stats():
#     """Get current session statistics"""
#     try:
#         # Calculate current context duration and add to tracking
#         contexts_with_current = dict(session_data["contexts"])
#         if session_data["current_context"]:
#             current_duration = time.time() - session_data["current_context_start"]
#             if session_data["current_context"] in contexts_with_current:
#                 contexts_with_current[session_data["current_context"]] += current_duration
#             else:
#                 contexts_with_current[session_data["current_context"]] = current_duration
        
#         # Create sorted list of contexts by duration
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
#     """Reset the session data"""
#     try:
#         # Reset session data
#         session_data["start_time"] = time.time()
#         session_data["contexts"] = {}
#         session_data["current_context"] = None
#         session_data["current_context_start"] = time.time()
#         session_data["screenshots"] = []
        
#         return jsonify({
#             "success": True,
#             "message": "Session data reset successfully"
#         })
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# if __name__ == '__main__':
#     print("Screen Analysis API Server starting...")
#     print(f"Running on {platform.system()}")
#     app.run(debug=True, port=5001)  # Use port 5001 to avoid conflicts

from flask import Flask, request, jsonify
from flask_cors import CORS
import time
import platform
import json
import datetime
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Global variables to store session data
session_data = {
    "start_time": time.time(),
    "contexts": {},
    "current_context": None,
    "current_context_start": time.time(),
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

@app.route('/api/update-context', methods=['POST'])
def update_context():
    """Update the current context based on screen analysis"""
    try:
        data = request.json
        context = data.get('context', 'unknown')
        app_name = data.get('app_name', 'unknown')
        idle_seconds = data.get('idle_seconds', 0)
        user_id = data.get('userId', 'unknown')
        
        # Update context if changed
        if session_data["current_context"] != context and session_data["current_context"] is not None:
            # Calculate duration of the previous context
            duration = time.time() - session_data["current_context_start"]
            if session_data["current_context"] not in session_data["contexts"]:
                session_data["contexts"][session_data["current_context"]] = 0
            session_data["contexts"][session_data["current_context"]] += duration
            context_change_duration = duration
        else:
            context_change_duration = 0
            
        # Update current context
        session_data["current_context"] = context
        session_data["current_context_start"] = time.time()
        
        # Store screenshot info (limited to last 5)
        timestamp = datetime.now().isoformat()
        session_data["screenshots"].append({
            "timestamp": timestamp,
            "context": context,
            "app": app_name
        })
        if len(session_data["screenshots"]) > 5:
            session_data["screenshots"].pop(0)
            
        # Generate insights based on context and app
        insights = []
        if idle_seconds > 90:
            insights.append("Long period of inactivity detected")
        
        if "coding" in context.lower():
            insights.append("Coding session detected")
        elif "reading" in context.lower():
            insights.append("Reading session detected")
        
        # Sample response data
        response_data = {
            "status": "success",
            "context": context,
            "app_name": app_name,
            "idle_seconds": idle_seconds,
            "context_duration": {
                "current": 0,  # Will be calculated on next update
                "previous": context_change_duration
            },
            "insights": insights
        }
        
        # Save to JSON file
        screen_data = {
            'userId': user_id,
            'context': context,
            'app_name': app_name,
            'idle_seconds': idle_seconds,
            'insights': insights
        }
        write_to_json_file('screen', screen_data)
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/session-summary', methods=['GET'])
def session_summary():
    """Get a summary of the current session"""
    try:
        # Calculate the duration of the current context
        current_duration = time.time() - session_data["current_context_start"]
        
        # Create a copy of contexts that includes the current context
        contexts_with_current = session_data["contexts"].copy()
        if session_data["current_context"] is not None:
            if session_data["current_context"] in contexts_with_current:
                contexts_with_current[session_data["current_context"]] += current_duration
            else:
                contexts_with_current[session_data["current_context"]] = current_duration
                
        context_list = [
            {"context": k, "duration": v}
            for k, v in sorted(contexts_with_current.items(), key=lambda x: x[1], reverse=True)
        ]
        
        return jsonify({
            "session_duration": time.time() - session_data["start_time"],
            "context_durations": context_list,
            "screenshot_history": session_data["screenshots"]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/reset-session', methods=['POST'])
def reset_session():
    """Reset the session data"""
    try:
        # Reset session data
        session_data["start_time"] = time.time()
        session_data["contexts"] = {}
        session_data["current_context"] = None
        session_data["current_context_start"] = time.time()
        session_data["screenshots"] = []
        return jsonify({
            "success": True,
            "message": "Session data reset successfully"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("Screen Analysis API Server starting...")
    print(f"Running on {platform.system()}")
    app.run(debug=True, port=5001)  # Use port 5001 to avoid conflicts