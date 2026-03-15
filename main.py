import cv2
import mediapipe as mp
import json
from kafka import KafkaProducer

# Initialize MediaPipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# Initialize Kafka Producer
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def get_hand_bitmask(landmarks):
    tips = [4, 8, 12, 16, 20]
    mask = 0
    for i, tip_idx in enumerate(tips):
        # Finger-up logic: Tip must be higher than the PIP joint
        if landmarks[tip_idx].y < landmarks[tip_idx - 2].y:
            mask |= (1 << i)
    return mask

cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame.")
        break

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    left_mask, right_mask, pinky_y = 0, 0, 0.0

    if results.multi_hand_landmarks:
        for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
            # Draw landmarks locally so you can see the camera working
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            label = results.multi_handedness[idx].classification[0].label
            if label == 'Left':
                left_mask = get_hand_bitmask(hand_landmarks.landmark)
            else:
                right_mask = get_hand_bitmask(hand_landmarks.landmark)
                pinky_y = hand_landmarks.landmark[20].y

        # Push to Kafka
        event = {"left_mask": left_mask, "right_mask": right_mask, "pinky_y": pinky_y}
        producer.send('gestures_raw', event)

    cv2.imshow("Vision Producer - Press Q to Quit", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()