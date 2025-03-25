from db.query import insert_user, get_user_by_email
from db.models import User
from common.logger import log_to_db

def handle_signup(payload: dict) -> dict:
    try:
        name = payload.get("userNm")
        nickname = payload.get("userNickNm")
        email = payload.get("userEmail")
        password = payload.get("userPassword")

        if not (name and nickname and email and password):
            return {"result": "fail", "reason": "필수 정보 누락"}

        user = User(
            user_id=None,
            name=name,
            nickname=nickname,
            email=email,
            password=password  # 추후 해싱 필요
        )

        user_id = insert_user(user)

        log_to_db(
            user_id=user_id,
            log_type="signup",
            detail=f"회원가입 완료: {email}"
        )

        return {"result": "success", "token": "dummy.token", "userId": user_id}

    except Exception as e:
        return {"result": "fail", "reason": str(e)}


def handle_login(payload: dict) -> dict:
    try:
        email = payload.get("userEmail")
        password = payload.get("userPassword")

        user = get_user_by_email(email)
        if not user or user["password"] != password:
            return {"result": "fail", "reason": "이메일 또는 비밀번호 오류"}

        log_to_db(
            user_id=user["user_id"],
            log_type="login",
            detail=f"로그인 성공: {email}"
        )

        return {"result": "success", "token": "dummy.token", "userId": user["user_id"]}

    except Exception as e:
        return {"result": "fail", "reason": str(e)}
