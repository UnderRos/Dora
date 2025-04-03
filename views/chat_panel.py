import threading
import cv2
import json
import socket
from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QTextBrowser, QPushButton,
    QCheckBox, QMessageBox, QLabel, QApplication, QListWidget, QListWidgetItem
)
from PyQt5.QtCore import Qt, QUrl, QTimer, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QImage, QPixmap, QTextCursor
from db.query import get_recent_chats, insert_chat
from ai.stt_wrapper import transcribe_audio
from ai.tts_wrapper import speak_text_korean
from common.recorder import LiveAudioRecorder
from db.models import Chat
from markdown2 import markdown
import subprocess
from interface.emotion import analyze_emotion as analyze_webcam_emotion
from interface.camera_manager import CameraManager
import librosa
import numpy as np
from ai.voice_emotion_model import predict_emotion

class ChatPanel(QWidget):
    expressionDetected = pyqtSignal(str)
    cameraToggled = pyqtSignal(bool)
    micToggled = pyqtSignal(bool)
    gestureToggled = pyqtSignal(bool)  # 제스처 체크박스 시그널

    dolbomMessageReceived = pyqtSignal(str, bool)
    chatRefreshRequested = pyqtSignal()

    def __init__(self, user_id: int, user_name: str):
        super().__init__()
        self.user_id = user_id
        self.user_name = user_name
        self.recorder = None
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.conn.connect(("127.0.0.1", 9000))
        except Exception as e:
            QMessageBox.critical(self, "서버 연결 오류", f"서버에 연결할 수 없습니다:\n{e}")
            return

        self.camera_manager = None  # 공유 카메라 관리자 인스턴스
        self.mic_enabled = False
        self.gesture_process = None

        self.last_block_cursor = None
        self.dolbom_started = False
        self.reply_accumulator = ""
        self.last_emotion_update = 0

        self.init_ui()
        self.load_chat_history()

        self.dolbomMessageReceived.connect(self.append_dolbom_message)
        self.chatRefreshRequested.connect(self.refresh_chat_display)

    def init_ui(self):
        layout = QVBoxLayout()

        self.chat_display = QTextBrowser()
        self.chat_display.setOpenLinks(False)
        self.chat_display.anchorClicked.connect(self.on_chat_anchor_clicked)
        self.chat_display.setPlaceholderText("여기에 대화 내용이 표시됩니다...")
        self.chat_display.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        self.chat_input = QTextEdit()
        self.chat_input.setPlaceholderText("메시지를 입력하세요...")
        self.chat_input.setFixedHeight(60)
        self.chat_input.keyPressEvent = self.handle_enter_key

        send_button = QPushButton("전송")
        send_button.clicked.connect(self.send_chat_message)

        toggles = QHBoxLayout()
        self.camera_checkbox = QCheckBox("카메라 ON")
        self.camera_checkbox.toggled.connect(self.toggle_camera)
        self.mic_checkbox = QCheckBox("마이크 ON")
        self.mic_checkbox.toggled.connect(self.toggle_mic)
        self.gesture_checkbox = QCheckBox("제스처 ON")
        self.gesture_checkbox.toggled.connect(self.toggle_gesture)
        toggles.addWidget(self.camera_checkbox)
        toggles.addWidget(self.mic_checkbox)
        toggles.addWidget(self.gesture_checkbox)

        input_layout = QHBoxLayout()
        input_layout.addWidget(self.chat_input)
        input_layout.addWidget(send_button)

        layout.addLayout(toggles)
        layout.addWidget(self.chat_display)
        layout.addLayout(input_layout)

        self.start_voice_btn = QPushButton("음성 입력 시작")
        self.stop_voice_btn = QPushButton("음성 입력 종료")
        self.stop_voice_btn.setEnabled(False)
        self.start_voice_btn.clicked.connect(self.start_recording)
        self.stop_voice_btn.clicked.connect(self.stop_recording)
        voice_btns = QHBoxLayout()
        voice_btns.addWidget(self.start_voice_btn)
        voice_btns.addWidget(self.stop_voice_btn)
        layout.addLayout(voice_btns)

        self.start_voice_btn.setEnabled(False)
        self.stop_voice_btn.setEnabled(False)

        self.camera_label = QLabel()
        self.camera_label.setFixedSize(320, 240)
        self.camera_label.setStyleSheet("background-color: black;")
        self.camera_label.setVisible(False)
        layout.addWidget(self.camera_label)

        self.setLayout(layout)

    def stop_recording(self):
        self.stop_voice_btn.setEnabled(False)
        try:
            wav_path = self.recorder.stop()
            self.recorder = None
            text = transcribe_audio(wav_path)
            existing_text = self.chat_input.toPlainText()
            self.chat_input.setText(existing_text + " " + text)

            audio_np, sr = librosa.load(wav_path, sr=16000)
            emotion, conf = predict_emotion(audio_np)
            if not np.isnan(conf):
                self.chat_display.append(f"<span style='color:gray;'>[감정 분석] {emotion} ({conf*100:.1f}%)</span>")
            else:
                self.chat_display.append("<span style='color:gray;'>[감정 분석 실패]</span>")
        except Exception as e:
            QMessageBox.critical(self, "STT 오류", f"음성 인식 실패: {e}")
        finally:
            self.start_voice_btn.setEnabled(True)

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    panel = ChatPanel(user_id=1, user_name="User1")
    panel.show()
    sys.exit(app.exec_())
