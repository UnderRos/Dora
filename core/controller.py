import json
from core.socket_client import send_message_to_server
from common.logger import log_to_db

# 로그인 요청을 처리하는 함수
def handle_login_request(email: str, password: str):
    message = {
        "command": "login",
        "payload": {
            "userEmail": email,
            "userPassword": password
        }
    }
    
    masked = {**message, "payload": {**message["payload"], "userPassword": "***"}}
    print("[Controller] 로그인 요청:", masked)
    response = send_message_to_server(message)
    print("[Controller] 로그인 응답:", response)
    if response.get("result") == "success":
        log_to_db(response.get("userId", 0), "login", f"로그인 요청: {email}")
    return response

# 회원가입 요청을 처리하는 함수
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
    masked = {**message, "payload": {**message["payload"], "userPassword": "***"}}
    print("[Controller] 회원가입 요청:", masked)
    response = send_message_to_server(message)
    if response.get("result") == "success":
        log_to_db(response.get("userId", 0), "signup", f"회원가입 요청: {email}")
    print("[Controller] 회원가입 응답:", response)
    return response

# 채팅 요청을 처리하는 함수
def handle_chat_request(user_id: int, message: str):
    message_data = {
        "command": "send_message",
        "payload": {
            "userId": user_id,
            "messageId": 0,
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
    if response.get("result") == "success":
        log_to_db(user_id, "chat", f"채팅 메시지: {message}")
    return response

# 감정 분석 요청을 처리하는 함수
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
    if response.get("result") == "success":
        log_to_db(user_id, "emotion_analysis", "감정 분석 요청")
    return response

# 펫의 성격 설정 요청을 처리하는 함수
def handle_set_character_request(user_id: int, speech: str, character: str, res_setting: str):
    message_data = {
        "command": "set_character",
        "payload": {
            "userId": user_id,
            "speech": speech,
            "character": character,
            "resSetting": res_setting
        }
    }
    print("[Controller] 펫의 성격 설정 요청:", message_data)
    response = send_message_to_server(message_data)
    print("[Controller] 펫의 성격 설정 응답:", response)
    if response.get("result") == "success":
        log_to_db(user_id, "set_character", f"말투={speech}, 성격={character}, 설정={res_setting}")
    return response

# 펫의 성격 조회 요청을 처리하는 함수
def handle_get_character_request(user_id: int):
    message_data = {
        "command": "get_character",
        "payload": {
            "userId": user_id
        }
    }
    print("[Controller] 펫의 성격 조회 요청:", message_data)
    response = send_message_to_server(message_data)

    if response.get("result") == "fail" and response.get("reason") == "설정 없음":
        print("[Controller] 펫 성격 설정 없음 → 기본값 사용")
        return {"speech": "존댓말", "character": "내향적", "resSetting": ""}

    print("[Controller] 펫의 성격 조회 응답:", response)
    return response

# 훈련 설정 요청을 처리하는 함수
def handle_set_training_request(user_id: int, training_text: str, keyword_text: str,
                                gesture_video_path: str, gesture_recognition_id: int, recognized_gesture: str):
    message_data = {
        "command": "set_training",
        "payload": {
            "userId": user_id,
            "trainingText": training_text,
            "keywordText": keyword_text,
            "gestureVideoPath": gesture_video_path,
            "gestureRecognitionId": gesture_recognition_id,
            "recognizedGesture": recognized_gesture
        }
    }
    print("[Controller] 훈련 설정 요청:", message_data)
    response = send_message_to_server(message_data)
    print("[Controller] 훈련 설정 응답:", response)
    if response.get("result") == "success":
        log_to_db(user_id, "set_training", f"훈련 등록: {training_text} → {recognized_gesture}")
    return response

# 훈련 설정 조회 요청을 처리하는 함수
def handle_get_training_request(user_id: int):
    message_data = {
        "command": "get_training",
        "payload": {
            "userId": user_id
        }
    }
    print("[Controller] 훈련 설정 조회 요청:", message_data)
    response = send_message_to_server(message_data)
    print("[Controller] 훈련 설정 조회 응답:", response)
    return response

# 사용자 설정 저장 요청을 처리하는 함수
def handle_set_setting_request(user_id: int, font_size: int):
    message_data = {
        "command": "set_setting",
        "payload": {
            "userId": user_id,
            "fontSize": font_size
        }
    }
    print("[Controller] 사용자 설정 저장 요청:", message_data)
    response = send_message_to_server(message_data)
    print("[Controller] 사용자 설정 저장 응답:", response)
    if response.get("result") == "success":
        log_to_db(user_id, "set_setting", f"폰트 크기: {font_size}")
    return response

# 사용자 설정 조회 요청을 처리하는 함수
def handle_get_setting_request(user_id: int):
    message_data = {
        "command": "get_setting",
        "payload": {
            "userId": user_id
        }
    }
    print("[Controller] 사용자 설정 조회 요청:", message_data)
    response = send_message_to_server(message_data)
    print("[Controller] 사용자 설정 조회 응답:", response)
    return response

# 로그 작성 요청을 처리하는 함수
def handle_log_write_request(user_id: int, log_type: str, timestamp: str,
                             detail: str, location: str, device_info: str,
                             error_code: str, ip_address: str):
    message_data = {
        "command": "write_log",
        "payload": {
            "userId": user_id,
            "logType": log_type,
            "timestamp": timestamp,
            "detail": detail,
            "location": location,
            "deviceInfo": device_info,
            "errorCode": error_code,
            "ipAddress": ip_address
        }
    }
    print("[Controller] 로그 작성 요청:", message_data)
    response = send_message_to_server(message_data)
    print("[Controller] 로그 작성 응답:", response)
    return response

# 영상 스트리밍 요청
def handle_video_stream_request(video_id: int, quality: str = "high", fps: int = 15):
    message_data = {
        "command": "get_video_stream",
        "payload": {
            "videoId": video_id,
            "quality": quality,
            "fps": fps
        }
    }
    print("[Controller] 영상 스트리밍 요청:", message_data)
    response = send_message_to_server(message_data)
    print("[Controller] 영상 스트리밍 응답:", response)
    if response.get("resultCode") == 1000:
        log_to_db(0, "video_stream", f"videoId={video_id}, quality={quality}, fps={fps}")
    return response

# 오디오 스트리밍 요청
def handle_audio_stream_request(audio_id: int, codec: str = "pcm",
                                sample_rate: int = 16000, channels: int = 1, chunk_size: int = 1024):
    message_data = {
        "command": "get_audio_stream",
        "payload": {
            "audioId": audio_id,
            "codec": codec,
            "sampleRate": sample_rate,
            "channels": channels,
            "chunkSize": chunk_size
        }
    }
    print("[Controller] 오디오 스트리밍 요청:", message_data)
    response = send_message_to_server(message_data)
    print("[Controller] 오디오 스트리밍 응답:", response)
    if response.get("resultCode") == 1000:
        log_to_db(0, "audio_stream", f"audioId={audio_id}, codec={codec}, rate={sample_rate}")
    return response

# 스트리밍 중지 요청
def handle_stop_stream_request(stream_type: str, stream_id: int):
    message_data = {
        "command": "stop_stream",
        "payload": {
            f"{stream_type}Id": stream_id
        }
    }
    print(f"[Controller] {stream_type} 스트리밍 중지 요청:", message_data)
    response = send_message_to_server(message_data)
    print(f"[Controller] {stream_type} 스트리밍 중지 응답:", response)
    if response.get("resultCode") == 1000:
        log_to_db(0, "stream_stop", f"{stream_type}Id={stream_id}")
    return response
