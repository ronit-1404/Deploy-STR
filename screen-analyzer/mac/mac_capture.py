# mac_capture.py
from PIL import ImageGrab
import numpy as np
import cv2

def capture_screen():
    img = ImageGrab.grab()
    img_np = np.array(img)
    img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
    return img_bgr
