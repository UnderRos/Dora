from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QComboBox, QTextEdit, QPushButton, QMessageBox
from core.controller import handle_get_character_request, handle_set_character_request
from views.training_popup import TrainingPopup

class PetPanel(QWidget):
    def __init__(self, user_id: int):
        super().__init__()
        self.user_id = user_id
        self.init_ui()
        self.load_character_setting()

    def init_ui(self):
        layout = QVBoxLayout()

        self.speech_combo = QComboBox()
        self.speech_combo.addItems(["존댓말", "반말"])

        self.character_combo = QComboBox()
        self.character_combo.addItems(["내향적", "외향적"])

        self.res_text = QTextEdit()
        self.res_text.setPlaceholderText("권장 혹은 기피 행동 등 특이사항을 입력하세요")

        save_button = QPushButton("설정 저장")
        save_button.clicked.connect(self.save_setting)

        layout.addWidget(QLabel("말투 설정"))
        layout.addWidget(self.speech_combo)
        layout.addWidget(QLabel("성격 설정"))
        layout.addWidget(self.character_combo)
        layout.addWidget(QLabel("기타 설정"))
        layout.addWidget(self.res_text)
        layout.addWidget(save_button)

        train_button = QPushButton("훈련 추가")
        train_button.clicked.connect(self.open_training_popup)
        layout.addWidget(train_button)


        self.setLayout(layout)

    def load_character_setting(self):
        response = handle_get_character_request(self.user_id)

        # 설정 없는 경우: 기본값 사용
        if response.get("result") == "success":
            speech = response.get("speech", "존댓말")
            character = response.get("character", "내향적")
            res_setting = response.get("resSetting", "")
        else:
            speech = "존댓말"
            character = "내향적"
            res_setting = ""
            return

        # 공통 적용
        self.speech_combo.setCurrentText(speech)
        self.character_combo.setCurrentText(character)
        self.res_text.setPlainText(res_setting)

    def save_setting(self):
        speech = self.speech_combo.currentText()
        character = self.character_combo.currentText()
        res_setting = self.res_text.toPlainText()

        response = handle_set_character_request(self.user_id, speech, character, res_setting)
        if response.get("result") == "success":
            QMessageBox.information(self, "설정 저장", "DORA 설정이 저장되었습니다.")
        else:
            QMessageBox.warning(self, "설정 실패", response.get("reason", "저장에 실패했습니다."))


    def open_training_popup(self):
        popup = TrainingPopup(self.user_id, self)
        popup.exec_()
