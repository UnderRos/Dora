from db.connection import Database
from db.models import *

# ---------------------- User ----------------------

def insert_user(user: User) -> int:
    db = Database()
    db.connect()
    query = """
        INSERT INTO User (name, nickname, email, password)
        VALUES (%s, %s, %s, %s)
    """
    db.execute(query, (user.name, user.nickname, user.email, user.password))
    user_id = db.lastrowid()
    db.disconnect()
    return user_id

def get_user_by_email(email: str) -> dict:
    db = Database()
    db.connect()
    db.execute("SELECT * FROM User WHERE email = %s", (email,))
    result = db.fetchone()
    db.disconnect()
    return result

# ---------------------- PetEmoticon ----------------------

def insert_pet_emoticon(emoticon: PetEmoticon) -> int:
    db = Database()
    db.connect()
    query = """
        INSERT INTO PetEmoticon (emoticon, text)
        VALUES (%s, %s)
    """
    db.execute(query, (emoticon.emoticon, emoticon.text))
    result_id = db.lastrowid()
    db.disconnect()
    return result_id

def get_pet_emoticon(e_id: int) -> dict:
    db = Database()
    db.connect()
    db.execute("SELECT * FROM PetEmoticon WHERE e_id = %s", (e_id,))
    result = db.fetchone()
    db.disconnect()
    return result

# ---------------------- Chat ----------------------

def insert_chat(chat: Chat) -> int:
    db = Database()
    db.connect()
    query = """
        INSERT INTO Chat (
            user_id, message_id, message, timestamp,
            video_id, video_path, video_start_timestamp, video_end_timestamp,
            voice_id, voice_path, voice_start_timestamp, voice_end_timestamp,
            e_id, pet_emotion, reply_message
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    params = (
        chat.user_id, chat.message_id, chat.message, chat.timestamp,
        chat.video_id, chat.video_path, chat.video_start_timestamp, chat.video_end_timestamp,
        chat.voice_id, chat.voice_path, chat.voice_start_timestamp, chat.voice_end_timestamp,
        chat.e_id, chat.pet_emotion, chat.reply_message
    )
    db.execute(query, params)
    chat_id = db.lastrowid()
    db.disconnect()
    return chat_id

def get_recent_chats(user_id: int, limit: int = 10) -> list[Chat]:
    db = Database()
    db.connect()
    query = """
        SELECT message, reply_message
        FROM Chat
        WHERE user_id = %s
        ORDER BY chat_id DESC
        LIMIT %s
    """
    db.execute(query, (user_id, limit))
    result = db.fetchall()
    db.disconnect()
    return result[::-1]  # 최신 → 오래된 순서로 바꿈


# ---------------------- UserEmotionAnalysis ----------------------

def insert_user_emotion_analysis(analysis: UserEmotionAnalysis) -> int:
    db = Database()
    db.connect()
    query = """
        INSERT INTO UserEmotionAnalysis (
            user_id, chat_id, face_emotion, voice_emotion, text_emotion, summary, time
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    params = (
        analysis.user_id, analysis.chat_id, analysis.face_emotion,
        analysis.voice_emotion, analysis.text_emotion, analysis.summary, analysis.time
    )
    db.execute(query, params)
    result_id = db.lastrowid()
    db.disconnect()
    return result_id

def get_user_emotion_analysis(user_id: int) -> list[dict]:
    db = Database()
    db.connect()
    query = """
        SELECT time, summary, face_emotion, voice_emotion, text_emotion
        FROM UserEmotionAnalysis
        WHERE user_id = %s
        ORDER BY time DESC
        LIMIT 50
    """
    db.execute(query, (user_id,))
    result = db.fetchall()
    db.disconnect()
    return result

# ---------------------- PetCharacterSetting ----------------------

def get_character_setting(user_id: int) -> dict:
    db = Database()
    db.connect()
    db.execute("SELECT * FROM PetCharacterSetting WHERE user_id = %s", (user_id,))
    result = db.fetchone()
    db.disconnect()
    return result

def insert_character_setting(setting: PetCharacterSetting) -> int:
    db = Database()
    db.connect()
    query = """
        INSERT INTO PetCharacterSetting (user_id, speech, character_style, res_setting)
        VALUES (%s, %s, %s, %s)
    """
    params = (setting.user_id, setting.speech, setting.character_style, setting.res_setting)
    db.execute(query, params)
    result_id = db.lastrowid()
    db.disconnect()
    return result_id

# ---------------------- PetTrainingSetting ----------------------

def insert_training_setting(setting: PetTrainingSetting) -> int:
    db = Database()
    db.connect()
    query = """
        INSERT INTO PetTrainingSetting (
            user_id, training_text, keyword_text,
            gesture_video_path, gesture_recognition_id, recognized_gesture
        ) VALUES (%s, %s, %s, %s, %s, %s)
    """
    params = (
        setting.user_id, setting.training_text, setting.keyword_text,
        setting.gesture_video_path, setting.gesture_recognition_id, setting.recognized_gesture
    )
    db.execute(query, params)
    result_id = db.lastrowid()
    db.disconnect()
    return result_id

# ---------------------- UserSetting ----------------------

def get_user_setting(user_id: int) -> dict:
    db = Database()
    db.connect()
    db.execute("SELECT * FROM UserSetting WHERE user_id = %s", (user_id,))
    result = db.fetchone()
    db.disconnect()
    return result

def set_user_setting(setting: UserSetting) -> int:
    db = Database()
    db.connect()
    query = """
        INSERT INTO UserSetting (user_id, font_size)
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE font_size = VALUES(font_size)
    """
    db.execute(query, (setting.user_id, setting.font_size))
    db.disconnect()
    return setting.user_id

# ---------------------- Log ----------------------

def insert_log(log: Log) -> int:
    db = Database()
    db.connect()
    query = """
        INSERT INTO Log (
            user_id, log_type, timestamp, detail,
            location, device_info, error_code, ip_address
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    params = (
        log.user_id, log.log_type, log.timestamp, log.detail,
        log.location, log.device_info, log.error_code, log.ip_address
    )
    db.execute(query, params)
    result_id = db.lastrowid()
    db.disconnect()
    return result_id
