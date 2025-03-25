import pyaudio
import socket
from settings import AUDIO_CONFIG

SERVER_IP = '127.0.0.1'
SERVER_PORT = 5010

# UDP 소켓을 생성하고 오디오 데이터를 서버로 전송하는 함수
def start_audio_stream():
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=AUDIO_CONFIG["channels"],
                    rate=AUDIO_CONFIG["sample_rate"],
                    input=True,
                    frames_per_buffer=AUDIO_CONFIG["chunk_size"])

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        while True:
            data = stream.read(AUDIO_CONFIG["chunk_size"])
            sock.sendto(data, (SERVER_IP, SERVER_PORT))
    except KeyboardInterrupt:
        pass
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()
        sock.close()
