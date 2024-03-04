import depthai as dai
import time
import logging as log

class LuxonisCamera:
    def __init__(self):
        self.output_capture = None
        self.camera_fps = 10
        self.sharpness = 4
        self.luma_denoise = 4
        self.chroma_denoise = 4
        self.preview_size = (3840, 2160)
        self.interleaved = False

    def start(self):
        try:
            pipeline = self.setup_camera()
            with dai.Device(pipeline) as device:
                self.output_capture = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)
        except Exception as e:
            log.error(e)
            log.debug("Relaunching luxonis camera...")
            time.sleep(5)
            self.start()

    def get_frame(self):
        try:
            frame = self.output_capture.get().getCvFrame()
            return frame
        except Exception as e:
            log.error(e)
            return None

    def setup_camera(self):
        pipeline = dai.Pipeline()
        camRgb = self.pipeline.create(dai.node.ColorCamera)
        xoutRgb = self.pipeline.create(dai.node.XLinkOut)
        xoutRgb.setStreamName("rgb")
        camRgb.initialControl.setSharpness(self.sharpness)
        camRgb.initialControl.setLumaDenoise(self.luma_denoise)
        camRgb.initialControl.setChromaDenoise(self.chroma_denoise)
        camRgb.setFps(self.camera_fps)
        camRgb.setPreviewSize(*self.preview_size)
        camRgb.setInterleaved(self.interleaved)
        camRgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_4_K)
        camRgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.RGB)
        camRgb.preview.link(self.xoutRgb.input)

        return pipeline
