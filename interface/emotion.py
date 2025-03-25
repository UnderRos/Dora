from db.models import UserEmotionAnalysis
from db.query import insert_emotion_analysis
from datetime import datetime

def handle_emotion_analysis(payload: dict) -> dict:
    try:
        user_id = payload.get("userId")
        chat_id = payload.get("chatId")
        video_path = payload.get("videoPath")
        voice_path = payload.get("voicePath")
        message = payload.get("message")

        if not (user_id and chat_id):
            return {"result": "fail", "reason": "필수 정보 누락"}

        # 감정 분석 모듈 연동 부분 (임시로 하드코딩된 결과 사용)
        face_emotion = "happy"
        voice_emotion = "calm"
        text_emotion = "worried"
        summary = "조금 걱정되지만 침착함"
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        analysis = UserEmotionAnalysis(
            emotion_analysis_id=None,
            user_id=user_id,
            chat_id=chat_id,
            face_emotion=face_emotion,
            voice_emotion=voice_emotion,
            text_emotion=text_emotion,
            summary=summary,
            time=now
        )

        emotion_id = insert_emotion_analysis(analysis)

        return {
            "result": "success",
            "emotionId": emotion_id,
            "faceEmotion": face_emotion,
            "voiceEmotion": voice_emotion,
            "textEmotion": text_emotion,
            "summary": summary,
            "time": now
        }

    except Exception as e:
        return {"result": "fail", "reason": str(e)}
