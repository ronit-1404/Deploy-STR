from PIL import ImageGrab

def capture_screen():
    screenshot = ImageGrab.grab()
    return screenshot
