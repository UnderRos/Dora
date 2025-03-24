# 돌봄 챗봇 Interface Specification & Database Schema

## 1. Interface Specifications

### [1] Login / Signup
- **Protocol**: TCP
- **Format**: JSON
- **Command**: "signup", "login"

#### Request
```json
{
  "command": "signup",
  "userNm": "admin",
  "userNickNm": "관리자",
  "userEmail": "abc@xyz.com",
  "userPassword": "123456"
}
```

#### Response
```json
{
  "result": "success",
  "token": "abc.def",
  "userId": 1
}
```

---

### [2] Chat Message
- **Protocol**: TCP
- **Format**: JSON
- **Command**: "send_message"

#### Request
```json
{
  "command": "send_message",
  "userId": 1,
  "messageId": 10,
  "message": "괜찮을까?",
  "timestamp": "2025-03-23 14:25:00",
  "videoId": 101,
  "videoPath": "/video/101.mp4",
  "videoStartTimestamp": "00:00:05.000",
  "videoEndTimestamp": "00:00:08.500",
  "voiceId": 201,
  "voicePath": "/voice/201.wav",
  "voiceStartTimestamp": "00:00:05.000",
  "voiceEndTimestamp": "00:00:08.500"
}
```

#### Response
```json
{
  "result": "success",
  "chatId": 3001,
  "eId": 5,
  "petEmotion": "기분 좋아요",
  "replyMessage": "너무 잘하고 있어!"
}
```

---

### [3] User Emotion Analysis
- **Protocol**: TCP
- **Format**: JSON
- **Command**: "analyze_emotion"

#### Request
```json
{
  "command": "analyze_emotion",
  "userId": 1,
  "chatId": 3001,
  "videoPath": "/video/101.mp4",
  "voicePath": "/voice/201.wav",
  "message": "괜찮을까?"
}
```

#### Response
```json
{
  "result": "success",
  "emotionId": 5001,
  "faceEmotion": "happy",
  "voiceEmotion": "calm",
  "textEmotion": "worried",
  "summary": "조금 걱정되지만 침착함",
  "time": "2025-03-23 14:26:00"
}
```

---

### [4] Pet Character Setting
- **Protocol**: TCP
- **Format**: JSON
- **Command**: "set_character", "get_character"

#### Request: set_character
```json
{
  "command": "set_character",
  "userId": 1,
  "speech": "존댓말",
  "character": "내향적",
  "resSetting": "땅콩 알레르기 있음"
}
```

#### Request: get_character
```json
{
  "command": "get_character",
  "userId": 1
}
```

#### Response
```json
{
  "result": "success",
  "characterId": 1001,
  "speech": "존댓말",
  "character": "내향적",
  "resSetting": "땅콩 알레르기 있음"
}
```

---

### [5] Pet Training Setting
- **Protocol**: TCP
- **Format**: JSON
- **Command**: "set_response", "get_response"

#### Request: set_response
```json
{
  "command": "set_response",
  "userId": 1,
  "trainingText": "날씨",
  "keywordText": "날씨, 하늘",
  "gestureVideoPath": "/gesture/weather.mp4",
  "gestureRecognitionId": 3101,
  "recognizedGesture": "오늘의 날씨 데이터 가져오기"
}
```

#### Response
```json
{
  "result": "success",
  "responseSettingId": 7001,
  "trainingText": "날씨",
  "keywordText": "날씨, 하늘",
  "gestureVideoPath": "/gesture/weather.mp4",
  "gestureRecognitionId": 3101,
  "recognizedGesture": "오늘의 날씨 데이터 가져오기"
}
```

---

### [6] Gesture Event
- **Protocol**: UDP
- **Format**: JSON or 단문 문자열

#### JSON 예시
```json
{
  "event": "gesture",
  "userId": "qpzja",
  "gesture": "wave",
  "trainingSettingId": 5001
}
```

---

### [7] User Setting
- **Protocol**: TCP
- **Format**: JSON
- **Command**: "set_setting", "get_setting"

#### Request: set_setting
```json
{
  "command": "set_setting",
  "userId": 1,
  "fontSize": 18
}
```

#### Response
```json
{
  "result": "success",
  "settingId": 9001,
  "fontSize": 18
}
```

---

### [8] Log
- **Protocol**: TCP
- **Format**: JSON
- **Command**: "write_log"

#### Request
```json
{
  "command": "write_log",
  "userId": 1,
  "logType": "emotion_analysis",
  "timestamp": "2025-03-23 14:30:00",
  "detail": "감정 분석 완료",
  "location": "mobile_app",
  "deviceInfo": "iPhone 14, iOS 17.2",
  "errorCode": "E2001",
  "ipAddress": "192.168.0.15"
}
```

#### Response
```json
{
  "result": "success",
  "logId": 8001,
  "errorCode": "E2001",
  "ipAddress": "192.168.0.15",
  "deviceInfo": "iPhone 14, iOS 17.2"
}
```

---

### [9] Video Stream
- **Protocol**: UDP
- **Format**: Binary (JPEG)

#### Request: get_video_stream
```json
{
  "command": "get_video_stream",
  "videoId": 101,
  "quality": "high",
  "fps": 15
}
```

#### Request: stop_stream
```json
{
  "command": "stop_stream",
  "videoId": 101
}
```

#### Response
```json
{
  "resultCode": 1000,
  "resultMsg": "SUCCESS",
  "data": {
    "streamPort": 5005,
    "protocol": "UDP",
    "format": "JPEG",
    "quality": "high",
    "fps": 15
  }
}
```

---

### [10] Audio Stream
- **Protocol**: UDP
- **Format**: Binary (PCM/MP3)

#### Request: get_audio_stream
```json
{
  "command": "get_audio_stream",
  "audioId": 201,
  "codec": "pcm",
  "sampleRate": 16000,
  "channels": 1,
  "chunkSize": 1024
}
```

#### Request: stop_stream
```json
{
  "command": "stop_stream",
  "audioId": 201
}
```

#### Response
```json
{
  "resultCode": 1000,
  "resultMsg": "SUCCESS",
  "data": {
    "streamPort": 5010,
    "protocol": "UDP",
    "codec": "pcm",
    "sampleRate": 16000,
    "channels": 1,
    "chunkSize": 1024
  }
}
```

---

## 2. Database Table Overview (컬럼 요약)

### User
- user_id (PK, INT)
- name (VARCHAR)
- nickname (VARCHAR)
- email (VARCHAR)
- password (VARCHAR)

### PetEmoticon
- e_id (PK, INT)
- emoticon (TEXT)
- text (TEXT)

### Chat
- chat_id (PK, INT)
- user_id (FK)
- message_id (INT)
- message (TEXT)
- timestamp (DATETIME)
- video_id (INT)
- video_path (TEXT)
- video_start_timestamp (TEXT)
- video_end_timestamp (TEXT)
- voice_id (INT)
- voice_path (TEXT)
- voice_start_timestamp (TEXT)
- voice_end_timestamp (TEXT)
- e_id (FK)
- pet_emotion (TEXT)
- reply_message (TEXT)

### UserEmotionAnalysis
- emotion_analysis_id (PK)
- user_id (FK)
- chat_id (FK)
- face_emotion (VARCHAR)
- voice_emotion (VARCHAR)
- text_emotion (VARCHAR)
- summary (TEXT)
- time (TEXT)

### PetCharacterSetting
- character_id (PK)
- user_id (FK)
- speech (TEXT)
- character_style (TEXT)
- res_setting (TEXT)

### PetTrainingSetting
- training_setting_id (PK)
- user_id (FK)
- training_text (TEXT)
- keyword_text (TEXT)
- gesture_video_path (TEXT)
- gesture_recognition_id (INT)
- recognized_gesture (TEXT)

### UserSetting
- setting_id (PK)
- user_id (FK)
- font_size (INT)

### Log
- log_id (PK)
- user_id (FK)
- log_type (VARCHAR)
- timestamp (DATETIME)
- detail (TEXT)
- location (VARCHAR)
- device_info (TEXT)
- error_code (VARCHAR)
- ip_address (VARCHAR)
---

## 3. 디렉토리 및 파일 구조

```plaintext
마지막으로, 이 구조 맞는지만 확인해주라.

project_root/
├── main.py                           # PyQt 앱 실행 진입점
├── controller.py                     # PyQt View 이벤트 핸들링 → socket 전송
├── socket_client.py                  # TCP/UDP 통신 클라이언트
├── dispatcher/                       # 클라이언트 명령 처리 분기
│   └── dispatcher.py                 # command → handler 라우팅
├── views/                            # PyQt UI 화면 구성
│   ├── main_window.py                # QMainWindow + 화면 전환
│   ├── login_view.py
│   ├── link_view.py
│   ├── main_view.py                  # 전체 메인 화면 (stacked layout)
│   ├── chat_panel.py
│   ├── user_status_panel.py
│   ├── pet_panel.py
│   └── setting_panel.py
├── components/                       # 공통 재사용 UI 위젯
│   ├── rounded_button.py
│   └── emoticon_label.py
├── network/                          # 서버 측 네트워크 처리
│   ├── tcp_server.py
│   ├── udp_stream.py
│   └── protocol.py                   # 메시지 형식, 공통 파서
├── interface/                        # 서버 수신 command 핸들러
│   ├── login.py
│   ├── chat.py
│   ├── emotion.py
│   ├── pet_character.py
│   ├── pet_training.py
│   ├── gesture.py
│   ├── setting.py
│   ├── log.py
│   ├── video.py
│   └── audio.py
├── db/                               # DB 연결 및 ORM/Query 처리
│   ├── connection.py                 # MySQL 연결 관리
│   ├── models.py                     # 테이블 모델 클래스
│   ├── query.py                      # 기능별 쿼리 모듈 분리
│   └── seed.py                       # 더미 파일
├── emotion/                          # 감정 분석 처리 모듈
│   ├── analyzer.py                   # 감정 분석 모델 로드 및 예측
│   └── model/                        # 학습된 모델 파일 저장
│       ├── face_emotion_model.h5
│       ├── voice_emotion_model.h5
│       └── text_emotion_model.h5
├── media/                            # 스트리밍 처리
│   ├── video_streamer.py
│   └── audio_streamer.py
├── model_training/                   # 모델 학습 및 저장
│   ├── train_face_emotion_model.py   # 얼굴 감정 모델 학습 코드
│   ├── train_voice_emotion_model.py  # 음성 감정 모델 학습 코드
│   ├── train_text_emotion_model.py   # 텍스트 감정 모델 학습 코드
│   └── datasets/                     # 학습 데이터셋 저장
│       ├── face_emotion_dataset/
│       ├── voice_emotion_dataset/
│       └── text_emotion_dataset/
├── config/
│   └── settings.py                   # DB, 포트, 경로 설정
├── log/
│   └── logger.py                     # 로그 기록 처리
└── style/
    └── style.qss                     # 전역 스타일 시트
```

---

## 4. 메시지 핸들링 구조

- PyQt → controller → socket_client → TCP/UDP → 서버
- 서버: tcp_server → dispatcher → interface/handler → query/model → 응답 반환
- 감정 분석은 `emotion/analyzer.py` 호출로 분리 처리

---

## 5. 기타 중요 사항

- `.env` 기반 DB 설정 사용 (`dotenv` 활용)
- query.py는 모든 테이블에 대해 insert/select 정의 완료
- seed.py는 모든 테이블 대상 더미 데이터 삽입 가능
- command dispatcher 구조 설계도 반영되어 있음

```python
# dispatcher.py

from interface.login import handle_signup, handle_login
from interface.chat import handle_chat_message
from interface.emotion import handle_emotion_analysis
from interface.pet_character import handle_set_character, handle_get_character
from interface.pet_training import handle_set_response, handle_get_response
from interface.gesture import handle_gesture_event
from interface.setting import handle_set_setting, handle_get_setting
from interface.log import handle_log_write
from interface.video import handle_video_stream_start, handle_stream_stop
from interface.audio import handle_audio_stream_start


def dispatch(message: dict):
    command = message.get("command")
    payload = message.get("payload", {})

    if command == "signup":
        return handle_signup(payload)
    elif command == "login":
        return handle_login(payload)

    elif command == "send_message":
        return handle_chat_message(payload)

    elif command == "analyze_emotion":
        return handle_emotion_analysis(payload)

    elif command == "set_character":
        return handle_set_character(payload)
    elif command == "get_character":
        return handle_get_character(payload)

    elif command == "set_response":
        return handle_set_response(payload)
    elif command == "get_response":
        return handle_get_response(payload)

    elif command == "gesture":
        return handle_gesture_event(payload)

    elif command == "set_setting":
        return handle_set_setting(payload)
    elif command == "get_setting":
        return handle_get_setting(payload)

    elif command == "write_log":
        return handle_log_write(payload)

    elif command == "get_video_stream":
        return handle_video_stream_start(payload)
    elif command == "get_audio_stream":
        return handle_audio_stream_start(payload)
    elif command == "stop_stream":
        return handle_stream_stop(payload)

    else:
        return {
            "resultCode": 4000,
            "resultMsg": f"UNKNOWN_COMMAND: {command}"
        }
```
