import cv2
import mediapipe as mp
import numpy as np
from tensorflow.keras.models import load_model
import json
from PIL import Image, ImageDraw, ImageFont

def put_korean_text(img, text, position, font_size=32, color=(0, 0, 255)):
    """
    OpenCV 이미지에 한글 텍스트를 그리기 위해 PIL을 사용합니다.
    img: OpenCV BGR 이미지
    text: 출력할 텍스트 (한글 포함)
    position: 텍스트 위치 (x, y)
    font_size: 텍스트 크기
    color: 텍스트 색상 (B, G, R)
    """
    # OpenCV BGR 이미지를 RGB로 변환하고 PIL 이미지로 변경
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(img_rgb)
    draw = ImageDraw.Draw(pil_img)
    try:
        # Ubuntu 환경에서 Nanum Gothic 폰트 사용
        font = ImageFont.truetype("/usr/share/fonts/truetype/nanum/NanumGothic.ttf", font_size)
    except IOError:
        print("NanumGothic.ttf not found. Using default font.")
        font = ImageFont.load_default()
    # PIL은 색상을 RGB 순서로 사용합니다.
    draw.text(position, text, font=font, fill=(color[2], color[1], color[0]))
    # PIL 이미지를 다시 OpenCV BGR 이미지로 변환
    img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    return img

def recognize_gesture(model_path):
    """
    실시간으로 제스처를 인식하고 화면에 표시합니다.
    """
    seq_length = 30

    try:
        model = load_model(model_path)
    except FileNotFoundError:
        print(f"Error: Model file not found at {model_path}")
        return

    # 모델의 레이블(제스처 이름) 가져오기
    try:
        with open('./ai/training/data/gesture_labels.json', 'r') as f:
            actions = json.load(f)
    except FileNotFoundError:
        print("Error: gesture_labels.json file not found.")
        return

    mp_hands = mp.solutions.hands
    mp_drawing = mp.solutions.drawing_utils
    hands = mp_hands.Hands(
        max_num_hands=2,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    seq = []
    action_seq = []

    while cap.isOpened():
        ret, img = cap.read()
        if not ret:
            print("Frame not captured.")
            break

        img = cv2.flip(img, 1)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        result = hands.process(img_rgb)
        img_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)

        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                joint = np.zeros((21, 4))
                for j, landmark in enumerate(hand_landmarks.landmark):
                    joint[j] = [landmark.x, landmark.y, landmark.z, landmark.visibility]

                v1 = joint[[0, 1, 2, 3, 0, 5, 6, 7, 0, 9, 10, 11, 0, 13, 14, 15, 0, 17, 18, 19], :3]
                v2 = joint[[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20], :3]
                v = v2 - v1
                norm = np.linalg.norm(v, axis=1)
                norm[norm == 0] = 1e-6  # 0으로 나누는 경우 방지
                v = v / norm[:, np.newaxis]

                angle = np.arccos(np.clip(np.einsum('nt,nt->n',
                    v[[0, 1, 2, 4, 5, 6, 8, 9, 10, 12, 13, 14, 16, 17, 18], :],
                    v[[1, 2, 3, 5, 6, 7, 9, 10, 11, 13, 14, 15, 17, 18, 19], :]), -1.0, 1.0))
                angle = np.degrees(angle)

                d = np.concatenate([joint.flatten(), angle])
                seq.append(d)

                mp_drawing.draw_landmarks(img_bgr, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                if len(seq) < seq_length:
                    continue

                input_data = np.expand_dims(np.array(seq[-seq_length:], dtype=np.float32), axis=0)
                y_pred = model.predict(input_data).squeeze()

                if y_pred.ndim == 0:
                    print("No prediction result.")
                    continue

                i_pred = int(np.argmax(y_pred))
                conf = y_pred[i_pred]

                if conf < 0.8:
                    continue

                predicted_action = actions[i_pred]
                action_seq.append(predicted_action)

                if len(action_seq) < 2:
                    continue

                this_action = '?'
                if action_seq[-1] == action_seq[-2] == action_seq[-3]:
                    this_action = predicted_action

                text = f'{this_action.upper()} ({conf:.2f})'
                img_bgr = put_korean_text(img_bgr, text, (10, 60), font_size=32, color=(0, 0, 255))
        else:
            img_bgr = put_korean_text(img_bgr, "손이 감지되지 않았습니다.", (10, 60), font_size=24, color=(0, 255, 0))

        cv2.imshow('img', img_bgr)
        if cv2.waitKey(30) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    model_path = './models/gesture_model.h5'
    recognize_gesture(model_path)
