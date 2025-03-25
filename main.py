import os
import sys
import threading
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTabWidget, QLabel
from PyQt5.QtCore import Qt
from views.login_view import LoginView
from views.chat_panel import ChatPanel
from network.tcp_server import start_server

class DoraGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Emotion AI GUI")
        self.setGeometry(100, 100, 700, 600)
        self.setStyleSheet(self.load_styles())
        self.user_id = None
        self.user_name = None
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.show_login_view()

    def show_login_view(self):
        self.login_view = LoginView(login_callback=self.on_login_success)
        self.layout.addWidget(self.login_view)

    def show_main_tabs(self):
        self.tabs = QTabWidget()
        self.tabs.addTab(QLabel("건강 상태 탭 (미구현)"), "건강 상태")
        self.tabs.addTab(QLabel("DORA 상태 탭 (미구현)"), "DORA 상태")
        self.tabs.addTab(ChatPanel(user_id=self.user_id, user_name=self.user_name), "채팅")
        self.tabs.addTab(QLabel("설정 탭 (미구현)"), "설정")
        self.layout.addWidget(self.tabs)
        self.tabs.setCurrentIndex(2)

    def on_login_success(self, user_id, user_name):
        self.user_id = user_id
        self.user_name = user_name
        self.layout.removeWidget(self.login_view)
        self.login_view.deleteLater()
        self.show_main_tabs()

    def load_styles(self):
        try:
            style_path = os.path.join(os.path.dirname(__file__), "views", "style.qss")
            with open(style_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            print(f"[Style] 스타일 로딩 실패: {e}")
            return ""

if __name__ == '__main__':
    threading.Thread(target=start_server, daemon=True).start()
    app = QApplication(sys.argv)
    window = DoraGUI()
    window.show()
    sys.exit(app.exec_())
