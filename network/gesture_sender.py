import socket
import json
from network.protocol import ENCODING

def send_gesture_event(user_id: str, gesture: str, training_setting_id: int,
                       host="127.0.0.1", port=9100):
    """
    제스처 이벤트를 UDP로 서버에 전송하는 함수

    Args:
        user_id (str): 사용자 ID (문자열)
        gesture (str): 인식된 제스처 이름
        training_setting_id (int): 연결된 훈련 설정 ID
        host (str): 서버 IP (기본 로컬)
        port (int): 서버 포트 (기본 9100)
    """
    message = {
        "event": "gesture",
        "userId": user_id,
        "gesture": gesture,
        "trainingSettingId": training_setting_id
    }

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(json.dumps(message).encode(ENCODING), (host, port))
        sock.close()
        print(f"[Client] 제스처 이벤트 전송 완료 → gesture={gesture}, user={user_id}")
    except Exception as e:
        print(f"[Client] 제스처 이벤트 전송 실패: {e}")
