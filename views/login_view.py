import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QFrame, QLineEdit, QPushButton, QHBoxLayout, QLabel, QSizePolicy, QMessageBox
from PyQt5.QtCore import Qt
from views.components.signup_dialog import SignUpDialog
from core.controller import handle_login_request

class LoginView(QWidget):
    def __init__(self, login_callback=None):
        super().__init__()
        self.login_callback = login_callback
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

        # 개발 모드일 경우 백도어 로그인 버튼 추가
        if os.getenv("DEV_MODE", "false").lower() == "true":
            backdoor_btn = QPushButton("백도어 로그인")
            backdoor_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            backdoor_btn.clicked.connect(self.handle_backdoor_login)
            login_layout.addWidget(backdoor_btn)

        login_box.setLayout(login_layout)

        layout.addStretch()
        layout.addWidget(login_box, alignment=Qt.AlignCenter)
        layout.addStretch()

        self.setLayout(layout)
        
    def handle_login(self):
        email = self.id_input.text().strip()
        password = self.pw_input.text().strip()
        if email and password:
            response = handle_login_request(email, password)
            if response.get("result") == "success":
                QMessageBox.information(self, "로그인 성공", "로그인에 성공했습니다.")
                if self.login_callback:
                    self.login_callback(response["userId"], email)  # 또는 닉네임으로 교체 가능
            else:
                QMessageBox.warning(self, "로그인 실패", response.get("reason", "로그인에 실패했습니다."))
        else:
            QMessageBox.warning(self, "입력 오류", "아이디와 비밀번호를 모두 입력하세요.")

    def handle_backdoor_login(self):
        
        # 개발 모드에서만 사용 가능한 백도어 로그인.
        # 클릭 시 임의의 userId와 이메일을 사용하여 바로 로그인된 것처럼 처리합니다.
        user_id = 1
        email = "dev@example.com"
        QMessageBox.information(self, "백도어 로그인", "개발 모드에서 백도어 로그인이 실행되었습니다.")
        if self.login_callback:
            self.login_callback(user_id, email)

    def show_signup_dialog(self):
        dialog = SignUpDialog()
        dialog.exec_()

    def load_styles(self):
        try:
            style_path = os.path.join(os.path.dirname(__file__), "style.qss")
            with open(style_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            print(f"[Style] 스타일 로딩 실패: {e}")
            return ""
