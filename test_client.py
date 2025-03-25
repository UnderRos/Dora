import socket
import json

HOST = '127.0.0.1'  # 서버 주소 (로컬 테스트)
PORT = 9000         # 서버 포트
ENCODING = 'utf-8'

def send_message(message: dict):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(json.dumps(message).encode(ENCODING))
        data = s.recv(4096)
        response = json.loads(data.decode(ENCODING))
        print("서버 응답:", response)

if __name__ == "__main__":
    # 테스트용 signup 메시지
    signup_message = {
    "command": "signup",
    "payload": {
        "userNm": "admin",
        "userNickNm": "관리자",
        "userEmail": "admin@example.com",
        "userPassword": "1234"
        }
    }

    # 테스트용 login 메시지
    login_message = {
        "command": "login",
        "payload": {
            "userEmail": "admin@example.com",
            "userPassword": "1234"
        }
    }

    print("===== 회원가입 요청 =====")
    send_message(signup_message)

    print("\n===== 로그인 요청 =====")
    send_message(login_message)
