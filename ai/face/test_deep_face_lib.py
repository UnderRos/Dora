import cv2
from deepface import DeepFace
from PIL import ImageFont, ImageDraw, Image
import numpy as np
import os

# 사용할 감정만 선택
target_emotions = ['angry', 'happy', 'neutral', 'sad', 'fear', 'disgust', 'surprise']

# 영어 → 한글 감정 매핑
emotion_kor_map = {
    'angry': '짜증',
    'happy': '행복',
    'neutral': '무표정',
    'sad': '슬픔',
    'fear': '무표정',
    'disgust': '짜증',
    'surprise': '행복'
}

# 감정 유지 관련 변수
previous_emotion = ""
emotion_counter = 0
stable_emotion = ""
stable_confidence = 0.0
threshold_frames = 10  # 감정이 몇 프레임 연속 유지되어야 표시할지

# 한글 폰트 경로 설정 (Ubuntu 기준)
fontpath = "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"
if not os.path.exists(fontpath):
    print("한글 폰트가 설치되어 있지 않아요. 아래 명령어로 설치해보세요:")
    print("sudo apt install fonts-nanum")
    exit()
font = ImageFont.truetype(fontpath, 32)

# 웹캠 열기
cap = cv2.VideoCapture(0)
print("📷 웹캠 시작됨. ESC 누르면 종료됩니다.")

# 창 이름을 영어로 설정 (한글 깨짐 방지)
window_name = "Emotion Detection"
cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

while True:
    ret, frame = cap.read()
    if not ret:
        print("프레임 캡처 실패")
        break

    try:
        result = DeepFace.analyze(img_path=frame,
                                  actions=['emotion'],
                                  enforce_detection=False)

        all_emotions = result[0]['emotion']
        filtered = {emotion: all_emotions[emotion] for emotion in target_emotions}
        dominant_emotion = max(filtered, key=filtered.get)
        confidence = filtered[dominant_emotion]

        if dominant_emotion == previous_emotion:
            emotion_counter += 1
        else:
            emotion_counter = 0
            previous_emotion = dominant_emotion

        if emotion_counter >= threshold_frames:
            stable_emotion = dominant_emotion
            stable_confidence = confidence

        # 감정 출력 (PIL + 한글)
        if stable_emotion:
            text = f"감정: {emotion_kor_map[stable_emotion]} ({stable_confidence:.1f}%)"
            img_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            draw = ImageDraw.Draw(img_pil)
            draw.text((30, 30), text, font=font, fill=(0, 255, 0))
            frame = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

    except Exception as e:
        print(f"분석 실패: {e}")

    # 결과 출력
    cv2.imshow(window_name, frame)

    if cv2.waitKey(1) == 27:  # ESC 키
        break

cap.release()
cv2.destroyAllWindows()
