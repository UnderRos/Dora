# chat_panel.py (통합 버전)

import threading
import cv2
import json
import socket
import os
from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QTextBrowser, QPushButton,
    QCheckBox, QMessageBox, QLabel, QApplication
)
from PyQt5.QtCore import Qt, QUrl, QTimer, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QImage, QPixmap, QTextCursor
from db.query import get_recent_chats, insert_chat
# from ai.stt_wrapper import transcribe_audio  # STT 임시 비활성화
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
    gestureToggled = pyqtSignal(bool)
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

        self.camera_manager = None
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

    def on_chat_anchor_clicked(self, url: QUrl):
        text = url.toString()
        speak_text_korean(text)

    def init_ui(self):
        layout = QVBoxLayout()

        self.chat_display = QTextBrowser()
        self.chat_display.setOpenLinks(False)
        self.chat_display.anchorClicked.connect(self.on_chat_anchor_clicked)
        self.chat_display.setPlaceholderText("여기에 대화 내용이 표시됩니다...")

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

    def toggle_gesture(self, checked: bool):
        self.gestureToggled.emit(checked)
        if checked:
            try:
                self.gesture_process = subprocess.Popen(["python", "./ai/gesture_recognize.py"])
            except Exception as e:
                QMessageBox.critical(self, "제스처 오류", str(e))
        elif self.gesture_process:
            self.gesture_process.terminate()
            self.gesture_process = None

    def toggle_camera(self, checked: bool):
        self.cameraToggled.emit(checked)
        if checked:
            self.start_camera()
        else:
            self.stop_camera()

    def toggle_mic(self, checked: bool):
        self.mic_enabled = checked
        self.micToggled.emit(checked)
        self.start_voice_btn.setEnabled(checked)
        if not checked:
            self.stop_voice_btn.setEnabled(False)
            if self.recorder:
                try:
                    self.recorder.stop()
                except Exception as e:
                    print("녹음 중지 오류:", e)
                self.recorder = None

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
            if not self.recorder:
                print("[녹음기] recorder is None — 종료 생략")
                return

            wav_path = self.recorder.stop()
            self.recorder = None

            if not wav_path or not os.path.exists(wav_path):
                raise FileNotFoundError("녹음된 음성 파일이 없습니다.")

            try:
                audio_np, sr = librosa.load(wav_path, sr=16000)
            except Exception as e:
                raise RuntimeError(f"오디오 파일 로딩 실패: {e}")

            emotion, conf = predict_emotion(audio_np)
            print(f"[음성 감정 분석] 감정: {emotion}, 신뢰도: {conf:.2f}")
            if not np.isnan(conf):
                self.chat_display.append(f"<span style='color:gray;'>[감정 분석] {emotion} ({conf*100:.1f}%)</span>")
            else:
                self.chat_display.append("<span style='color:gray;'>[감정 분석 실패]</span>")

        except Exception as e:
            print("[녹음 오류]", e)
            QMessageBox.critical(self, "감정 분석 오류", f"오류 발생: {e}")
        finally:
            self.start_voice_btn.setEnabled(True)

    def send_chat_message(self):
        user_input = self.chat_input.toPlainText().strip()
        if not user_input:
            return
        self.chat_input.clear()
        self.chat_display.append(f"<b>{self.user_name}</b>: {user_input}<br>")
        self.last_user_message = user_input
        self.partial_buffer = ""

        message_data = {
            "command": "send_message",
            "payload": {
                "userId": self.user_id,
                "messageId": 0,
                "message": user_input,
                "timestamp": "",
                "videoId": 0,
                "videoPath": "",
                "videoStartTimestamp": "",
                "videoEndTimestamp": "",
                "voiceId": 0,
                "voicePath": "",
                "voiceStartTimestamp": "",
                "voiceEndTimestamp": ""
            }
        }

        try:
            self.conn.sendall(json.dumps(message_data).encode("utf-8"))
        except Exception as e:
            QMessageBox.critical(self, "전송 오류", str(e))
            return

        threading.Thread(target=self.handle_stream_response, daemon=True).start()

    @pyqtSlot(str, bool)
    def append_dolbom_message(self, content: str, partial: bool = True):
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.End)
        if partial:
            if not self.dolbom_started:
                self.chat_display.append("Dolbom: ")
                self.dolbom_started = True
            self.reply_accumulator += content
            cursor.insertText(content)
            self.chat_display.setTextCursor(cursor)
        else:
            self.dolbom_started = False
            self.reply_accumulator = ""

    def handle_stream_response(self):
        buffer = ""
        while True:
            try:
                data = self.conn.recv(4096)
                if not data:
                    break
                buffer += data.decode("utf-8")
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    if not line.strip():
                        continue
                    msg = json.loads(line)
                    if msg.get("type") == "stream_chunk":
                        self.dolbomMessageReceived.emit(msg["chunk"], True)
                    elif msg.get("type") == "stream_done":
                        self.dolbomMessageReceived.emit(self.reply_accumulator, False)
                        insert_chat(Chat(
                            chat_id=None, user_id=self.user_id,
                            message_id=None, message=self.last_user_message,
                            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            video_id=None, video_path=None,
                            video_start_timestamp=None, video_end_timestamp=None,
                            voice_id=None, voice_path=None,
                            voiceStartTimestamp=None, voiceEndTimestamp=None,
                            e_id=msg.get("eId", 5),
                            pet_emotion=msg.get("petEmotion", "기분 좋아요"),
                            reply_message=self.reply_accumulator
                        ))
                        self.chatRefreshRequested.emit()
                        return
            except Exception as e:
                print("[stream 수신 오류]", e)
                break

    def handle_enter_key(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter) and not event.modifiers():
            self.send_chat_message()
            event.accept()
        else:
            QTextEdit.keyPressEvent(self.chat_input, event)

    def start_camera(self):
        try:
            self.camera_manager = CameraManager.instance()
            self.camera_label.setVisible(True)
            self.camera_manager.add_frame_callback(self.update_camera_frame)
            self.camera_manager.start()
        except RuntimeError as e:
            QMessageBox.critical(self, "카메라 오류", str(e))
            self.camera_checkbox.setChecked(False)

    def stop_camera(self):
        if self.camera_manager:
            self.camera_manager.remove_frame_callback(self.update_camera_frame)
        self.camera_label.clear()
        self.camera_label.setVisible(False)

    def update_camera_frame(self, frame):
        if frame is not None:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            qt_image = QImage(rgb_frame.data, w, h, ch * w, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qt_image).scaled(
                self.camera_label.width(), self.camera_label.height(), Qt.KeepAspectRatio
            )
            self.camera_label.setPixmap(pixmap)
            current_time = datetime.now().timestamp()
            if current_time - self.last_emotion_update >= 1:
                summary = analyze_webcam_emotion(frame)
                self.expressionDetected.emit(summary)
                self.last_emotion_update = current_time

    def load_chat_history(self):
        history = get_recent_chats(self.user_id, limit=20)
        self.chat_display.clear()
        for chat in history:
            if msg := chat.get("message"):
                self.chat_display.append(f"<b>{self.user_name}</b>: {msg}<br>")
            if reply := chat.get("reply_message"):
                html = markdown(reply).replace("\n", "<br>")
                self.chat_display.append(f'<b><a href="{reply}">Dolbom</a></b>:<br>{html}<br><br>')

    def refresh_chat_display(self):
        self.chat_display.clear()
        self.load_chat_history()


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    panel = ChatPanel(user_id=1, user_name="User1")
    panel.show()
    sys.exit(app.exec_())
