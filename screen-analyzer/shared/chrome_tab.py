# chrome_tab.py

import subprocess

def get_chrome_tab_info():
    try:
        script = '''
        tell application "Google Chrome"
            if not (exists window 1) then return {"", ""}
            set tabTitle to title of active tab of front window
            set tabURL to URL of active tab of front window
            return {tabTitle, tabURL}
        end tell
        '''
        result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
        output = result.stdout.strip().split(", ")
        if len(output) == 2:
            title = output[0].strip().replace('"', '')
            url = output[1].strip().replace('"', '')
            return title, url
    except Exception as e:
        print(f"Chrome tab fetch error: {e}")
    return None, None
