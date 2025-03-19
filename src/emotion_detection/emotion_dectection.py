import cv2
import numpy as np
import tensorflow as tf
import os

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.utils import to_categorical
from sklearn.model_selection import train_test_split

class EmotionRecognizer:
    def __init__(self):
        self.model = self.build_model()
        self.emotion_labels = ["angry", "disgust", "fear", "happy", "neutral", "sad", "surprise"]
    
    def build_model(self): # CNN 기반 감정 인식 모델을 구축
        model = Sequential([
            Conv2D(32, (3,3), activation='relu', input_shape=(48, 48, 1)),
            MaxPooling2D(2,2),
            
            Conv2D(64, (3,3), activation='relu'),
            MaxPooling2D(2,2),

            Conv2D(128, (3,3), activation='relu'),
            MaxPooling2D(2,2),

            Flatten(),
            Dense(128, activation='relu'),
            Dropout(0.5),
            Dense(7, activation='softmax')# 감정 7가지 분류
        ])
        
        model.compile(optimizer='adam',
                      loss='categorical_crossentropy',
                      metrics=['accuracy'])
        return model
    
    def load_data(self, train_path, test_path):
        def load_images_from_folder(folder, label):
            images, labels = [], []
            for emotion in self.emotion_labels:
                emotion_folder = os.path.join(folder, emotion.lower())
                if not os.path.exists(emotion_folder):
                    print(f"{emotion_folder} 폴더가 존재하지 않습니다.")
                    continue
                
                img_files = os.listdir(emotion_folder)
                if len(img_files) == 0:
                    print(f"{emotion} 폴더가 비어 있습니다.")
                    continue
                
                for img_name in img_files:
                    img_path = os.path.join(emotion_folder, img_name)
                    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
                    if img is None:
                        print(f"{img_name} 파일을 불러오지 못했습니다: {img_path}")
                        continue
                    img = cv2.resize(img, (48, 48))
                    images.append(img)
                    labels.append(label[emotion])

            return np.array(images), np.array(labels)

        # 감정 레이블 매핑 (라벨 인덱스)
        label_mapping = {emotion: idx for idx, emotion in enumerate(self.emotion_labels)}

        # train, test 데이터 로드
        X_train, y_train = load_images_from_folder(train_path, label_mapping)
        X_test, y_test = load_images_from_folder(test_path, label_mapping)

        # 데이터 정규화
        X_train = X_train / 255.0
        X_test = X_test / 255.0

        # 데이터 모양 변환
        X_train = X_train.reshape(-1, 48, 48, 1)
        X_test = X_test.reshape(-1, 48, 48, 1)

        # 원-핫 인코딩
        y_train = to_categorical(y_train, num_classes=7)
        y_test = to_categorical(y_test, num_classes=7)

        print(f"훈련 데이터: {len(X_train)}개, 테스트 데이터: {len(X_test)}개")
        return X_train, X_test, y_train, y_test

    
    def train(self, X_train, y_train, X_test, y_test, epochs=150, batch_size=64): # 모델을 학습
        self.model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size, validation_data=(X_test, y_test))
        self.model.save("emotion_model.h5")  # 학습된 모델 저장
    
    def evaluate(self, X_test, y_test): # 모델을 평가하고 정확도를 출력
        loss, acc = self.model.evaluate(X_test, y_test)
        print(f"Test Accuracy: {acc * 100:.2f}%")
    
    def load_trained_model(self, model_path="emotion_model.h5"): # 저장된 모델을 불러옵니다.
        self.model = tf.keras.models.load_model(model_path)
    
    def recognize_emotion(self): # 실시간 감정 인식을 수행하는 함수
        cap = cv2.VideoCapture(0)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            
            for (x, y, w, h) in faces:
                face = gray[y:y+h, x:x+w]
                face = cv2.resize(face, (48, 48))
                face = np.expand_dims(face, axis=0) / 255.0
                face = np.expand_dims(face, axis=-1)

                prediction = self.model.predict(face)
                emotion = self.emotion_labels[np.argmax(prediction)]
                
                cv2.putText(frame, emotion, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            cv2.imshow("Emotion Detection", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    recognizer = EmotionRecognizer()
    train_path = "data/archive/train"
    test_path = "data/archive/test"
    X_train, X_test, y_train, y_test = recognizer.load_data(train_path, test_path)
    recognizer.train(X_train, y_train, X_test, y_test)
    recognizer.evaluate(X_test, y_test)
    recognizer.recognize_emotion()
