import cv2
import numpy as np
import joblib
from deepface import DeepFace
from PIL import Image, ImageDraw, ImageFont

# 저장된 MLPClassifier 모델 불러오기 (한 번만 로딩)
model_path = "./ai/MLPClassifier/results/mlp_model.pkl"
clf = joblib.load(model_path)
print("학습된 모델 불러오기 완료:", model_path)

# 감정 라벨 매핑
emotion_kor_map = {"angry": "짜증", "happy": "행복", "neutral": "무표정", "sad": "슬픔"}
# DeepFace 임베딩 추출에 사용할 모델명
embedding_model_name = "ArcFace"

# 감정 안정화 관련 변수 (여러 프레임에 걸친 결과 누적)
previous_emotion = ""
emotion_counter = 0
stable_emotion = ""
stable_confidence = 0.0
threshold_frames = 2  # 감정이 프레임 연속 유지되어야 업데이트

def analyze_emotion(frame): 
    # 전달받은 프레임(이미지 배열)을 DeepFace와 저장된 MLP 모델을 사용하여 감정을 분석하고,
    # 안정적인 결과가 나오면 "감정: <라벨> (<확률>%)" 형태의 문자열을 반환합니다.
    
    global previous_emotion, emotion_counter, stable_emotion, stable_confidence
    try:
        # DeepFace로 임베딩 추출 (enforce_detection=False: 얼굴 검출 실패 시에도 처리)
        representation = DeepFace.represent(img_path=frame,
                                            model_name=embedding_model_name,
                                            enforce_detection=False)
        embedding = representation[0]['embedding']

        # MLP 모델을 사용하여 감정 예측
        pred = clf.predict([embedding])[0]
        proba = clf.predict_proba([embedding])[0]
        # 해당 감정의 확률 (백분율 계산)
        prob = proba[clf.classes_ == pred][0]

        # 감정 안정화 로직: 연속 프레임 결과가 같으면 카운트 증가
        if pred == previous_emotion:
            emotion_counter += 1
        else:
            emotion_counter = 0
            previous_emotion = pred

        if emotion_counter >= threshold_frames:
            stable_emotion = pred
            stable_confidence = prob

        if stable_emotion:
            pred_text = emotion_kor_map.get(stable_emotion, stable_emotion)
            return f"감정: {pred_text} ({stable_confidence * 100:.1f}%)"
        else:
            return "감정: 분석 중..."
    except Exception as e:
        print("예측 오류:", e)
        return "감정: 오류"
