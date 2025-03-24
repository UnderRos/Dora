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
