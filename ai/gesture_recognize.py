import cv2
import mediapipe as mp
import numpy as np
import os, json
import argparse
from tensorflow.keras.models import load_model

class GestureRecognizer:
    def __init__(self, model_path, seq_length=30):
        self.model_path = model_path
        self.seq_length = seq_length

        try:
            self.model = load_model(self.model_path)
        except FileNotFoundError:
            print(f"Error: Model file not found at {self.model_path}")
            self.model = None

        label_file = os.path.join(os.path.dirname(self.model_path), 'gesture_labels.json')
        try:
            with open(label_file, 'r') as f:
                self.actions = json.load(f)
        except FileNotFoundError:
            print("Error: gesture_labels.json file not found.")
            self.actions = None

        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5)

    def recognize(self):
        if self.model is None or self.actions is None:
            print("Model or gesture labels not loaded. Exiting.")
            return

        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error: Could not open camera.")
            return

        seq = []
        action_seq = []

        while cap.isOpened():
            ret, img = cap.read()
            if not ret:
                break

            img = cv2.flip(img, 1)
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            result = self.hands.process(img_rgb)
            img_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)

            if result.multi_hand_landmarks:
                for hand_landmarks in result.multi_hand_landmarks:
                    joint = np.zeros((21, 4))
                    for j, landmark in enumerate(hand_landmarks.landmark):
                        joint[j] = [landmark.x, landmark.y, landmark.z, landmark.visibility]

                    v1 = joint[[0, 1, 2, 3, 0, 5, 6, 7, 0, 9, 10, 11, 0, 13, 14, 15, 0, 17, 18, 19], :3]
                    v2 = joint[[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20], :3]
                    v = v2 - v1
                    v = v / np.linalg.norm(v, axis=1)[:, np.newaxis]

                    angle = np.arccos(np.einsum('nt,nt->n',
                        v[[0, 1, 2, 4, 5, 6, 8, 9, 10, 12, 13, 14, 16, 17, 18], :],
                        v[[1, 2, 3, 5, 6, 7, 9, 10, 11, 13, 14, 15, 17, 18, 19], :]))
                    angle = np.degrees(angle)

                    d = np.concatenate([joint.flatten(), angle])
                    seq.append(d)

                    self.mp_drawing.draw_landmarks(img_bgr, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

                    if len(seq) < self.seq_length:
                        continue

                    input_data = np.expand_dims(np.array(seq[-self.seq_length:], dtype=np.float32), axis=0)
                    y_pred = self.model.predict(input_data).squeeze()

                    if y_pred.ndim == 0:
                        continue

                    i_pred = int(np.argmax(y_pred))
                    conf = y_pred[i_pred]

                    if conf < 0.9:
                        continue

                    predicted_action = self.actions[i_pred]
                    action_seq.append(predicted_action)

                    if len(action_seq) < 3:
                        continue

                    this_action = '?'
                    if action_seq[-1] == action_seq[-2] == action_seq[-3]:
                        this_action = predicted_action

                    text = f'{this_action.upper()} ({conf:.2f})'
                    cv2.putText(img_bgr, text, org=(10, 30),
                                fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1,
                                color=(255, 255, 255), thickness=2)

            cv2.imshow('Gesture Recognition', img_bgr)
            if cv2.waitKey(1) == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

def main():
    parser = argparse.ArgumentParser(description="Gesture Recognition Application")
    parser.add_argument('--model_path', type=str, default='models/gesture_model.h5', help="모델 저장 경로")
    args = parser.parse_args()

    recognizer = GestureRecognizer(model_path=args.model_path)
    recognizer.recognize()

if __name__ == "__main__":
    main()
