import os
import cv2
import pyaudio
import wave
import threading
from datetime import datetime
from core.settings import VIDEO_CONFIG, AUDIO_CONFIG

class LiveAudioRecorder:
    def __init__(self):
        self.frames = []
        self.running = False
        self.thread = None
        self.sample_rate = AUDIO_CONFIG["sample_rate"]
        self.chunk = AUDIO_CONFIG["chunk_size"]
        self.channels = AUDIO_CONFIG["channels"]
        self.save_dir = AUDIO_CONFIG["save_dir"]

    def _record_loop(self):
        import pyaudio
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16,
                        channels=self.channels,
                        rate=self.sample_rate,
                        input=True,
                        frames_per_buffer=self.chunk)
        self.stream = stream

        while self.running:
            data = stream.read(self.chunk)
            self.frames.append(data)

        stream.stop_stream()
        stream.close()
        p.terminate()

    def start(self):
        os.makedirs(self.save_dir, exist_ok=True)
        self.frames = []
        self.running = True
        self.thread = threading.Thread(target=self._record_loop)
        self.thread.start()

    def stop(self) -> str:
        self.running = False
        self.thread.join()

        from datetime import datetime
        import wave
        filename = f"voice_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
        output_path = os.path.join(self.save_dir, filename)

        wf = wave.open(output_path, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(pyaudio.PyAudio().get_sample_size(pyaudio.paInt16))
        wf.setframerate(self.sample_rate)
        wf.writeframes(b''.join(self.frames))
        wf.close()

        return output_path

def generate_filename(prefix: str, ext: str, directory: str) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{prefix}_{timestamp}.{ext}"
    return os.path.join(directory, filename)


class VideoRecorder:
    def __init__(self, duration=None, fps=None):
        self.duration = duration or VIDEO_CONFIG["duration"]
        self.fps = fps or VIDEO_CONFIG["fps"]
        self.save_dir = VIDEO_CONFIG["save_dir"]

    def record(self) -> str:
        os.makedirs(self.save_dir, exist_ok=True)
        output_path = generate_filename("video", "mp4", self.save_dir)

        cap = cv2.VideoCapture(0)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, self.fps, (width, height))

        for _ in range(int(self.duration * self.fps)):
            ret, frame = cap.read()
            if not ret:
                break
            out.write(frame)

        cap.release()
        out.release()
        return output_path
