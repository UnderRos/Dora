from db.models import PetTrainingSetting
from db.query import insert_training_setting

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

        response_id = insert_training_setting(setting)

        return {
            "result": "success",
            "responseSettingId": response_id,
            "trainingText": training_text,
            "keywordText": keyword_text,
            "gestureVideoPath": gesture_video_path,
            "gestureRecognitionId": gesture_recognition_id,
            "recognizedGesture": recognized_gesture
        }

    except Exception as e:
        return {"result": "fail", "reason": str(e)}


def handle_get_response(payload: dict) -> dict:
    # 명세서에 get_response 응답만 있고 요청 형식은 없음
    return {"result": "fail", "reason": "get_response 미구현"}
