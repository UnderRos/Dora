from common.logger import log_to_db

def handle_gesture_event(payload: dict) -> dict:
    try:
        user_id = payload.get("userId")
        gesture = payload.get("gesture")
        training_setting_id = payload.get("trainingSettingId")

        if not (user_id and gesture and training_setting_id):
            return {"result": "fail", "reason": "필수 정보 누락"}

        log_to_db(
            user_id=0,  # ID 형식이 문자열이므로, 0 또는 None 처리
            log_type="gesture",
            detail=f"[제스처 인식] user={user_id}, gesture={gesture}, settingId={training_setting_id}"
        )

        return {"result": "success"}

    except Exception as e:
        return {"result": "fail", "reason": str(e)}
