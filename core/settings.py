import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'dolbom_chatbot'),
    'charset': 'utf8mb4'
}

VIDEO_CONFIG = {
    "save_dir": "media/video/",
    "fps": 15,
    "duration": 3
}

AUDIO_CONFIG = {
    "save_dir": "media/voice/",
    "sample_rate": 16000,
    "channels": 1,
    "chunk_size": 1024,
    "duration": 3
}
