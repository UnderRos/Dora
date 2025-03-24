def handle_gesture_event(payload: dict) -> dict:
    try:
        user_id = payload.get("userId")
        gesture = payload.get("gesture")
        training_setting_id = payload.get("trainingSettingId")

        if not (user_id and gesture):
            return {"result": "fail", "reason": "필수 정보 누락"}

        # 현재는 단순히 성공 응답만 반환 (추후 확장 가능)
        return {
            "result": "success",
            "userId": user_id,
            "gesture": gesture,
            "trainingSettingId": training_setting_id
        }

    except Exception as e:
        return {"result": "fail", "reason": str(e)}
