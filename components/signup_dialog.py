from PyQt5.QtWidgets import QDialog, QFormLayout, QLineEdit, QPushButton
from controller import handle_signup_request

class SignUpDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("회원가입")
        self.setGeometry(200, 200, 350, 250)
        self.setStyleSheet(self.load_styles())
        self.init_ui()

    def init_ui(self):
        self.layout = QFormLayout()

        self.name_input = QLineEdit()
        self.id_input = QLineEdit()
        self.pw_input = QLineEdit()
        self.pw_input.setEchoMode(QLineEdit.Password)
        self.phone_input = QLineEdit()

        self.layout.addRow("이름", self.name_input)
        self.layout.addRow("ID (이메일)", self.id_input)
        self.layout.addRow("비밀번호", self.pw_input)
        self.layout.addRow("전화번호", self.phone_input)

        signup_btn = QPushButton("회원가입 완료")
        signup_btn.clicked.connect(self.submit_signup)
        self.layout.addWidget(signup_btn)

        self.setLayout(self.layout)

    def submit_signup(self):
        name = self.name_input.text().strip()
        email = self.id_input.text().strip()
        password = self.pw_input.text().strip()
        nickname = self.phone_input.text().strip()  # 전화번호 대신 nickname 활용

        if name and email and password:
            handle_signup_request(name, nickname, email, password)
            self.accept()

    def load_styles(self):
        return """
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
        """
