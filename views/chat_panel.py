from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QCheckBox
from PyQt5.QtCore import Qt
from core.controller import handle_chat_request

class ChatPanel(QWidget):
    def __init__(self, user_id: int, user_name: str):
        super().__init__()
        self.user_id = user_id
        self.user_name = user_name
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
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
        toggles.addWidget(QCheckBox("스피커 ON"))

        input_layout = QHBoxLayout()
        input_layout.addWidget(self.chat_input)
        input_layout.addWidget(send_button)

        layout.addLayout(toggles)
        layout.addWidget(self.chat_display)
        layout.addLayout(input_layout)
        self.setLayout(layout)

    def send_chat_message(self):
        text = self.chat_input.toPlainText().strip()
        if text:
            self.chat_display.append(f"<b>{self.user_name}</b>: {text}<br>")
            self.chat_input.clear()
            response = handle_chat_request(self.user_id, text)
            reply = response.get("replyMessage", "...")
            pet_emotion = response.get("petEmotion", "")
            self.chat_display.append(f"<b>DORA</b>: {self.reply_message}<br><br>")

    def handle_enter_key(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter) and not event.modifiers():
            self.send_chat_message()
            event.accept()
        else:
            QTextEdit.keyPressEvent(self.chat_input, event)


