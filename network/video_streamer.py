import cv2
import socket
import time
from settings import VIDEO_CONFIG

SERVER_IP = '127.0.0.1'
SERVER_PORT = 5005
FPS = VIDEO_CONFIG["fps"]

# UDP 소켓을 생성하고, 카메라 영상을 읽어서 서버로 전송하는 함수
def start_video_stream():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        _, jpeg = cv2.imencode('.jpg', frame)
        sock.sendto(jpeg.tobytes(), (SERVER_IP, SERVER_PORT))
        time.sleep(1 / FPS)

    cap.release()
    sock.close()
