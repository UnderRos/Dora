import socket
import json
import threading
from network.protocol import ENCODING, BUFFER_SIZE
from interface.gesture import handle_gesture_event

# 포트 설정
GESTURE_PORT = 9100
VIDEO_PORT = 5005
AUDIO_PORT = 5010


def start_gesture_listener():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", GESTURE_PORT))
    print(f"[UDP] 제스처 이벤트 수신 대기 중 (port: {GESTURE_PORT})")

    while True:
        try:
            data, addr = sock.recvfrom(BUFFER_SIZE)
            try:
                json_data = json.loads(data.decode(ENCODING))
                if json_data.get("event") == "gesture":
                    result = handle_gesture_event(json_data)
                    print("[UDP] 제스처 이벤트 처리:", result)
            except json.JSONDecodeError:
                print("[UDP] 잘못된 JSON")
        except Exception as e:
            print("[UDP] 제스처 수신 오류:", e)


def start_video_stream_receiver():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", VIDEO_PORT))
    print(f"[UDP] 비디오 스트림 수신 대기 중 (port: {VIDEO_PORT})")

    while True:
        try:
            data, addr = sock.recvfrom(65535)
            print(f"[UDP][VIDEO] {addr} → 프레임 크기: {len(data)} bytes")
        except Exception as e:
            print("[UDP][VIDEO] 오류:", e)


def start_audio_stream_receiver():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", AUDIO_PORT))
    print(f"[UDP] 오디오 스트림 수신 대기 중 (port: {AUDIO_PORT})")

    while True:
        try:
            data, addr = sock.recvfrom(65535)
            print(f"[UDP][AUDIO] {addr} → 청크 크기: {len(data)} bytes")
        except Exception as e:
            print("[UDP][AUDIO] 오류:", e)


def start_udp_listener():
    threading.Thread(target=start_gesture_listener, daemon=True).start()
    threading.Thread(target=start_video_stream_receiver, daemon=True).start()
    threading.Thread(target=start_audio_stream_receiver, daemon=True).start()
