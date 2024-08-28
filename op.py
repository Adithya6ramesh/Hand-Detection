import cv2
import mediapipe as mp
import math
import time

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils
cap = cv2.VideoCapture(0)

square=0
cube=0

entered_number = ""  # String to store the concatenated number
last_detection_time = time.time()  
delay_seconds = 2  # Set delay time to 2 seconds

def is_c_gesture(landmarks):
   
    thumb_tip = landmarks[4]
    thumb_ip = landmarks[3]
    thumb_mcp = landmarks[2]

   
    index_tip = landmarks[8]
    index_dip = landmarks[7]
    index_pip = landmarks[6]

    # Check thumb curve and proximity to index finger
    thumb_curved = thumb_tip.x < thumb_ip.x < thumb_mcp.x
    thumb_near_index = calculate_distance(thumb_tip, index_tip) < 0.1

    # Check index finger curved shape
    index_curved = index_tip.y > index_dip.y > index_pip.y

    # Check for a fist shape
    if thumb_curved and thumb_near_index and index_curved:
        return True
    return False

def calculate_distance(point1, point2):
    return math.sqrt((point1.x - point2.x) ** 2 + (point1.y - point2.y) ** 2)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    total_fingers = 0

    frame = cv2.flip(frame, 1)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    results = hands.process(frame_rgb)

    # Continue if hands are detected
    if results.multi_hand_landmarks:
        current_time = time.time()
        
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            if is_c_gesture(hand_landmarks.landmark):

                entered_number = ""  # Clear the number if fist gesture is detected
                square = 0
                cube = 0
                cv2.putText(frame, ' Number Cleared', (50, 400), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
                continue
            # Extract the required landmarks for finger detection
            # Extract the required landmarks for finger detection
            landmarks = hand_landmarks.landmark
            
            # Calculate finger states (open/closed) by comparing y-coordinates
            finger_states = []
            for i in [8, 12, 16, 20]:  # Index, Middle, Ring, Pinky
                if landmarks[i].y < landmarks[i - 2].y:  # Check if finger is up
                    finger_states.append(1)  # Finger is open
                else:
                    finger_states.append(0)  # Finger is closed
            
            thumb_is_up = 0

            
            thumb_tip = landmarks[4]
            thumb_mcp = landmarks[2]
            index_finger_mcp = landmarks[5]

            thumb_is_below_mcp = thumb_tip.y > thumb_mcp.y  # Thumb tip below its MCP joint
            thumb_is_near_index = calculate_distance(thumb_tip, index_finger_mcp) < 0.05  # Thumb close to index base

            if not thumb_is_below_mcp and not thumb_is_near_index:
                thumb_is_up = 1  # Thumb is up
            
            finger_states.append(thumb_is_up)
            fingers_up = sum(finger_states)

            if fingers_up> 0:
                    total_fingers += fingers_up
            else:
                    total_fingers = 0
       

        # Check if the delay period has passed
        if current_time - last_detection_time > delay_seconds:
            # Concatenate the detected digit
          if total_fingers > 0:
            entered_number += str(total_fingers)
            print(f"entered Number: {entered_number}")
            
            # Update the last detection time
            last_detection_time = current_time

        # Convert concatenated_number to an integer for calculations
    
            try:
                num = int(entered_number)
                square = num ** 2
                cube = num ** 3
            except ValueError:
                pass
    
    # Display the number of fingers up on the frame
    cv2.putText(frame, f'Number: {total_fingers}', (50, 50), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 0), 2)
    cv2.putText(frame, f'Entered Number: {entered_number}', (50, 100), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 0), 2)
    cv2.putText(frame, f'Square: {square}', (50, 150), cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 0), 2)
    cv2.putText(frame, f'Cube: {cube}', (50, 200), cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 0), 2)

    cv2.imshow('Hand Tracking', frame)

    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
