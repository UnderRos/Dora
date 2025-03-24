from PyQt5.QtWidgets import QWidget, QVBoxLayout, QFrame, QLineEdit, QPushButton, QHBoxLayout, QLabel, QSizePolicy
from PyQt5.QtCore import Qt
from components.signup_dialog import SignUpDialog
from controller import handle_login_request

class LoginView(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(self.load_styles())
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        login_box = QFrame()
        login_box.setObjectName("LoginBox")
        login_layout = QVBoxLayout()
        login_layout.setSpacing(12)

        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("아이디를 입력하세요")

        self.pw_input = QLineEdit()
        self.pw_input.setPlaceholderText("비밀번호를 입력하세요")
        self.pw_input.setEchoMode(QLineEdit.Password)

        login_btn = QPushButton("로그인")
        login_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        login_btn.clicked.connect(self.handle_login)

        signup_layout = QHBoxLayout()
        signup_layout.addStretch()
        signup_label = QLabel("계정이 없으신가요?")
        signup_link = QPushButton("회원가입")
        signup_link.setObjectName("LinkButton")
        signup_link.clicked.connect(self.show_signup_dialog)
        signup_layout.addWidget(signup_label)
        signup_layout.addWidget(signup_link)
        signup_layout.addStretch()

        login_layout.addWidget(self.id_input)
        login_layout.addWidget(self.pw_input)
        login_layout.addWidget(login_btn)
        login_layout.addLayout(signup_layout)

        login_box.setLayout(login_layout)

        layout.addStretch()
        layout.addWidget(login_box, alignment=Qt.AlignCenter)
        layout.addStretch()

        self.setLayout(layout)

    def handle_login(self):
        email = self.id_input.text().strip()
        password = self.pw_input.text().strip()
        if email and password:
            handle_login_request(email, password)

    def show_signup_dialog(self):
        dialog = SignUpDialog()
        dialog.exec_()

    def load_styles(self):
        return '''
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
            QPushButton#LinkButton {
                background: transparent;
                color: #4a90e2;
                border: none;
                text-decoration: underline;
                font-size: 13px;
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
        '''
