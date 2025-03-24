from db.models import Chat
from db.query import insert_chat
from db.query import get_pet_emoticon  # 이모티콘 및 메시지 대응
from datetime import datetime

def handle_chat_message(payload: dict) -> dict:
    try:
        user_id = payload.get("userId")
        message_id = payload.get("messageId")
        message = payload.get("message")
        timestamp = payload.get("timestamp")
        video_id = payload.get("videoId")
        video_path = payload.get("videoPath")
        video_start = payload.get("videoStartTimestamp")
        video_end = payload.get("videoEndTimestamp")
        voice_id = payload.get("voiceId")
        voice_path = payload.get("voicePath")
        voice_start = payload.get("voiceStartTimestamp")
        voice_end = payload.get("voiceEndTimestamp")

        if not (user_id and message):
            return {"result": "fail", "reason": "필수 정보 누락"}

        # 기본 이모티콘 ID 임의 설정 (예: 5), 추후 감정 분석 결과 반영 가능
        e_id = 5
        pet_emoticon = get_pet_emoticon(e_id)
        pet_emotion = pet_emoticon["emoticon"] if pet_emoticon else "기분 좋아요"
        reply_message = pet_emoticon["text"] if pet_emoticon else "응원할게요!"

        chat = Chat(
            chat_id=None,
            user_id=user_id,
            message_id=message_id,
            message=message,
            timestamp=timestamp or datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            video_id=video_id,
            video_path=video_path,
            video_start_timestamp=video_start,
            video_end_timestamp=video_end,
            voice_id=voice_id,
            voice_path=voice_path,
            voice_start_timestamp=voice_start,
            voice_end_timestamp=voice_end,
            e_id=e_id,
            pet_emotion=pet_emotion,
            reply_message=reply_message
        )

        chat_id = insert_chat(chat)

        return {
            "result": "success",
            "chatId": chat_id,
            "eId": e_id,
            "petEmotion": pet_emotion,
            "replyMessage": reply_message
        }

    except Exception as e:
        return {"result": "fail", "reason": str(e)}
