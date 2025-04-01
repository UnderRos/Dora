import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import QThread, pyqtSignal
import speech_recognition as sr
import time

from_class = uic.loadUiType("stt_test.ui")[0]

# 마이크 입력을 실시간으로 처리하고 텍스트 인식 결과를 전달하는 스레드 클래스
class Mic(QThread):
    update = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__()
        self.main = parent
        self.running = True
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

    def run(self):
        self.running = True
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)  # 주변 잡음 보정
            while self.running:
                try:
                    print("듣는 중...")
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                    text = self.recognizer.recognize_google(audio, language="ko-KR")
                    print("인식 결과:", text)
                    self.update.emit(text)
                except sr.UnknownValueError:
                    self.update.emit("음성을 인식할 수 없습니다.")
                except sr.RequestError as e:
                    self.update.emit(f"STT 요청 오류: {e}")
                except sr.WaitTimeoutError:
                    continue  # 5초 내 음성이 없으면 건너뛰기
                time.sleep(0.2)

    def stop(self):
        self.running = False

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
        self.stt_label.setText(text)

    def clickMic(self):
        if not self.isMicOn:
            self.btnMic.setText("마이크 Off")
            self.stt_label.setText("듣는 중...")
            self.isMicOn = True
            self.mic.start()
        else:
            self.btnMic.setText("마이크 On")
            self.stt_label.setText("")
            self.isMicOn = False
            self.mic.stop()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindows = WindowClass()
    myWindows.show()
    sys.exit(app.exec_())
