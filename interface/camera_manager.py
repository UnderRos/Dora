# camera_manager.py
import cv2
from PyQt5.QtCore import QTimer

class CameraManager:
    _instance = None

    def __init__(self, camera_index=0):
        self.camera_index = camera_index
        self.cap = cv2.VideoCapture(camera_index)
        if not self.cap.isOpened():
            raise RuntimeError("Could not open camera")
        self.timer = QTimer()
        self.timer.setInterval(30)
        self.callbacks = []  # 각 패널에서 프레임을 받아 처리할 콜백 함수 목록
        self.timer.timeout.connect(self._read_frame)

    @classmethod
    def instance(cls, camera_index=0):
        if cls._instance is None:
            cls._instance = cls(camera_index)
        return cls._instance

    def _read_frame(self):
        ret, frame = self.cap.read()
        if ret:
            for cb in self.callbacks:
                cb(frame)

    def start(self):
        self.timer.start()

    def stop(self):
        self.timer.stop()
        self.cap.release()
        CameraManager._instance = None

    def add_frame_callback(self, callback):
        if callback not in self.callbacks:
            self.callbacks.append(callback)

    def remove_frame_callback(self, callback):
        if callback in self.callbacks:
            self.callbacks.remove(callback)
