import threading
import cv2
import json
import socket
from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QTextBrowser, QPushButton,
    QCheckBox, QMessageBox, QLabel, QApplication
)
from PyQt5.QtCore import Qt, QUrl, QTimer, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QImage, QPixmap, QTextCursor
from db.query import get_recent_chats, insert_chat
from ai.stt_wrapper import transcribe_audio
from ai.tts_wrapper import speak_text_korean
from common.recorder import LiveAudioRecorder
from db.models import Chat
from markdown2 import markdown

from .webcam_emotion import analyze_emotion

class ChatPanel(QWidget):
    expressionDetected = pyqtSignal(str)
    cameraToggled = pyqtSignal(bool)
    micToggled = pyqtSignal(bool)

    dolbomMessageReceived = pyqtSignal(str, bool)

    chatRefreshRequested = pyqtSignal()

    def __init__(self, user_id: int, user_name: str):
        super().__init__()
        self.user_id = user_id
        self.user_name = user_name
        self.recorder = None
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.connect(("127.0.0.1", 9000))

        self.camera_capture = None
        self.camera_timer = QTimer(self)
        self.camera_timer.timeout.connect(self.update_camera_frame)
        self.expression_timer = QTimer(self)
        self.expression_timer.timeout.connect(self.update_expression_result)

        self.mic_enabled = False

        self.last_block_cursor = None

        self.dolbom_started = False
        self.reply_accumulator = ""

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
        toggles.addWidget(self.camera_checkbox)
        toggles.addWidget(self.mic_checkbox)

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

    def refresh_chat_display(self):
        self.chat_display.clear()
        self.load_chat_history()

    def load_chat_history(self):
        history = get_recent_chats(self.user_id, limit=20)
        self.chat_display.clear()
        for chat in history:
            user_msg = chat.get("message", "")
            dolbom_reply = chat.get("reply_message", "")
            if user_msg:
                self.chat_display.append(f"<b>{self.user_name}</b>: {user_msg}<br>")
            if dolbom_reply:
                html = markdown(dolbom_reply).replace("\n", "<br>")
                self.chat_display.append(f'<b><a href="{dolbom_reply}">Dolbom</a></b>:<br>{html}<br><br>')

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
            QMessageBox.critical(self, "전송 오류", f"서버에 메시지를 보낼 수 없습니다.\n{e}")
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
                        chunk = msg["chunk"]
                        self.dolbomMessageReceived.emit(chunk, True)
                        QApplication.processEvents()

                    elif msg.get("type") == "stream_done":
                        full_reply = self.reply_accumulator  # 저장된 전체 응답
                        self.dolbomMessageReceived.emit(full_reply, False)

                        chat = Chat(
                            chat_id=None,
                            user_id=self.user_id,
                            message_id=None,
                            message=self.last_user_message,
                            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            video_id=None, video_path=None,
                            video_start_timestamp=None, video_end_timestamp=None,
                            voice_id=None, voice_path=None,
                            voice_start_timestamp=None, voice_end_timestamp=None,
                            e_id=msg.get("eId", 5),
                            pet_emotion=msg.get("petEmotion", "기분 좋아요"),
                            reply_message=full_reply
                        )
                        insert_chat(chat)

                        self.chatRefreshRequested.emit()

                        return
                    
            except Exception as e:
                print("[ChatPanel] stream 수신 오류:", e)
                break




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
            existing_text = self.chat_input.toPlainText()
            self.chat_input.setText(existing_text + " " + text)
        except Exception as e:
            QMessageBox.critical(self, "STT 오류", f"음성 인식 실패: {e}")
        finally:
            self.start_voice_btn.setEnabled(True)

    def on_chat_anchor_clicked(self, url: QUrl):
        text = url.toString()
        speak_text_korean(text)

    def toggle_camera(self, checked: bool):
        self.cameraToggled.emit(checked)
        if checked:
            self.start_camera()
        else:
            self.stop_camera()

    def start_camera(self):
        self.camera_capture = cv2.VideoCapture(0)
        if not self.camera_capture.isOpened():
            QMessageBox.critical(self, "카메라 오류", "웹캠을 열 수 없습니다.")
            self.camera_checkbox.setChecked(False)
            return
        self.camera_label.setVisible(True)
        self.camera_timer.start(30)
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

    def update_expression_result(self):
        if self.camera_capture and self.camera_capture.isOpened():
            ret, frame = self.camera_capture.read()
            if ret:
                emotion_text = analyze_emotion(frame)
                self.expressionDetected.emit(emotion_text)

    def toggle_mic(self, checked: bool):
        self.mic_enabled = checked
        self.micToggled.emit(checked)
        if checked:
            self.start_voice_btn.setEnabled(True)
        else:
            self.start_voice_btn.setEnabled(False)
            self.stop_voice_btn.setEnabled(False)
            if self.recorder is not None:
                try:
                    self.recorder.stop()
                except Exception as e:
                    print("녹음 중지 오류:", e)
                self.recorder = None
