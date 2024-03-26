from frame_image_saver import FrameImageSaver
import time
import os
import json
import shutil

class MainInteractionHandler:
  def __init__(self, device_id):
    self.frame_image_saver = FrameImageSaver("./interactions/")
    self.device_id = device_id
    self.interaction_files = []

  def handle_interaction_roi_movement_stopped(self, frame, interaction_start_ts):
    start_ts = int(interaction_start_ts)
    sub_dir = f"{start_ts}/"
    file_name = f"{int(time.time())}.jpg"
    self.interaction_files.append(file_name)
    self.frame_image_saver.save(frame, file_name, sub_dir)

  def handle_interaction_end(self, interaction_start_ts):
    ts = int(time.time())
    start_ts = int(interaction_start_ts)

    interaction_data = {
      "deviceId": self.device_id,
      "interactionId": str(start_ts),
      "startTime": start_ts,
      "endTime": ts
    }
    manifest = {
      "files": self.interaction_files
    }

    if not os.path.exists(f"./interactions/{start_ts}/"):
      os.makedirs(os.path.dirname(f"./interactions/{start_ts}/"))

    with open(f"./interactions/{start_ts}/manifest.json", "w") as json_file:
      json.dump(manifest, json_file, indent=4)

    with open(f"./interactions/{start_ts}/metadata.json", "w") as json_file:
      json.dump(interaction_data, json_file, indent=4)

    shutil.copytree(f"./interactions/{start_ts}", f"./upload_queue/{start_ts}")
    shutil.rmtree(f"./interactions/{start_ts}")