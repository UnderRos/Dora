import sys
import threading
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTabWidget
from views.login_view import LoginView
from network.tcp_server import start_server

class DoraGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Emotion AI GUI")
        self.setGeometry(100, 100, 700, 600)
        self.setStyleSheet(self.load_styles())
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.tabs = QTabWidget()
        self.tabs.addTab(LoginView(), "로그인")
        # self.tabs.addTab(...) # 다른 탭들도 여기에 추가 예정
        layout.addWidget(self.tabs)
        self.setLayout(layout)

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
        """

if __name__ == '__main__':
    # TCP 서버 백그라운드로 실행
    threading.Thread(target=start_server, daemon=True).start()

    app = QApplication(sys.argv)
    window = DoraGUI()
    window.show()
    sys.exit(app.exec_())