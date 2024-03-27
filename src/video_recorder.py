import cv2
import os

class VideoRecorder:
    def __init__(self, output_dir, fps=10.0, size=(960, 540), format="mp4v"):
        self.output_dir = output_dir
        self.fps = fps
        self.size = size
        self.format = format
        self._video_writer = None
        self.is_recording = False

    def start(self, file_name, sub_dir=None):
        if sub_dir is not None:
            output_dir = os.path.join(self.output_dir, sub_dir)
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
        else:
            output_dir = self.output_dir

        self.is_recording = True

        self._video_writer = cv2.VideoWriter(os.path.join(output_dir, file_name), self._fourcc(), self.fps, self.size)

    def _fourcc(self):
        codec = self.format
        return cv2.VideoWriter_fourcc(*codec)

    def write_frame(self, frame):
        if not self.is_recording:
            return
        
        frame = cv2.resize(frame, self.size)
        self._video_writer.write(frame)

    def release(self):
        self.is_recording = False
        self._video_writer.release()