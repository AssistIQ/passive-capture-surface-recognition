import cv2
import numpy as np
import mediapipe as mp
from models.point import Point
from models.polygon import Polygon

class FrameProcessor:
    def __init__(self, roi_size=(3000, 1700), roi_position=(600, 100)):
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2()
        # https://developers.google.com/mediapipe/solutions/vision/hand_landmarker
        self.joint_list = [2,3,4,8,7,6,12,11,10,16,15,14,20,19,18]

        self.roi_width = roi_size[0]
        self.roi_height = roi_size[1]

        self.roi_polygon = self.init_roi_polygon(roi_size, roi_position)

        # center of roi polygon using self.roi_polygon
        center_x = self.roi_polygon.points[0].x + (self.roi_width / 2)
        center_y = self.roi_polygon.points[0].y + (self.roi_height / 2)
        self.roi_center = Point(center_x, center_y)

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
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        mask = self.bg_subtractor.apply(gray)
        mask = cv2.threshold(mask, 225, 255, cv2.THRESH_BINARY)[1]

        kernel = np.ones((5,5),np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        hand_detection_results = self.hands.process(rgb_frame)

        # draw roi rectangle on frame where points is a Point class
        self.roi_polygon.draw(frame)

        if not hand_detection_results.multi_hand_landmarks:
            return
        
        is_hand_inside_roi = False
        for landmarks in hand_detection_results.multi_hand_landmarks:
            self.draw_hand(frame, landmarks)
            is_hand_inside_roi = self.check_hand_inside_roi(frame, landmarks)
            if is_hand_inside_roi:
                break

        if is_hand_inside_roi:
            cv2.putText(frame, "Hand inside roi", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
        self.handle_interaction(is_hand_inside_roi)
        
        return frame
    
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

    def start_interaction(self):
        self.is_session_started = True
        pass

    def update_interaction(self):
        pass

    def end_interaction(self):
        self.is_session_started = False
        pass

    def handle_interaction(self, is_hand_inside_roi):
        pass
