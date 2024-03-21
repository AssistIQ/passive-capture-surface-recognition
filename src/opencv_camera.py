import cv2
import time
import logging as log

class OpenCVCamera:
    def __init__(self, camera_id=0, preview_size=(1920, 1080)):
        self.cap = None
        self.camera_id = camera_id
        self.width, self.height = preview_size

    def start(self):
        try:
            self.cap = cv2.VideoCapture(self.camera_id)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        except Exception as e:
            log.error(e)
            log.debug("Relaunching OpenCV camera...")
            time.sleep(5)
            self.start()
    
    def get_frame(self):
        _, frame = self.cap.read()
        return frame