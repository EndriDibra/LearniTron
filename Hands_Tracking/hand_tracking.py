# importing libraries
import cv2 
import mediapipe as mp


# this class serves for hand detection
class Hand_Detector:
    
    # initializing parameters/values to vartiables with a constructor
    def __init__(self, mode=False, max_hands=2, detection_con=int(0.5), track_con=int(0.5)):
    
        self.mode = mode
        self.max_hands = max_hands
        self.detection_con = detection_con
        self.track_con = track_con

        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(self.mode, self.max_hands, self.detection_con, self.track_con)
        self.mp_draw = mp.solutions.drawing_utils

    # finding hands, maximum two hands, and capturing them 
    def find_hands(self, frame, draw=True):
       
        # transforming image to RGB mode
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        self.results = self.hands.process(frame_rgb)

        if self.results.multi_hand_landmarks:
           
            for hand_landmarks in self.results.multi_hand_landmarks:
                
                if draw:
                
                    self.mp_draw.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
        return frame

    # finding the position of maximum two hands and
    # capturing them with designed dots
    def find_position(self, frame, hand_no=0, draw=True):
        
        lm_list = []
        
        if self.results.multi_hand_landmarks:
        
            hand = self.results.multi_hand_landmarks[hand_no]
        
            for id, lm in enumerate(hand.landmark):
        
                height, weight, c = frame.shape
                
                cx, cy = int(lm.x * weight), int(lm.y * height)
        
                lm_list.append([id, cx, cy])
        
                if draw:
         
                    cv2.circle(frame, (cx, cy), 5, (255, 0, 255), cv2.FILLED)
        
        return lm_list

    # counting how many fingers, users have raised
    def count_fingers(self, lm_list):
       
        finger_tip_ids = [4, 8, 12, 16, 20]
       
        fingers = 0
       
        # Thumb
        if lm_list[4][1] < lm_list[3][1]:
            
            fingers += 1
       
        # Other fingers
        for id in range(1, 5):
       
            if lm_list[finger_tip_ids[id]][2] < lm_list[finger_tip_ids[id] - 2][2]:
                
                fingers += 1
        
        return fingers

# main function, which will run the process and
# display the results [Hand tracking and fingers counting]
def main():
   
    # using the default camera
    camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    
    # creating and object/instance of class:Hand_Detector
    detector = Hand_Detector()
   
    while camera.isOpened():
   
        success, frame = camera.read()

        # checking if camera works
        if not success:

            print("Error! Camera did not open.")

        # detecting hands in each frame from the camera
        frame = detector.find_hands(frame)

        # finding the position of the maximum two hands
        lm_list = detector.find_position(frame)

        # checking if there are any hands
        if len(lm_list) != 0:
            
            # counting how many fingers are raised per frame
            fingers = detector.count_fingers(lm_list)

            # based on fingers number
            # an according action will be performed
   
            print("Number of fingers:", fingers)
    
            cv2.putText(frame, f"Fingers: {int(fingers)}", (10, 70), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)

        # displaying the final frame
        cv2.imshow("Image", frame)
        
        # stoping process by pressing letter/key q:quit
        if cv2.waitKey(1) & 0xFF == ord("q"):
            
            break

    # closing all opened frames/windows    
    cv2.destroyAllWindows()
    camera.release()

# performing main function
main()
