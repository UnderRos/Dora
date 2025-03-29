import sys
import threading
import time
import cv2
import numpy as np
import joblib
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QTextBrowser, QPushButton,
    QCheckBox, QMessageBox, QLabel
)
from PyQt5.QtCore import Qt, QUrl, QTimer, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap
from core.controller import handle_chat_request
from db.query import get_recent_chats
from ai.stt_wrapper import transcribe_audio
from ai.tts_wrapper import speak_text_korean
from common.recorder import LiveAudioRecorder

from .webcam_emotion import analyze_emotion

class ChatPanel(QWidget):
    # 체크박스 상태 변경을 외부로 알리기 위한 시그널 (카메라, 마이크)
    expressionDetected = pyqtSignal(str)
    cameraToggled = pyqtSignal(bool)
    micToggled = pyqtSignal(bool)

    def __init__(self, user_id: int, user_name: str):
        super().__init__()
        self.user_id = user_id
        self.user_name = user_name
        self.recorder = None

        # 웹캠 관련 변수
        self.camera_capture = None
        self.camera_timer = QTimer(self)
        self.camera_timer.timeout.connect(self.update_camera_frame)
        # 감정 분석 타이머 (예: 1초 간격)
        self.expression_timer = QTimer(self)
        self.expression_timer.timeout.connect(self.update_expression_result)

        # 마이크 상태 변수 (True: 사용가능, False: 비활성)
        self.mic_enabled = False

        self.init_ui()
        self.load_chat_history()

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

        # 토글 영역 - 카메라와 마이크 체크박스
        toggles = QHBoxLayout()
        self.camera_checkbox = QCheckBox("카메라 ON")
        self.camera_checkbox.toggled.connect(self.toggle_camera)
        self.mic_checkbox = QCheckBox("마이크 ON")
        self.mic_checkbox.toggled.connect(self.toggle_mic)
        toggles.addWidget(self.camera_checkbox)
        toggles.addWidget(self.mic_checkbox)

        input_layout = QHBoxLayout()
        input_layout.addWidget(self.chat_input)
        input_layout.addWidget(send_button)

        layout.addLayout(toggles)
        layout.addWidget(self.chat_display)
        layout.addLayout(input_layout)

        # 음성 제어 버튼 영역
        self.start_voice_btn = QPushButton("음성 입력 시작")
        self.stop_voice_btn = QPushButton("음성 입력 종료")
        self.stop_voice_btn.setEnabled(False)
        self.start_voice_btn.clicked.connect(self.start_recording)
        self.stop_voice_btn.clicked.connect(self.stop_recording)
        voice_btns = QHBoxLayout()
        voice_btns.addWidget(self.start_voice_btn)
        voice_btns.addWidget(self.stop_voice_btn)
        layout.addLayout(voice_btns)

        # 초기에는 마이크가 꺼져 있으므로 음성 버튼 비활성화
        self.start_voice_btn.setEnabled(False)
        self.stop_voice_btn.setEnabled(False)

        # 웹캠 영상을 표시할 QLabel (초기에는 숨김)
        self.camera_label = QLabel()
        self.camera_label.setFixedSize(320, 240)
        self.camera_label.setStyleSheet("background-color: black;")
        self.camera_label.setVisible(False)
        layout.addWidget(self.camera_label)

        self.setLayout(layout)

    def load_chat_history(self):
        history = get_recent_chats(self.user_id, limit=20)
        self.chat_display.clear()
        for chat in history:
            user_msg = chat.get("message", "")
            dora_reply = chat.get("reply_message", "")
            if user_msg:
                self.chat_display.append(f"<b>{self.user_name}</b>: {user_msg}<br>")
            if dora_reply:
                self.chat_display.append(
                    f'<b><a href="{dora_reply}">DORA</a></b>: {dora_reply}<br><br>'
                )

    def send_chat_message(self):
        text = self.chat_input.toPlainText().strip()
        if not text:
            return
        self.chat_input.clear()
        response = handle_chat_request(self.user_id, text)
        if response.get("result") == "success":
            self.chat_display.clear()
            self.load_chat_history()
        else:
            QMessageBox.warning(self, "전송 실패", "메시지 전송에 실패했습니다.")

    def handle_enter_key(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter) and not event.modifiers():
            self.send_chat_message()
            event.accept()
        else:
            QTextEdit.keyPressEvent(self.chat_input, event)

    def start_recording(self):
        if not self.mic_enabled:
            QMessageBox.warning(self, "마이크 비활성", "마이크가 꺼져있습니다.")
            return
        self.recorder = LiveAudioRecorder()
        self.recorder.start()
        self.start_voice_btn.setEnabled(False)
        self.stop_voice_btn.setEnabled(True)

    def stop_recording(self):
        self.stop_voice_btn.setEnabled(False)
        try:
            wav_path = self.recorder.stop()
            text = transcribe_audio(wav_path)
            self.chat_input.setText(text)
        except Exception as e:
            QMessageBox.critical(self, "STT 오류", f"음성 인식 실패: {e}")
        finally:
            self.start_voice_btn.setEnabled(True)

    def on_chat_anchor_clicked(self, url: QUrl):
        text = url.toString()
        speak_text_korean(text)

    # --- 웹캠 관련 메서드 ---
    def toggle_camera(self, checked: bool):
        # 외부에 상태 전달
        self.cameraToggled.emit(checked)
        if checked:
            self.start_camera()
        else:
            self.stop_camera()

    def start_camera(self):
        # 웹캠 열기
        self.camera_capture = cv2.VideoCapture(0)
        if not self.camera_capture.isOpened():
            QMessageBox.critical(self, "카메라 오류", "웹캠을 열 수 없습니다.")
            self.camera_checkbox.setChecked(False)
            return
        self.camera_label.setVisible(True)
        # 타이머 시작 (예: 30ms 간격으로 프레임 업데이트)
        self.camera_timer.start(30)
        # 감정 분석 타이머 시작 (예: 1초 간격)
        self.expression_timer.start(1000)

    def stop_camera(self):
        self.camera_timer.stop()
        self.expression_timer.stop()
        if self.camera_capture:
            self.camera_capture.release()
            self.camera_capture = None
        self.camera_label.clear()
        self.camera_label.setVisible(False)

    def update_camera_frame(self):
        if self.camera_capture and self.camera_capture.isOpened():
            ret, frame = self.camera_capture.read()
            if ret:
                # BGR -> RGB 변환
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_frame.shape
                bytes_per_line = ch * w
                qt_image = QImage(
                    rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888
                )
                pixmap = QPixmap.fromImage(qt_image).scaled(
                    self.camera_label.width(), self.camera_label.height(), Qt.KeepAspectRatio
                )
                self.camera_label.setPixmap(pixmap)

    # --- 감정 분석 메서드 ---
    def update_expression_result(self):
        if self.camera_capture and self.camera_capture.isOpened():
            ret, frame = self.camera_capture.read()
            if ret:
                emotion_text = analyze_emotion(frame)
                # 기존에는 self.chat_display.append(...)로 출력했으나, 대신 시그널로 내보냄
                self.expressionDetected.emit(emotion_text)
    
    # --- 마이크 관련 메서드 ---
    def toggle_mic(self, checked: bool):
        self.mic_enabled = checked
        # 외부에 상태 전달
        self.micToggled.emit(checked)
        if checked:
            # 마이크가 켜지면 음성 입력 버튼 활성화
            self.start_voice_btn.setEnabled(True)
        else:
            # 마이크가 꺼지면 음성 입력 버튼 비활성화 및 진행 중이면 중단
            self.start_voice_btn.setEnabled(False)
            self.stop_voice_btn.setEnabled(False)
            if self.recorder is not None:
                try:
                    self.recorder.stop()
                except Exception as e:
                    print("녹음 중지 오류:", e)
                self.recorder = None
