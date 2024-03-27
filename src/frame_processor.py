import time
import cv2
import numpy as np
import mediapipe as mp
from models.point import Point
from models.polygon import Polygon
from main_interaction_handler import MainInteractionHandler

class FrameProcessor():
    def __init__(self, roi_size=(3000, 1700), roi_position=(600, 100), interaction_handler=MainInteractionHandler()):
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(detectShadows=True)
        self.joint_list = [2,3,4,8,7,6,12,11,10,16,15,14,20,19,18]  # Hand landmarks
        self.hands = mp.solutions.hands.Hands()
        self.interaction_handler = interaction_handler

        self.roi_width = roi_size[0]
        self.roi_height = roi_size[1]
        self.roi_polygon = self.init_roi_polygon(roi_size, roi_position)
        center_x = self.roi_polygon.points[0].x + (self.roi_width / 2)
        center_y = self.roi_polygon.points[0].y + (self.roi_height / 2)
        self.roi_center = Point(center_x, center_y)

        self.HANDS_ABSENCE_THRESHOLD_SECONDS = 5
        self.INTERACTION_END_THRESHOLD_FRAMES = 10
        self.CHANGE_IN_ROI_MASK_THRESHOLD = 0.01

        self.interaction_start_ts = None
        self.is_interaction_started = False
        self.last_movement_ts = None
        self.frames_without_movement = 0

    def init_roi_polygon(self, roi_size, roi_position):
        roi_x_pos = roi_position[0]
        roi_y_pos = roi_position[1]
        width = roi_size[0]
        height = roi_size[1]

        right_x_pos = roi_x_pos + width
        bottom_y_pos = roi_y_pos + height

        # array of Points in clockwise order
        return Polygon([
            Point(roi_x_pos, roi_y_pos),
            Point(right_x_pos, roi_y_pos),
            Point(right_x_pos, bottom_y_pos),
            Point(roi_x_pos, bottom_y_pos)
        ])

    def reset_interaction(self):
        self.is_interaction_started = False
        self.interaction_start_ts = None
        self.last_movement_ts = None
        self.frames_without_movement = 0

    def process(self, frame):
        current_ts = time.time()
        mask = self.bg_subtractor.apply(frame)
        mask = self.filter_out_shadows(mask)
        mask = self.erode_and_dilate(mask)

        self.interaction_handler.on_interaction_ongoing(frame)

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        if self.is_hand_detected_in_roi(rgb_frame):
            self.handle_hand_inside_roi(current_ts)
        else:
            self.handle_hand_outside_roi(current_ts, mask, frame)

        return frame

    def filter_out_shadows(self, mask):
        _, mask = cv2.threshold(mask, 250, 255, cv2.THRESH_BINARY)
        return mask

    def erode_and_dilate(self, mask):
        mask = cv2.erode(mask, None, iterations=1)
        mask = cv2.dilate(mask, None, iterations=2)
        return mask

    def handle_hand_inside_roi(self, current_ts):
        self.last_movement_ts = current_ts
        if not self.is_interaction_started:
            self.is_interaction_started = True
            self.interaction_start_ts = current_ts
            self.interaction_handler.on_interaction_start(self.interaction_start_ts)
            print("Interaction started")
        else:
            self.interaction_start_ts = current_ts
            print("Interaction updated")

    def handle_hand_outside_roi(self, current_ts, mask, frame):
        if self.is_interaction_started and current_ts - self.last_movement_ts > self.HANDS_ABSENCE_THRESHOLD_SECONDS: 
            if self.roi_contains_movement(mask):
                self.frames_without_movement = 0
                print("movement still detected")
            else:
                self.handle_no_movement_in_roi(frame)

    def handle_no_movement_in_roi(self, frame):
        if self.frames_without_movement == 0:
            self.interaction_handler.on_interaction_roi_movement_stopped(frame, self.interaction_start_ts)

        self.frames_without_movement += 1
        if self.frames_without_movement > self.INTERACTION_END_THRESHOLD_FRAMES:
            print("roi has no movement, end interaction")
            self.interaction_handler.on_interaction_end(self.interaction_start_ts)
            self.reset_interaction()
            
    
    def is_hand_detected_in_roi(self, frame):
        hand_detection_results = self.hands.process(frame)

        if not hand_detection_results.multi_hand_landmarks:
            return False

        is_hand_inside_roi = False  
        for landmarks in hand_detection_results.multi_hand_landmarks:
            self.draw_hand(frame, landmarks)
            is_hand_inside_roi = self.is_thumb_tip_inside_roi(frame, landmarks)
            if is_hand_inside_roi:
                break

        return is_hand_inside_roi
    
    def is_thumb_tip_inside_roi(self, frame, landmarks):
        frame_height, frame_width, _ = frame.shape
        # use thumb tip (4)
        thumb_tip = landmarks.landmark[4]
        tip = Point(int(thumb_tip.x * frame_width), int(thumb_tip.y * frame_height))

        return self.roi_polygon.contains(tip)

    def roi_contains_movement(self, mask):
        roi_x1 = self.roi_polygon.points[0].x
        roi_y1 = self.roi_polygon.points[0].y
        roi_x2 = self.roi_polygon.points[2].x
        roi_y2 = self.roi_polygon.points[2].y

        roi_mask = mask[roi_y1:roi_y2, roi_x1:roi_x2]
        movement_area = np.sum(roi_mask) // 255
        mask_area = self.roi_width * self.roi_height
        change_in_roi = movement_area / mask_area

        return change_in_roi > self.CHANGE_IN_ROI_MASK_THRESHOLD

    def draw_hand(self, frame, landmarks):
        frame_height, frame_width, _ = frame.shape
        for joint in self.joint_list:
                joint_x = int(landmarks.landmark[joint].x * frame_width)
                joint_y = int(landmarks.landmark[joint].y * frame_height)
                cv2.circle(frame, (joint_x, joint_y), 5, (255, 0, 0), -1)
