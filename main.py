import sys
import threading
from PyQt5.QtWidgets import QApplication
from views.main_window import MainWindow
from network.tcp_server import start_server

if __name__ == '__main__':
    threading.Thread(target=start_server, daemon=True).start()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
