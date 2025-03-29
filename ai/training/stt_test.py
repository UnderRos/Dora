import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
import time
from PyQt5.QtCore import QThread, pyqtSignal
import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write

from_class = uic.loadUiType("stt_test.ui")[0]


# 마이크 녹음을 위한 스레드 클래스
class Mic(QThread):
    update = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__()
        self.main = parent
        self.running = True
        self.fs = 16000  # 샘플레이트
        self.recorded_frames = []  # 녹음된 데이터를 저장할 리스트

    def callback(self, indata, frames, time, status):
        if self.running:
            self.recorded_frames.append(indata.copy())

    def run(self):
        self.running = True
        self.recorded_frames = []

        with sd.InputStream(samplerate=self.fs, channels=1, callback=self.callback):
            while self.running:
                sd.sleep(100)

    def stop(self):
        self.running = False
        time.sleep(0.5)  # 스트림 종료 기다림

        # numpy 배열로 병합
        audio = np.concatenate(self.recorded_frames, axis=0)
        write("output.wav", self.fs, audio)  # WAV 파일 저장
        self.update.emit("녹음 완료: output.wav 저장됨")
        

# 메인 윈도우 클래스
class WindowClass(QMainWindow, from_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.mic = Mic(self)
        self.mic.update.connect(self.updateMic)

        self.isMicOn = False
        self.btnMic.clicked.connect(self.clickMic)

    def updateMic(self, text):
        self.label.setText(text)

    def clickMic(self):
        if not self.isMicOn:
            self.btnMic.setText("마이크 Off")
            self.label.setText("녹음 중...")
            self.isMicOn = True
            self.mic.start()
        else:
            self.btnMic.setText("마이크 On")
            self.label.setText("저장 중...")
            self.isMicOn = False
            self.mic.stop()
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindows = WindowClass()
    myWindows.show()
    sys.exit(app.exec_())
