from dataclasses import dataclass
from typing import Optional

# 각 테이블의 컬럼 구조 정의용 데이터 클래스

@dataclass
class User:
    user_id: Optional[int]
    name: str
    nickname: str
    email: str
    password: str

@dataclass
class PetEmoticon:
    e_id: Optional[int]
    emoticon: str
    text: str

@dataclass
class Chat:
    chat_id: Optional[int]
    user_id: int
    message_id: Optional[int]
    message: str
    timestamp: str
    video_id: Optional[int]
    video_path: Optional[str]
    video_start_timestamp: Optional[str]
    video_end_timestamp: Optional[str]
    voice_id: Optional[int]
    voice_path: Optional[str]
    voice_start_timestamp: Optional[str]
    voice_end_timestamp: Optional[str]
    e_id: Optional[int]
    pet_emotion: Optional[str]
    reply_message: Optional[str]

@dataclass
class UserEmotionAnalysis:
    emotion_analysis_id: Optional[int]
    user_id: int
    chat_id: int
    face_emotion: Optional[str]
    voice_emotion: Optional[str]
    text_emotion: Optional[str]
    summary: Optional[str]
    time: Optional[str]

@dataclass
class PetCharacterSetting:
    character_id: Optional[int]
    user_id: int
    speech: Optional[str]
    character_style: Optional[str]
    res_setting: Optional[str]

@dataclass
class PetTrainingSetting:
    training_setting_id: Optional[int]
    user_id: int
    training_text: str
    keyword_text: Optional[str]
    gesture_video_path: Optional[str]
    gesture_recognition_id: Optional[int]
    recognized_gesture: Optional[str]

@dataclass
class UserSetting:
    setting_id: Optional[int]
    user_id: int
    font_size: int

@dataclass
class Log:
    log_id: Optional[int]
    user_id: int
    log_type: str
    timestamp: str
    detail: Optional[str]
    location: Optional[str]
    device_info: Optional[str]
    error_code: Optional[str]
    ip_address: Optional[str]
