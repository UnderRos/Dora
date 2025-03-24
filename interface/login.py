from db.models import User
from db.query import insert_user, get_user_by_email

def handle_signup(payload: dict) -> dict:
    name = payload.get("userNm")
    nickname = payload.get("userNickNm")
    email = payload.get("userEmail")
    password = payload.get("userPassword")

    print(f"[SIGNUP] name={name}, nickname={nickname}, email={email}, password={password}")

    if not (name and email and password):
        return {"result": "fail", "reason": "필수 정보 누락"}

    existing = get_user_by_email(email)
    if existing:
        return {"result": "fail", "reason": "이미 존재하는 이메일"}

    user = User(user_id=None, name=name, nickname=nickname, email=email, password=password)
    user_id = insert_user(user)

    return {
        "result": "success",
        "userId": user_id
    }

def handle_login(payload: dict) -> dict:
    email = payload.get("userEmail")
    password = payload.get("userPassword")

    user = get_user_by_email(email)
    if not user or user["password"] != password:
        return {"result": "fail", "reason": "이메일 또는 비밀번호 불일치"}

    return {
        "result": "success",
        "userId": user["user_id"]
    }
