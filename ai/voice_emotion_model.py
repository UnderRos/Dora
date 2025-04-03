import numpy as np
import librosa
from tensorflow.keras.models import load_model
import os

# 감정 라벨 정의 (모델이 예측하는 클래스 순서대로!)
emotion_labels = ['Angry', 'Anxious', 'Embarrassed', 'Happy', 'Hurt', 'Neutrality', 'Sad', 'Neutrality']

# 모델 경로 설정
base_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(base_dir, 'models', 'voice_emotion_model.h5')

# 모델 로딩 (최초 1회만 로드됨)
model = load_model(model_path)

# MFCC 전처리 함수
def extract_mfcc(audio_np, sr=16000, max_pad_len=128):
    mfcc = librosa.feature.mfcc(y=audio_np.astype(np.float32), sr=sr, n_mfcc=40)
    if mfcc.shape[1] < max_pad_len:
        mfcc = np.pad(mfcc, ((0, 0), (0, max_pad_len - mfcc.shape[1])), mode='constant')
    else:
        mfcc = mfcc[:, :max_pad_len]
    return mfcc.T[np.newaxis, :, :]  # (1, 128, 40)

# 감정 예측 함수 (GUI에서 호출)
def predict_emotion(audio_np, sr=16000):
    mfcc_input = extract_mfcc(audio_np, sr)
    pred = model.predict(mfcc_input, verbose=0)[0]
    idx = np.argmax(pred)
    emotion = emotion_labels[idx]
    confidence = pred[idx]
    return emotion, confidence
