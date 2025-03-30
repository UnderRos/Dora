import os
from PyQt5.QtWidgets import QMainWindow
from views.login_view import LoginView
from views.main_view import MainView
from core.controller import handle_get_setting_request

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Emotion AI GUI")
        self.setGeometry(100, 100, 700, 800)

        self.user_id = None
        self.user_name = None
        self.login_view = LoginView(self.on_login_success)
        self.setCentralWidget(self.login_view)

    def on_login_success(self, user_id, user_name):
        self.user_id = user_id
        self.user_name = user_name

        font_size = self.load_user_font_size(user_id)
        style = self.load_styles_with_font(font_size)
        self.setStyleSheet(style)

        self.main_view = MainView(user_id, user_name)
        self.setCentralWidget(self.main_view)

    def load_user_font_size(self, user_id):
        response = handle_get_setting_request(user_id)
        if response.get("result") == "success":
            return response.get("fontSize", 14)
        return 14

    def load_styles_with_font(self, font_size):
        try:
            style_path = os.path.join(os.path.dirname(__file__), "style.qss")
            with open(style_path, "r", encoding="utf-8") as f:
                qss = f.read()
            return qss.replace("{FONT_SIZE}", str(font_size))
        except Exception as e:
            print(f"[Style] 스타일 로딩 실패: {e}")
            return ""