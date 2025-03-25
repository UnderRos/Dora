from db.models import UserSetting
from db.query import set_user_setting, get_user_setting
from common.logger import log_to_db

def handle_set_setting(payload: dict) -> dict:
    try:
        user_id = payload.get("userId")
        font_size = payload.get("fontSize")

        if not (user_id and font_size):
            return {"result": "fail", "reason": "필수 정보 누락"}

        setting = UserSetting(
            setting_id=None,
            user_id=user_id,
            font_size=font_size
        )

        set_user_setting(setting)

        log_to_db(
            user_id=user_id,
            log_type="set_setting",
            detail=f"폰트 크기 설정 변경: {font_size}"
        )

        return {
            "result": "success",
            "settingId": user_id, 
            "fontSize": font_size
        }

    except Exception as e:
        return {"result": "fail", "reason": str(e)}


def handle_get_setting(payload: dict) -> dict:
    try:
        user_id = payload.get("userId")
        if not user_id:
            return {"result": "fail", "reason": "userId 누락"}

        setting = get_user_setting(user_id)
        if not setting:
            return {"result": "fail", "reason": "설정 없음"}

        return {
            "result": "success",
            "settingId": setting["setting_id"],
            "fontSize": setting["font_size"]
        }

    except Exception as e:
        return {"result": "fail", "reason": str(e)}
