import time
import cv2
import numpy as np
import mediapipe as mp
from models.point import Point
from models.polygon import Polygon

class FrameProcessor:
    def __init__(self, roi_size=(3000, 1700), roi_position=(600, 100)):
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(detectShadows=True)
        # https://developers.google.com/mediapipe/solutions/vision/hand_landmarker
        self.joint_list = [2,3,4,8,7,6,12,11,10,16,15,14,20,19,18]

        self.roi_width = roi_size[0]
        self.roi_height = roi_size[1]

        self.roi_polygon = self.init_roi_polygon(roi_size, roi_position)

        # center of roi polygon using self.roi_polygon
        center_x = self.roi_polygon.points[0].x + (self.roi_width / 2)
        center_y = self.roi_polygon.points[0].y + (self.roi_height / 2)
        self.roi_center = Point(center_x, center_y)

        # Constants
        self.HANDS_ABSENCE_THRESHOLD_SECONDS = 5
        self.INTERACTION_END_THRESHOLD_FRAMES = 10
        self.CHANGE_IN_ROI_MASK_THRESHOLD = 0.05

        self.interaction_start_ts = None
        self.is_interaction_started = False
        self.last_movement_ts = None

        self.frames_without_movement = 0

        mp_hands = mp.solutions.hands
        self.hands = mp_hands.Hands()

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


    def process(self, frame):
        mask = self.bg_subtractor.apply(frame)
        # Filter out shadows
        _, mask = cv2.threshold(mask, 250, 255, cv2.THRESH_BINARY)
        mask = cv2.erode(mask, None, iterations=1)
        mask = cv2.dilate(mask, None, iterations=2)
        
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # draw roi polygon on frame
        self.roi_polygon.draw(frame)

        is_hand_inside_roi = self.check_hand_in_roi(rgb_frame)

        self.roi_contains_movement(mask)
        
        if is_hand_inside_roi:
            self.last_movement_ts = time.time()
            if not self.is_interaction_started:
                self.is_interaction_started = True
                self.interaction_start_ts = time.time()
                print("Interaction started")
            else:
                self.interaction_start_ts = time.time()
                print("Interaction updated")
        else:
            current_ts = time.time()
            if self.is_interaction_started and (current_ts - self.last_movement_ts) > self.HANDS_ABSENCE_THRESHOLD_SECONDS: 
                print("No hands detected for 5 seconds")  
                if self.roi_contains_movement(mask):
                    self.frames_without_movement = 0
                    print("movement still detected")
                else:
                    self.frames_without_movement += 1
                    print('waiting for frame to stay still')
                    if self.frames_without_movement > self.INTERACTION_END_THRESHOLD_FRAMES:
                        print("roi has no movement, end interaction")
                        self.last_movement_ts = None
                        self.frames_without_movement = 0
                        self.is_interaction_started = False
            
        return frame 
    
    def check_hand_in_roi(self, frame):
        hand_detection_results = self.hands.process(frame)

        if not hand_detection_results.multi_hand_landmarks:
            return False

        is_hand_inside_roi = False  
        for landmarks in hand_detection_results.multi_hand_landmarks:
            self.draw_hand(frame, landmarks)
            is_hand_inside_roi = self.check_hand_inside_roi(frame, landmarks)
            if is_hand_inside_roi:
                break

        if is_hand_inside_roi:
            cv2.putText(frame, "Hand inside roi", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

        return is_hand_inside_roi


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

    def check_hand_inside_roi(self, frame, landmarks):
        frame_height, frame_width, _ = frame.shape
        # use thumb tip (4)
        thumb_tip = landmarks.landmark[4]
        tip = Point(int(thumb_tip.x * frame_width), int(thumb_tip.y * frame_height))

        return self.roi_polygon.contains(tip)

    def draw_hand(self, frame, landmarks):
        frame_height, frame_width, _ = frame.shape
        for joint in self.joint_list:
                joint_x = int(landmarks.landmark[joint].x * frame_width)
                joint_y = int(landmarks.landmark[joint].y * frame_height)
                cv2.circle(frame, (joint_x, joint_y), 5, (255, 0, 0), -1)
