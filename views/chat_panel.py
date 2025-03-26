from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QTextBrowser, QPushButton, QCheckBox, QMessageBox
from PyQt5.QtCore import Qt, QUrl
from core.controller import handle_chat_request
from db.query import get_recent_chats
from ai.stt_wrapper import transcribe_audio
from ai.tts_wrapper import speak_text_korean
from common.recorder import LiveAudioRecorder


class ChatPanel(QWidget):
    def __init__(self, user_id: int, user_name: str):
        super().__init__()
        self.user_id = user_id
        self.user_name = user_name
        self.recorder = None
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

        toggles = QHBoxLayout()
        toggles.addWidget(QCheckBox("카메라 ON"))
        toggles.addWidget(QCheckBox("마이크 ON"))

        input_layout = QHBoxLayout()
        input_layout.addWidget(self.chat_input)
        input_layout.addWidget(send_button)

        layout.addLayout(toggles)
        layout.addWidget(self.chat_display)
        layout.addLayout(input_layout)

        # 음성 제어 버튼
        self.start_voice_btn = QPushButton("음성 입력 시작")
        self.stop_voice_btn = QPushButton("음성 입력 종료")
        self.stop_voice_btn.setEnabled(False)

        self.start_voice_btn.clicked.connect(self.start_recording)
        self.stop_voice_btn.clicked.connect(self.stop_recording)

        voice_btns = QHBoxLayout()
        voice_btns.addWidget(self.start_voice_btn)
        voice_btns.addWidget(self.stop_voice_btn)
        layout.addLayout(voice_btns)

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
