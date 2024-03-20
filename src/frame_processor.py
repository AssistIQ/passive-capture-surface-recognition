import cv2
import numpy as np
import mediapipe as mp

class FrameProcessor:
    def __init__(self):
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2()
        # https://developers.google.com/mediapipe/solutions/vision/hand_landmarker
        self.joint_list = [2,3,4,8,7,6,12,11,10,16,15,14,20,19,18]
        self.inside_roi = False

        mp_hands = mp.solutions.hands
        self.hands = mp_hands.Hands()

    def process(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        mask = self.bg_subtractor.apply(gray)
        mask = cv2.threshold(mask, 225, 255, cv2.THRESH_BINARY)[1]

        kernel = np.ones((5,5),np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        hand_detection_results = self.hands.process(rgb_frame)

        if not hand_detection_results.multi_hand_landmarks:
            return
        
        for landmarks in hand_detection_results.multi_hand_landmarks:
            joint_positions = []
            for joint in self.joint_list:
                joint_positions.append((landmarks.landmark[joint].x, landmarks.landmark[joint].y))
            self.draw_hand(frame, joint_positions)
        
        return frame

    def draw_hand(self, frame, joint_positions):
        for joint in joint_positions:
            x, y = joint
            x = int(x * frame.shape[1])
            y = int(y * frame.shape[0])
            cv2.circle(frame, (x, y), 5, (0, 0, 255), -1)

            if self.inside_roi:
                cv2.putText(frame, "Hand detected", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
            else:
                cv2.putText(frame, "No hand detected", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

