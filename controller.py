import json
from socket_client import send_message_to_server


def handle_login_request(email: str, password: str):
    message = {
        "command": "login",
        "payload": {
            "userEmail": email,
            "userPassword": password
        }
    }
    print("[Controller] 로그인 요청:", message)
    response = send_message_to_server(message)
    print("[Controller] 로그인 응답:", response)
    return response

def handle_signup_request(name: str, nickname: str, email: str, password: str):
    message = {
        "command": "signup",
        "payload": {
            "userNm": name,
            "userNickNm": nickname,
            "userEmail": email,
            "userPassword": password
        }
    }
    print("[Controller] 회원가입 요청:", message)
    response = send_message_to_server(message)
    print("[Controller] 회원가입 응답:", response)
    return response
