import os
import cv2
import pyaudio
import threading
from datetime import datetime
from core.settings import VIDEO_CONFIG, AUDIO_CONFIG
from ai.stt_wrapper import get_whisper

class LiveAudioRecorder:
    def __init__(self, callback=None):
        self.running = False
        self.thread = None
        self.sample_rate = AUDIO_CONFIG["sample_rate"]
        self.chunk = AUDIO_CONFIG["chunk_size"]
        self.channels = AUDIO_CONFIG["channels"]
        self.save_dir = AUDIO_CONFIG["save_dir"]
        self.callback = callback
        self.whisper = get_whisper()

    def _record_loop(self):
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16,
                        channels=self.channels,
                        rate=self.sample_rate,
                        input=True,
                        frames_per_buffer=self.chunk)

        audio_data = b""
        buffer_duration = 1  # 초 단위
        buffer_size = int(self.sample_rate / self.chunk * buffer_duration)

        while self.running:
            frames = []
            for _ in range(buffer_size):
                data = stream.read(self.chunk, exception_on_overflow=False)
                frames.append(data)

            audio_data = b"".join(frames)
            temp_path = os.path.join(self.save_dir, "__temp_chunk.wav")
            self._save_chunk(temp_path, audio_data, p)

            try:
                result = self.whisper.transcribe(temp_path, language="ko").strip()
                if result and self.callback:
                    self.callback(result)
            except Exception as e:
                print(f"[STT] 오류: {e}")

        stream.stop_stream()
        stream.close()
        p.terminate()

    def _save_chunk(self, path, data, p):
        import wave
        wf = wave.open(path, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(self.sample_rate)
        wf.writeframes(data)
        wf.close()

    def start(self):
        os.makedirs(self.save_dir, exist_ok=True)
        self.running = True
        self.thread = threading.Thread(target=self._record_loop)
        self.thread.start()

    def stop(self):
        self.running = False
        self.thread.join()


class VideoRecorder:
    def __init__(self, fps=30):
        self.fps = fps
        self.running = False
        self.thread = None
        self.save_dir = VIDEO_CONFIG["save_dir"]

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._record_loop)
        self.thread.start()

    def stop(self):
        self.running = False
        self.thread.join()

    def _record_loop(self):
        os.makedirs(self.save_dir, exist_ok=True)
        output_path = generate_filename("video", "mp4", self.save_dir)

        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("카메라 열기 실패")
            return

        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, self.fps, (width, height))

        while self.running:
            ret, frame = cap.read()
            if not ret:
                break
            out.write(frame)

        cap.release()
        out.release()

def generate_filename(prefix: str, ext: str, directory: str) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{prefix}_{timestamp}.{ext}"
    return os.path.join(directory, filename)