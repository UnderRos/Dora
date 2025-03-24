import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QLineEdit, QTextEdit, QTabWidget, QSlider, QCheckBox, QDialog, QFormLayout,
    QFrame, QSizePolicy, QSpacerItem
)
from PyQt5.QtCore import Qt

class SignUpDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("회원가입")
        self.setGeometry(200, 200, 350, 250)
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
                border: 1px solid #ccc;
                border-radius: 10px;
            }
            QLabel {
                font-size: 14px;
                margin-bottom: 5px;
            }
            QLineEdit {
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 6px;
                margin-bottom: 10px;
            }
            QPushButton {
                background-color: #4a90e2;
                color: white;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #357abd;
            }
        """)
        layout = QFormLayout()
        layout.addRow("이름", QLineEdit())
        layout.addRow("ID", QLineEdit())
        layout.addRow("비밀번호", QLineEdit())
        layout.addRow("전화번호", QLineEdit())
        layout.addWidget(QPushButton("회원가입 완료", self))
        self.setLayout(layout)

class EmotionAIGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Emotion AI GUI")
        self.setGeometry(100, 100, 700, 600)
        self.setStyleSheet(self.load_styles())

        layout = QVBoxLayout()
        self.tabs = QTabWidget()
        self.tabs.addTab(self.login_tab_ui(), "🔐 로그인")
        self.tabs.addTab(self.emotion_tab_ui(), "💖 건강 상태")
        self.tabs.addTab(self.robot_tab_ui(), "🤖 펫 상태")
        self.tabs.addTab(self.chat_tab_ui(), "💬 채팅")
        self.tabs.addTab(self.settings_tab_ui(), "⚙️ 설정")

        layout.addWidget(self.tabs)
        self.setLayout(layout)

    def login_tab_ui(self):
        tab = QWidget()
        layout = QVBoxLayout()

        login_box = QFrame()
        login_box.setObjectName("LoginBox")
        login_layout = QVBoxLayout()
        login_layout.setSpacing(12)

        id_input = QLineEdit()
        id_input.setPlaceholderText("👤 아이디를 입력하세요")

        pw_input = QLineEdit()
        pw_input.setPlaceholderText("🔒 비밀번호를 입력하세요")
        pw_input.setEchoMode(QLineEdit.Password)

        login_btn = QPushButton("로그인")
        login_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        signup_layout = QHBoxLayout()
        signup_layout.addStretch()
        signup_label = QLabel("계정이 없으신가요?")
        signup_link = QPushButton("회원가입")
        signup_link.setObjectName("LinkButton")
        signup_link.clicked.connect(self.show_signup_dialog)
        signup_layout.addWidget(signup_label)
        signup_layout.addWidget(signup_link)
        signup_layout.addStretch()

        login_layout.addWidget(id_input)
        login_layout.addWidget(pw_input)
        login_layout.addWidget(login_btn)
        login_layout.addLayout(signup_layout)

        login_box.setLayout(login_layout)
        layout.addStretch()
        layout.addWidget(login_box, alignment=Qt.AlignCenter)
        layout.addStretch()

        tab.setLayout(layout)
        return tab

    def show_signup_dialog(self):
        dialog = SignUpDialog()
        dialog.exec_()

    def emotion_tab_ui(self):
        tab = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.label("오늘의 감정: 😊 행복", size=16))
        layout.addWidget(self.label("어제보다 긍정적인 변화가 감지되었습니다."))
        layout.addWidget(self.label("최근 목소리: 밝음"))
        tab.setLayout(layout)
        return tab

    def robot_tab_ui(self):
        tab = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.label("상태: 😿 심심해요"))
        layout.addWidget(self.label("함께한지 5일째"))
        layout.addWidget(self.label("생일까지 10일 남음"))
        layout.addWidget(self.label("말투: 반말 / 성격: 외향적"))
        layout.addWidget(QTextEdit("기타 정보 (예: 알레르기 등)"))
        tab.setLayout(layout)
        return tab

    def chat_tab_ui(self):
        tab = QWidget()
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setPlaceholderText("여기에 대화 내용이 표시됩니다...")

        self.chat_input = QTextEdit()
        self.chat_input.setPlaceholderText("메시지를 입력하세요...")
        self.chat_input.setFixedHeight(60)
        self.chat_input.keyPressEvent = self.handle_enter_key

        send_button = QPushButton("전송")
        send_button.clicked.connect(self.send_chat_message)

        input_layout = QHBoxLayout()
        input_layout.addWidget(self.chat_input)
        input_layout.addWidget(send_button)

        layout = QVBoxLayout()
        toggles = QHBoxLayout()
        toggles.addWidget(QCheckBox("카메라 ON"))
        toggles.addWidget(QCheckBox("마이크 ON"))
        toggles.addWidget(QCheckBox("스피커 ON"))
        layout.addLayout(toggles)

        layout.addWidget(self.chat_display)
        layout.addLayout(input_layout)
        tab.setLayout(layout)
        return tab

    def send_chat_message(self):
        text = self.chat_input.toPlainText().strip()
        if text:
            self.chat_display.append(f"👤 나: {text}")
            self.chat_input.clear()
            self.chat_display.append(f"🤖 펫: '{text}'에 대해 더 알고 싶어요!")

    def handle_enter_key(self, event):
        if event.key() == Qt.Key_Return and not event.modifiers():
            self.send_chat_message()
        else:
            QTextEdit.keyPressEvent(self.chat_input, event)

    def settings_tab_ui(self):
        tab = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.label("텍스트 크기 조절"))
        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(12)
        slider.setMaximum(24)
        layout.addWidget(slider)
        layout.addWidget(QPushButton("연결된 보호자 보기"))
        layout.addWidget(QPushButton("연결 끊기"))
        tab.setLayout(layout)
        return tab

    def label(self, text, size=14, color="#333"):
        label = QLabel(text)
        label.setStyleSheet(f"font-size: {size}px; color: {color}; margin: 5px;")
        return label

    def load_styles(self):
        return """
            QWidget {
                background-color: #f9f9fb;
                font-family: 'Segoe UI', sans-serif;
            }
            QTabWidget::pane {
                border: 1px solid #ccc;
                background: #fff;
                border-radius: 10px;
            }
            QTabBar::tab {
                background: #eee;
                border: 1px solid #ccc;
                padding: 8px 16px;
                margin: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }
            QTabBar::tab:selected {
                background: #fff;
                font-weight: bold;
            }
            QLineEdit, QTextEdit {
                border: 1px solid #ccc;
                border-radius: 6px;
                padding: 8px;
                font-size: 14px;
                background-color: #fff;
            }
            QPushButton {
                background-color: #4a90e2;
                color: white;
                border-radius: 6px;
                padding: 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #357abd;
            }
            QPushButton#LinkButton {
                background: transparent;
                color: #4a90e2;
                border: none;
                text-decoration: underline;
                font-size: 13px;
            }
            QCheckBox {
                font-size: 13px;
                margin-right: 10px;
            }
            QSlider {
                margin: 10px 0;
            }
            QFrame#LoginBox {
                background: #fff;
                border: 1px solid #ccc;
                border-radius: 10px;
                padding: 30px;
                max-width: 500px;
                min-width: 400px;
                margin-left: auto;
                margin-right: auto;
            }
        """

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = EmotionAIGUI()
    window.show()
    sys.exit(app.exec_())