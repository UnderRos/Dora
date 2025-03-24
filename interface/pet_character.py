from db.models import PetCharacterSetting
from db.query import insert_character_setting, get_character_setting

def handle_set_character(payload: dict) -> dict:
    try:
        user_id = payload.get("userId")
        speech = payload.get("speech")
        character = payload.get("character")
        res_setting = payload.get("resSetting")

        if not user_id:
            return {"result": "fail", "reason": "userId 누락"}

        setting = PetCharacterSetting(
            character_id=None,
            user_id=user_id,
            speech=speech,
            character_style=character,
            res_setting=res_setting
        )

        character_id = insert_character_setting(setting)

        return {
            "result": "success",
            "characterId": character_id,
            "speech": speech,
            "character": character,
            "resSetting": res_setting
        }

    except Exception as e:
        return {"result": "fail", "reason": str(e)}


def handle_get_character(payload: dict) -> dict:
    try:
        user_id = payload.get("userId")
        if not user_id:
            return {"result": "fail", "reason": "userId 누락"}

        setting = get_character_setting(user_id)
        if not setting:
            return {"result": "fail", "reason": "설정 없음"}

        return {
            "result": "success",
            "characterId": setting["character_id"],
            "speech": setting["speech"],
            "character": setting["character_style"],
            "resSetting": setting["res_setting"]
        }

    except Exception as e:
        return {"result": "fail", "reason": str(e)}
