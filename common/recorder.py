import os
import cv2
import pyaudio
import wave
from datetime import datetime
from settings import VIDEO_CONFIG, AUDIO_CONFIG


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


class AudioRecorder:
    def __init__(self, duration=None):
        self.duration = duration or AUDIO_CONFIG["duration"]
        self.save_dir = AUDIO_CONFIG["save_dir"]
        self.sample_rate = AUDIO_CONFIG["sample_rate"]
        self.chunk = AUDIO_CONFIG["chunk_size"]
        self.channels = AUDIO_CONFIG["channels"]

    def record(self) -> str:
        os.makedirs(self.save_dir, exist_ok=True)
        output_path = generate_filename("voice", "wav", self.save_dir)

        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16,
                        channels=self.channels,
                        rate=self.sample_rate,
                        input=True,
                        frames_per_buffer=self.chunk)

        frames = []
        for _ in range(int(self.sample_rate / self.chunk * self.duration)):
            data = stream.read(self.chunk)
            frames.append(data)

        stream.stop_stream()
        stream.close()
        p.terminate()

        wf = wave.open(output_path, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(self.sample_rate)
        wf.writeframes(b''.join(frames))
        wf.close()

        return output_path
