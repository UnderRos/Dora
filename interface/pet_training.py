from db.models import PetTrainingSetting
from db.query import insert_training_setting
from common.logger import log_to_db

def handle_set_response(payload: dict) -> dict:
    try:
        user_id = payload.get("userId")
        training_text = payload.get("trainingText")
        keyword_text = payload.get("keywordText")
        gesture_video_path = payload.get("gestureVideoPath")
        gesture_recognition_id = payload.get("gestureRecognitionId")
        recognized_gesture = payload.get("recognizedGesture")

        if not (user_id and training_text):
            return {"result": "fail", "reason": "필수 정보 누락"}

        setting = PetTrainingSetting(
            training_setting_id=None,
            user_id=user_id,
            training_text=training_text,
            keyword_text=keyword_text,
            gesture_video_path=gesture_video_path,
            gesture_recognition_id=gesture_recognition_id,
            recognized_gesture=recognized_gesture
        )

        setting_id = insert_training_setting(setting)

        log_to_db(
            user_id=setting.user_id,
            log_type="set_response",
            detail=f"훈련 등록: '{setting.training_text}' → {setting.recognized_gesture}"
        )

        return {
            "result": "success",
            "responseSettingId": setting_id,
            "trainingText": setting.training_text,
            "keywordText": setting.keyword_text,
            "gestureVideoPath": setting.gesture_video_path,
            "gestureRecognitionId": setting.gesture_recognition_id,
            "recognizedGesture": setting.recognized_gesture
        }

    except Exception as e:
        return {"result": "fail", "reason": str(e)}


def handle_get_response(payload: dict) -> dict:
    # 현재 응답 정의 없음 (설정 조회 시 응답 형태 필요 시 구현)
    return {"result": "fail", "reason": "미구현"}
