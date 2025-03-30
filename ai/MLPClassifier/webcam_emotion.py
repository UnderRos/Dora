import cv2
import numpy as np
import joblib
from deepface import DeepFace
from PIL import Image, ImageDraw, ImageFont

# 저장된 MLPClassifier 모델 불러오기
model_path = "./MLPClassifier/results/mlp_model.pkl"
clf = joblib.load(model_path)
print("학습된 모델 불러오기 완료:", model_path)

# 감정 라벨 매핑
emotion_kor_map = {"angry": "짜증", "happy": "행복", "neutral": "무표정", "sad": "슬픔"}
# DeepFace 임베딩 추출에 사용할 모델명
embedding_model_name = "ArcFace"

# 한글 폰트 설정
font_path = "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"
font = ImageFont.truetype(font_path, 32)

# 감정 안정화 관련 변수 설정
previous_emotion = ""
emotion_counter = 0
stable_emotion = ""
stable_confidence = 0.0
threshold_frames = 5  # 감정이 5 프레임 연속 유지되어야 업데이트

# 웹캠 열기
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("웹캠을 열 수 없습니다.")
    exit()

print("웹캠 시작됨. ESC 누르면 종료됩니다.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("프레임 캡처 실패")
        break

    try:
        # DeepFace로 임베딩 추출 (실시간 프레임 전달)
        representation = DeepFace.represent(img_path=frame,
                                            model_name=embedding_model_name,
                                            enforce_detection=False)
        embedding = representation[0]['embedding']

        # 예측 (임베딩을 2D 배열 형태로 전달)
        pred = clf.predict([embedding])[0]
        proba = clf.predict_proba([embedding])[0]
        # 해당 감정의 확률 (백분율)
        prob = proba[clf.classes_ == pred][0]

        # 감정 안정화 로직
        if pred == previous_emotion:
            emotion_counter += 1
        else:
            emotion_counter = 0
            previous_emotion = pred

        if emotion_counter >= threshold_frames:
            stable_emotion = pred
            stable_confidence = prob

        # 한글 텍스트 출력 (PIL 사용)
        if stable_emotion:
            pred_text = emotion_kor_map.get(stable_emotion, stable_emotion)
            text = f"감정: {pred_text} ({stable_confidence*100:.1f}%)"
            img_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            draw = ImageDraw.Draw(img_pil)
            draw.text((30, 50), text, font=font, fill=(0, 255, 0))
            frame = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
        
    except Exception as e:
        print("예측 오류:", e)
    
    cv2.imshow("Webcam Emotion Detection (MLP)", frame)
    if cv2.waitKey(1) == 27:  # ESC 키
        break

cap.release()
cv2.destroyAllWindows()