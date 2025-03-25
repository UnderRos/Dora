from db.models import UserEmotionAnalysis
from db.query import insert_emotion_analysis
from datetime import datetime
from common.logger import log_to_db
from ai.emotion_analyzer import analyze_emotion

def handle_emotion_analysis(payload: dict) -> dict:
    try:
        user_id = payload.get("userId")
        chat_id = payload.get("chatId")
        video_path = payload.get("videoPath")
        voice_path = payload.get("voicePath")
        message = payload.get("message")

        if not (user_id and chat_id):
            return {"result": "fail", "reason": "필수 정보 누락"}

        # 실제 감정 분석 수행
        result = analyze_emotion(message=message, video_path=video_path, voice_path=voice_path)
        face_emotion = result.get("face")
        voice_emotion = result.get("voice")
        text_emotion = result.get("text")
        summary = result.get("summary")
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

        log_to_db(
            user_id=user_id,
            log_type="emotion_analysis",
            detail=f"[감정분석] chat_id={chat_id}, face={face_emotion}, voice={voice_emotion}, text={text_emotion}"
        )

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
