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


def handle_chat_request(user_id: int, message: str):
    message_data = {
        "command": "send_message",
        "payload": {
            "userId": user_id,
            "messageId": 0,  # 실제 메시지 ID는 서버에서 부여
            "message": message,
            "timestamp": "",
            "videoId": 0,
            "videoPath": "",
            "videoStartTimestamp": "",
            "videoEndTimestamp": "",
            "voiceId": 0,
            "voicePath": "",
            "voiceStartTimestamp": "",
            "voiceEndTimestamp": ""
        }
    }
    print("[Controller] 채팅 요청:", message_data)
    response = send_message_to_server(message_data)
    print("[Controller] 채팅 응답:", response)
    return response

def handle_emotion_analysis_request(user_id: int, chat_id: int, video_path: str, voice_path: str, message: str):
    message_data = {
        "command": "analyze_emotion",
        "payload": {
            "userId": user_id,
            "chatId": chat_id,
            "videoPath": video_path,
            "voicePath": voice_path,
            "message": message
        }
    }
    print("[Controller] 감정 분석 요청:", message_data)
    response = send_message_to_server(message_data)
    print("[Controller] 감정 분석 응답:", response)
    return response
