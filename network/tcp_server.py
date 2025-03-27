import socket
import threading
import json
from core.dispatcher import dispatch

HOST = '0.0.0.0'
PORT = 9000
BUFFER_SIZE = 4096
ENCODING = 'utf-8'

def handle_client(conn, addr):
    print(f"[TCP] 클라이언트 접속: {addr}")
    with conn:
        while True:
            try:
                data = conn.recv(BUFFER_SIZE)
                if not data:
                    print(f"[TCP] 연결 종료: {addr}")
                    break

                message = data.decode(ENCODING)

                # 로그 출력 전, 비밀번호 마스킹
                try:
                    temp_json = json.loads(message)
                    if isinstance(temp_json, dict):
                        if "payload" in temp_json and isinstance(temp_json["payload"], dict):
                            if "userPassword" in temp_json["payload"]:
                                temp_json["payload"]["userPassword"] = "***"
                        print(f"[TCP] 수신 데이터: {json.dumps(temp_json)}")
                    else:
                        print(f"[TCP] 수신 데이터: {message}")
                except json.JSONDecodeError:
                    print(f"[TCP] 수신 데이터: {message}")


                try:
                    json_data = json.loads(message)
                    response = dispatch(json_data)
                except json.JSONDecodeError:
                    response = {
                        "resultCode": 4001,
                        "resultMsg": "INVALID_JSON"
                    }

                conn.sendall(json.dumps(response).encode(ENCODING))

            except ConnectionResetError:
                print(f"[TCP] 연결 끊김: {addr}")
                break


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"[TCP] 서버 시작: {HOST}:{PORT}")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
        thread.start()

