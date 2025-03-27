import socket
import json

HOST = '127.0.0.1'
PORT = 9000
ENCODING = 'utf-8'
BUFFER_SIZE = 4096

def send_message_to_server(message: dict) -> dict:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.sendall(json.dumps(message).encode(ENCODING))
            data = s.recv(BUFFER_SIZE)
            response = json.loads(data.decode(ENCODING))
            return response
    except ConnectionRefusedError:
        print("[SocketClient] 서버에 연결할 수 없습니다.")
        return {"result": "fail", "reason": "서버 연결 실패"}
    except Exception as e:
        print(f"[SocketClient] 오류 발생: {e}")
        return {"result": "fail", "reason": str(e)}
