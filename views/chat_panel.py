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

    def toggle_gesture(self, checked: bool):
        self.gestureToggled.emit(checked)
        if checked:
            try:
                self.gesture_process = subprocess.Popen(["python", "./ai/gesture_recognize.py"])
                print("제스처 인식 프로세스 시작됨")
            except Exception as e:
                QMessageBox.critical(self, "제스처 인식 오류", f"제스처 인식 스크립트 실행 중 오류 발생:\n{str(e)}")
        else:
            if self.gesture_process is not None:
                self.gesture_process.terminate()
                self.gesture_process = None
                print("제스처 인식 프로세스 종료됨")

    def toggle_camera(self, checked: bool):
        self.cameraToggled.emit(checked)
        if checked:
            self.start_camera()
        else:
            self.stop_camera()

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
                    elif msg.get("type") == "stream_done":
                        full_reply = self.reply_accumulator
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
                            voiceStartTimestamp=None, voiceEndTimestamp=None,
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

    def on_chat_anchor_clicked(self, url: QUrl):
        text = url.toString()
        speak_text_korean(text)

    def start_camera(self):
        try:
            self.camera_manager = CameraManager.instance()
        except RuntimeError as e:
            QMessageBox.critical(self, "카메라 오류", str(e))
            self.camera_checkbox.setChecked(False)
            return
        self.camera_label.setVisible(True)
        self.camera_manager.add_frame_callback(self.update_camera_frame)
        self.camera_manager.start()

    def stop_camera(self):
        if self.camera_manager is not None:
            self.camera_manager.remove_frame_callback(self.update_camera_frame)
        self.camera_label.clear()
        self.camera_label.setVisible(False)

    def update_camera_frame(self, frame):
        if frame is not None:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
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
            user_msg = chat.get("message", "")
            dolbom_reply = chat.get("reply_message", "")
            if user_msg:
                self.chat_display.append(f"<b>{self.user_name}</b>: {user_msg}<br>")
            if dolbom_reply:
                html = markdown(dolbom_reply).replace("\n", "<br>")
                self.chat_display.append(f'<b><a href="{dolbom_reply}">Dolbom</a></b>:<br>{html}<br><br>')

    def refresh_chat_display(self):
        self.chat_display.clear()
        self.load_chat_history()

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    panel = ChatPanel(user_id=1, user_name="User1")
    panel.show()
    sys.exit(app.exec_())
