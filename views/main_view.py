from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from views.chat_panel import ChatPanel
from views.pet_panel import PetPanel
from views.user_status_panel import UserPanel
from views.setting_panel import SettingPanel

class MainView(QWidget):
    def __init__(self, user_id, user_name):
        super().__init__()
        layout = QVBoxLayout()
        tabs = QTabWidget()
        tabs.addTab(UserPanel(user_id=user_id), "나의 상태")
        tabs.addTab(PetPanel(user_id=user_id), "DORA 상태")
        tabs.addTab(ChatPanel(user_id=user_id, user_name=user_name), "채팅")
        tabs.addTab(SettingPanel(user_id=user_id), "설정")
        layout.addWidget(tabs)
        self.setLayout(layout)
