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

