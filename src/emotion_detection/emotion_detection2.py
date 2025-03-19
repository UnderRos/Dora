import os
import cv2
import numpy as np
import tensorflow as tf
import mediapipe as mp
import keras_tuner as kt
import tensorflow_model_optimization as tfmot

from tensorflow.keras import mixed_precision
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout, BatchNormalization
from tensorflow.keras.utils import to_categorical
from collections import deque, Counter

# Mixed Precision 활성화
mixed_precision.set_global_policy('mixed_float16')

class DataLoader:
    def __init__(self, emotions):
        self.emotions = emotions

    def load(self, train_dir, test_dir):
        def _load(folder):
            imgs, labels = [], []
            for idx, emo in enumerate(self.emotions):
                path = os.path.join(folder, emo)
                if not os.path.isdir(path): continue
                for f in os.listdir(path):
                    img = cv2.imread(os.path.join(path, f), cv2.IMREAD_GRAYSCALE)
                    if img is None: continue
                    imgs.append(cv2.resize(img,(48,48)))
                    labels.append(idx)
            return np.array(imgs), np.array(labels)

        X_train, y_train = _load(train_dir)
        X_test, y_test   = _load(test_dir)
        X_train = X_train.reshape(-1,48,48,1)/255.0
        X_test  = X_test.reshape(-1,48,48,1)/255.0
        return X_train, X_test, to_categorical(y_train,len(self.emotions)), to_categorical(y_test,len(self.emotions))

class ModelBuilder:
    @staticmethod
    def build(hp):
        model = Sequential()
        for i, filters in enumerate([
            hp.Choice('conv1_filters',[32,64]),
            hp.Choice('conv2_filters',[64,128]),
            hp.Choice('conv3_filters',[128,256])]):
            if i==0:
                model.add(Conv2D(filters,(3,3),activation='relu',input_shape=(48,48,1),
                                 kernel_regularizer=tf.keras.regularizers.l2(hp.Choice('l2',[1e-4,1e-3]))))
            else:
                model.add(Conv2D(filters,(3,3),activation='relu',
                                 kernel_regularizer=tf.keras.regularizers.l2(hp.Choice('l2',[1e-4,1e-3]))))
            model.add(BatchNormalization()); model.add(MaxPooling2D(2,2))
        model.add(Flatten())
        model.add(Dense(hp.Int('dense_units',64,256,step=64),activation='relu'))
        model.add(Dropout(hp.Choice('dropout_rate',[0.2,0.3,0.5])))
        model.add(Dense(len(emotions),activation='softmax'))
        optimizer = tf.keras.optimizers.Adam(hp.Choice('learning_rate',[1e-2,1e-3,1e-4]))
        model.compile(optimizer=optimizer, loss='categorical_crossentropy', metrics=['accuracy'])
        return model

class HyperbandTuner:
    def __init__(self):
        self.tuner = kt.Hyperband(
            ModelBuilder.build,
            objective='val_accuracy',
            max_epochs=30,
            factor=3,
            directory='kt_dir',
            project_name='emotion_tuning'
        )

    def search(self, X_train, y_train, X_test, y_test):
        prune_cb = tfmot.sparsity.keras.UpdatePruningStep()
        early = tf.keras.callbacks.EarlyStopping('val_accuracy', patience=5, restore_best_weights=True)

        self.tuner.search(
            X_train, y_train,
            validation_data=(X_test, y_test),
            epochs=50,
            callbacks=[prune_cb, early]
        )

        teacher = self.tuner.get_best_models()[0]
        hp = self.tuner.get_best_hyperparameters()[0]
        return teacher, hp

class Distiller:
    def __init__(self, teacher, student): self.teacher, self.student = teacher, student
    def distill(self, X_train, y_train, X_test, y_test):
        self.student.compile(optimizer='adam', loss=tf.keras.losses.KLDivergence(), metrics=['accuracy'])
        self.student.fit(X_train,y_train,validation_data=(X_test,y_test),epochs=20)
        return self.student

class Exporter:
    @staticmethod
    def to_tflite(model,path):
        conv = tf.lite.TFLiteConverter.from_keras_model(model)
        conv.optimizations=[tf.lite.Optimize.DEFAULT]
        open(path,'wb').write(conv.convert())

class EmotionRecognizer:
    def __init__(self, model, emotions):
        self.model = model
        self.emotions = emotions
        self.history = deque(maxlen=10)    # 최근 10개 예측 저장

    def recognize(self):
        cap = cv2.VideoCapture(0)
        detector = mp.solutions.face_detection.FaceDetection(0.5)

        while True:
            ret, frame = cap.read()
            if not ret: break

            results = detector.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            if results.detections:
                for d in results.detections:
                    bbox = d.location_data.relative_bounding_box
                    h,w,_ = frame.shape
                    x,y,w_box,h_box = int(bbox.xmin*w), int(bbox.ymin*h), int(bbox.width*w), int(bbox.height*h)

                    face = cv2.cvtColor(frame[y:y+h_box, x:x+w_box], cv2.COLOR_BGR2GRAY)
                    face = cv2.resize(face, (48,48)) / 255.0
                    preds = self.model.predict(face.reshape(1,48,48,1))
                    emotion_idx = np.argmax(preds)

                    # 히스토리에 추가 → 다수결로 결정
                    self.history.append(emotion_idx)
                    most_common = Counter(self.history).most_common(1)[0][0]
                    emotion = self.emotions[most_common]

                    cv2.rectangle(frame, (x,y), (x+w_box, y+h_box), (0,255,0), 2)
                    cv2.putText(frame, emotion, (x, y-10),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

            cv2.imshow("Emotion Detection", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

if __name__=='__main__':
    emotions=["angry","disgust","fear","happy","neutral","sad","surprise"]
    dl=DataLoader(emotions)
    X_train,X_test,y_train,y_test=dl.load('data/archive/train','data/archive/test')
    tuner=HyperbandTuner(); teacher,best_hp=tuner.search(X_train,y_train,X_test,y_test)
    print('Best HP:',best_hp.values)
    student=Sequential([Conv2D(32,(3,3),
                               activation='relu',input_shape=(48,48,1)),
                               MaxPooling2D(),Flatten(),Dense(64,activation='relu'),
                               Dense(len(emotions),activation='softmax')])
    dist=Distiller(teacher,student); student=dist.distill(X_train,y_train,X_test,y_test)
    Exporter.to_tflite(student,'emotion_student_quant.tflite')
    app=EmotionRecognizer(student,emotions); app.recognize()