import cv2
import mediapipe as mp
import numpy as np
import time, os, json
import argparse
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.callbacks import ModelCheckpoint, ReduceLROnPlateau
from tensorflow.keras.utils import to_categorical
from sklearn.model_selection import train_test_split

class GestureDataCollector:
    def __init__(self, gesture_name, data_path, seq_length=30, secs_for_action=15):
        self.gesture_name = gesture_name
        self.data_path = data_path
        self.seq_length = seq_length
        self.secs_for_action = secs_for_action
        os.makedirs(self.data_path, exist_ok=True)

        # MediaPipe Hands 초기화
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5)

    def collect_data(self):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error: Cannot open camera.")
            return

        created_time = int(time.time())
        collected_data = []

        print(f"Start collecting data for gesture: {self.gesture_name.upper()}")
        # 준비 메시지
        ret, img = cap.read()
        img = cv2.flip(img, 1)
        cv2.putText(img, f'Collecting {self.gesture_name.upper()} action...', org=(10, 30),
                    fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1,
                    color=(255, 255, 255), thickness=2)
        cv2.imshow('img', img)
        cv2.waitKey(3000)

        start_time = time.time()
        while time.time() - start_time < self.secs_for_action:
            ret, img = cap.read()
            if not ret: break
            img = cv2.flip(img, 1)
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            result = self.hands.process(img_rgb)
            img_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)

            if result.multi_hand_landmarks is not None:
                for res in result.multi_hand_landmarks:
                    joint = np.zeros((21, 4))
                    for j, lm in enumerate(res.landmark):
                        joint[j] = [lm.x, lm.y, lm.z, lm.visibility]

                    # 관절 간 벡터 및 각도 계산
                    v1 = joint[[0,1,2,3,0,5,6,7,0,9,10,11,0,13,14,15,0,17,18,19], :3]
                    v2 = joint[[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20], :3]
                    v = v2 - v1
                    v = v / np.linalg.norm(v, axis=1)[:, np.newaxis]

                    angle = np.arccos(np.einsum('nt,nt->n',
                        v[[0,1,2,4,5,6,8,9,10,12,13,14,16,17,18],:],
                        v[[1,2,3,5,6,7,9,10,11,13,14,15,17,18,19],:]))
                    angle = np.degrees(angle)

                    # 특징 벡터 구성: 관절 좌표 + 각도
                    d = np.concatenate([joint.flatten(), angle])
                    collected_data.append(d)
                    self.mp_drawing.draw_landmarks(img_bgr, res, self.mp_hands.HAND_CONNECTIONS)

            cv2.imshow('img', img_bgr)
            if cv2.waitKey(1) == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

        collected_data = np.array(collected_data)
        print(f"{self.gesture_name} data shape: {collected_data.shape}")
        # 원시 데이터 저장
        raw_filename = os.path.join(self.data_path, f'raw_{self.gesture_name}_{created_time}.npy')
        np.save(raw_filename, collected_data)

        # 시퀀스 데이터 생성 및 저장
        full_seq_data = []
        for seq in range(len(collected_data) - self.seq_length):
            full_seq_data.append(collected_data[seq:seq + self.seq_length])
        full_seq_data = np.array(full_seq_data)
        print(f"{self.gesture_name} sequence data shape: {full_seq_data.shape}")
        seq_filename = os.path.join(self.data_path, f'seq_{self.gesture_name}_{created_time}.npy')
        np.save(seq_filename, full_seq_data)

        return raw_filename, seq_filename

class GestureTrainer:
    def __init__(self, data_path, model_path, seq_length=30):
        self.data_path = data_path
        self.model_path = model_path
        self.seq_length = seq_length

    def load_data(self):
        x_data = []
        y_data = []
        actions = []  # 제스처 이름 목록

        for filename in os.listdir(self.data_path):
            if filename.startswith('seq_') and filename.endswith('.npy'):
                action_name = filename.split('_')[1]
                if action_name not in actions:
                    actions.append(action_name)
                action_index = actions.index(action_name)
                data = np.load(os.path.join(self.data_path, filename))
                x_data.extend(data[:, :, :-1].tolist())
                y_data.extend([action_index] * len(data))

        x_data = np.array(x_data, dtype=np.float32)
        y_data = np.array(y_data)
        y_data = to_categorical(y_data, num_classes=len(actions))
        return x_data, y_data, actions

    def train_model(self, epochs=200, test_size=0.1):
        x_data, y_data, actions = self.load_data()
        print("Data shapes:", x_data.shape, y_data.shape)

        x_train, x_val, y_train, y_val = train_test_split(x_data, y_data, test_size=test_size, random_state=43)

        # LSTM 모델 구성
        model = Sequential([
            LSTM(64, activation='relu', input_shape=x_train.shape[1:3]),
            Dense(32, activation='relu'),
            Dense(len(actions), activation='softmax')
        ])

        model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['acc'])

        callbacks = [
            ModelCheckpoint(self.model_path, monitor='val_acc', verbose=1, save_best_only=True, mode='auto'),
            ReduceLROnPlateau(monitor='val_acc', factor=0.5, patience=50, verbose=1, mode='auto')
        ]

        model.fit(
            x_train,
            y_train,
            validation_data=(x_val, y_val),
            epochs=epochs,
            callbacks=callbacks
        )

        # 제스처 레이블 저장
        label_path = os.path.join(os.path.dirname(self.model_path), 'gesture_labels.json')
        with open(label_path, 'w') as f:
            json.dump(actions, f)
        print("Training complete. Labels saved to:", label_path)

def main():
    parser = argparse.ArgumentParser(description="Gesture Training Application")
    parser.add_argument('--mode', choices=['collect', 'train'], required=True,
                        help="모드 선택: collect (데이터 수집), train (모델 학습)")
    parser.add_argument('--gesture', type=str, help="수집할 제스처 이름 (collect 모드)")
    parser.add_argument('--data_path', type=str, default='data/gesture_seed_data', help="데이터 저장 경로")
    parser.add_argument('--model_path', type=str, default='models/gesture_model.h5', help="모델 저장 경로")
    parser.add_argument('--epochs', type=int, default=200, help="학습 에포크 (train 모드)")
    args = parser.parse_args()

    if args.mode == 'collect':
        if not args.gesture:
            print("collect 모드에서는 --gesture 인자를 필수로 지정해야 합니다.")
            return
        collector = GestureDataCollector(gesture_name=args.gesture, data_path=args.data_path)
        collector.collect_data()
    elif args.mode == 'train':
        trainer = GestureTrainer(data_path=args.data_path, model_path=args.model_path)
        trainer.train_model(epochs=args.epochs)

if __name__ == "__main__":
    main()
