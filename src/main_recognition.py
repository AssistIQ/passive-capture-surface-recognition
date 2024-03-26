from luxonis_camera import LuxonisCamera
from opencv_camera import OpenCVCamera
from frame_processor import FrameProcessor
from main_interaction_handler import MainInteractionHandler
import uuid
import argparse
import cv2

if __name__ == "__main__":
  # Get command line arguments for which camera to use, either "luxonis" or "opencv" followed by the camera id for OpenCV
  parser = argparse.ArgumentParser()
  parser.add_argument("--camera", help="The camera to use, either 'luxonis' or 'opencv'")
  parser.add_argument("--camera_id", help="The camera id to use for OpenCV", type=int)
  args = parser.parse_args()

  if args.camera == "luxonis":
    camera = LuxonisCamera()
  elif args.camera == "opencv":
    if args.camera_id is None:
      print("OpenCV camera requires a camera id")
      exit(1)
    camera = OpenCVCamera(args.camera_id)
  else:
    print("Invalid camera type")
    exit(1)

  interaction_handler = MainInteractionHandler(device_id=str(uuid.uuid4()))
  processor = FrameProcessor(
    roi_size=(1000, 500),
    roi_position=(100, 200),
    on_interaction_roi_movement_stopped=interaction_handler.handle_interaction_roi_movement_stopped,
    on_interaction_end=interaction_handler.handle_interaction_end
  )

  camera.start()

  while True:
    frame = camera.get_frame()

    if frame is None:
      continue
    
    frame = processor.process(frame)
    cv2.imshow("Frame", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
      break
  
  # Clean up
  cv2.destroyAllWindows()