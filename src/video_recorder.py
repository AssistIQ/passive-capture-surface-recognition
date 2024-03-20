import cv2

class VideoRecorder:
    def __init__(self, filename, fps=30.0, size=None, is_color=True, format="XVID", video_frame_width=1920, video_frame_height=1080):
        self.filename = filename
        self.fps = fps
        self.size = size
        self.is_color = is_color
        self.format = format
        self._video_writer = None

    def start(self):
        self._video_writer = cv2.VideoWriter(self.filename, self._fourcc(), self.fps, self.size, self.is_color)

    def _fourcc(self):
        codec = self.format
        return cv2.VideoWriter_fourcc(*codec)

    def write_frame(self, frame):
        cv2.resize(frame,(self.video_frame_width, self.video_frame_height))
        self._video_writer.write(frame)

    def release(self):
        self._video_writer.release()