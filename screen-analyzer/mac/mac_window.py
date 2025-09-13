# mac_window.py
import subprocess

def get_active_app():
    script = 'tell application "System Events" to name of first process where frontmost is true'
    try:
        app_name = subprocess.check_output(['osascript', '-e', script]).decode('utf-8').strip()
        return app_name
    except Exception as e:
        return f"Unknown ({e})"
