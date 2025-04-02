import sys
import threading
import os
import cv2
from PyQt5.QtWidgets import QApplication
from views.main_window import MainWindow
from network.tcp_server import start_server

qt_plugin_path = os.path.join(os.path.dirname(cv2.__file__), 'qt', 'plugins')
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = qt_plugin_path

if __name__ == '__main__':
    threading.Thread(target=start_server, daemon=True).start()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

