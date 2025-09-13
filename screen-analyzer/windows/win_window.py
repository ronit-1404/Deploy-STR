import win32gui

def get_active_app():
    window = win32gui.GetForegroundWindow()
    app_name = win32gui.GetWindowText(window)
    return app_name if app_name else "Unknown"
