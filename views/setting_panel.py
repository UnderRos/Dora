from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QComboBox, QPushButton, QMessageBox
)
from core.controller import handle_get_setting_request, handle_set_setting_request

class SettingPanel(QWidget):
    def __init__(self, user_id: int):
        super().__init__()
        self.user_id = user_id
        self.init_ui()
        self.load_setting()

    def init_ui(self):
        layout = QVBoxLayout()

        self.font_size_combo = QComboBox()
        self.font_size_combo.addItems([str(size) for size in range(10, 31)])

        save_btn = QPushButton("저장")
        save_btn.clicked.connect(self.save_setting)

        layout.addWidget(QLabel("폰트 크기 설정"))
        layout.addWidget(self.font_size_combo)
        layout.addWidget(save_btn)

        self.setLayout(layout)

    def load_setting(self):
        response = handle_get_setting_request(self.user_id)
        if response.get("result") == "success":
            font_size = response.get("fontSize", 14)
            self.font_size_combo.setCurrentText(str(font_size))
        else:
            print("[설정] 사용자 설정 불러오기 실패")

    def save_setting(self):
        font_size = int(self.font_size_combo.currentText())
        response = handle_set_setting_request(self.user_id, font_size)
        if response.get("result") == "success":
            QMessageBox.information(self, "저장 완료", "설정이 저장되었습니다. 다음 접속부터 적용됩니다.")
        else:
            QMessageBox.warning(self, "저장 실패", response.get("reason", "저장에 실패했습니다."))
