import cv2
import os

class FrameImageSaver:
    def __init__(self, output_dir):
        self.output_dir = output_dir

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def save(self, frame, file_name, sub_dir=None):
        if sub_dir is not None:
            output_dir = os.path.join(self.output_dir, sub_dir)
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
        else:
            output_dir = self.output_dir

        cv2.imwrite(os.path.join(output_dir, file_name), frame)