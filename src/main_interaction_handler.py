from frame_image_saver import FrameImageSaver
from video_recorder import VideoRecorder
import time
import os
import json
import shutil
import uuid

class MainInteractionHandler:
  def __init__(self):
    self.frame_image_saver = FrameImageSaver("./interactions/")
    self.video_recorder = VideoRecorder("./interactions/")
    self.device_id = str(uuid.uuid4())
    self.interaction_files = []

  def on_interaction_ongoing(self, frame):
    self.video_recorder.write_frame(frame)

  def on_interaction_start(self, interaction_start_ts):
    start_ts = int(interaction_start_ts)
    sub_dir = f"{start_ts}/"
    file_name = f"{start_ts}.mp4"
    self.video_recorder.start(file_name, sub_dir)

  def on_interaction_roi_movement_stopped(self, frame, interaction_start_ts):
    start_ts = int(interaction_start_ts)
    sub_dir = f"{start_ts}/"
    file_name = f"{int(time.time())}.jpg"
    self.interaction_files.append(file_name)
    self.frame_image_saver.save(frame, file_name, sub_dir)

  def on_interaction_end(self, interaction_start_ts):
    ts = int(time.time())
    start_ts = int(interaction_start_ts)

    interaction_data = {
      "deviceId": self.device_id,
      "interactionId": str(start_ts),
      "startTime": start_ts,
      "endTime": ts
    }

    self.interaction_files.append(f"{start_ts}.mp4")

    manifest = {
      "files": self.interaction_files
    }

    if not os.path.exists(f"./interactions/{start_ts}/"):
      os.makedirs(os.path.dirname(f"./interactions/{start_ts}/"))

    with open(f"./interactions/{start_ts}/manifest.json", "w") as json_file:
      json.dump(manifest, json_file, indent=4)

    with open(f"./interactions/{start_ts}/metadata.json", "w") as json_file:
      json.dump(interaction_data, json_file, indent=4)

    self.video_recorder.release()

    shutil.copytree(f"./interactions/{start_ts}", f"./upload_queue/{start_ts}")
    shutil.rmtree(f"./interactions/{start_ts}")