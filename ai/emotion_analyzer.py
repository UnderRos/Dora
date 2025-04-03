import os
import joblib
from keras.models import load_model
import numpy as np

# 모델 경로
MODEL_DIR = os.path.join(os.path.dirname(__file__), 'models')

try:
    # 텍스트 감정 분석 모델 로드
    text_model = joblib.load(os.path.join(MODEL_DIR, 'text_emotion_model.h5'))

    # 음성 감정 분석 모델 로드
    voice_model = load_model(os.path.join(MODEL_DIR, 'voice_emotion_model.keras'))

    # 얼굴 감정 분석 모델 로드
    face_model = load_model(os.path.join(MODEL_DIR, 'face_emotion_model.h5'))
except Exception:
    text_model = None
    voice_model = None
    face_model = None


# 간단한 분석 함수 (예시)
def analyze_emotion(message: str, video_path: str = None, voice_path: str = None) -> dict:
    # 텍스트 분석 (예시: SVM 분류기)
    text_emotion = text_model.predict([message])[0] if message else None

    # 음성 분석 (예시: MFCC → 예측)
    voice_emotion = "neutral"  # placeholder
    if voice_path:
        # 여기에 실제 음성 특징 추출 및 예측 코드 연결
        voice_emotion = "calm"  # 예시

    # 얼굴 분석 (예시: 프레임 추출 후 예측)
    face_emotion = "happy"  # placeholder
    if video_path:
        # 여기에 실제 영상 프레임 처리 코드 연결
        face_emotion = "happy"  # 예시

    # 통합 결과 요약
    summary = "텍스트: {}, 음성: {}, 얼굴: {}".format(text_emotion, voice_emotion, face_emotion)

    return {
        "text": text_emotion,
        "voice": voice_emotion,
        "face": face_emotion,
        "summary": summary
    }