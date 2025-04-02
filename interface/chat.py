from db.query import (
    get_pet_emoticon, get_recent_chats,
    get_character_setting, get_training_settings
)
from ai.gpt_wrapper import generate_reply

def handle_chat_message(payload: dict):
    try:
        user_id = payload.get("userId")
        message = payload.get("message")

        if not (user_id and message):
            return {"result": "fail", "reason": "필수 정보 누락"}

        e_id = 5  # 기본 감정 ID
        pet_emoticon = get_pet_emoticon(e_id)
        pet_emotion = pet_emoticon["emoticon"] if pet_emoticon else "기분 좋아요"

        # 설정 조회
        character = get_character_setting(user_id) or {}
        trainings = get_training_settings(user_id) or []

        # 최근 대화 이력
        recent_chats = get_recent_chats(user_id, limit=15)
        chat_history = []
        for c in recent_chats:
            chat_history.append({"role": "user", "content": c["message"]})
            chat_history.append({"role": "assistant", "content": c["reply_message"]})

        # GPT 응답 생성 (stream=True)
        response_stream, _ = generate_reply(
            user_message=message,
            character=character,
            trainings=trainings,
            chat_history=chat_history,
            stream=True
        )

        return {
            "result": "success",
            "responseStream": response_stream,
            "eId": e_id,
            "petEmotion": pet_emotion
        }

    except Exception as e:
        return {"result": "fail", "reason": str(e)}
