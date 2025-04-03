from PyQt5.QtWidgets import (
    QDialog, QLabel, QLineEdit, QTextEdit, QPushButton,
    QFileDialog, QVBoxLayout, QHBoxLayout, QMessageBox, QListWidget
)
import subprocess  # subprocess 모듈 임포트
from core.controller import handle_set_training_request, handle_get_training_request

class TrainingPopup(QDialog):
    def __init__(self, user_id: int, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.setWindowTitle("훈련 추가")
        self.setFixedSize(500, 650)
        self.init_ui()
        self.load_training_list()

    def init_ui(self):
        layout = QVBoxLayout()

        self.training_text_input = QLineEdit()
        self.training_text_input.setPlaceholderText("훈련 명령어 입력")

        self.keyword_text_input = QLineEdit()
        self.keyword_text_input.setPlaceholderText("키워드 입력 (쉼표로 구분)")

        self.video_path_input = QLineEdit()
        self.video_path_input.setPlaceholderText("제스처 영상 경로")
        browse_btn = QPushButton("찾아보기")
        browse_btn.clicked.connect(self.browse_video_file)
        record_btn = QPushButton("촬영")
        record_btn.clicked.connect(self.record_video)  # 촬영 버튼 클릭 시 record_video 호출

        self.gesture_input = QTextEdit()
        self.gesture_input.setPlaceholderText("훈련시킬 내용을 입력하세요")
        self.gesture_input.setFixedHeight(80)

        save_btn = QPushButton("저장")
        save_btn.clicked.connect(self.save_training)

        self.training_list = QListWidget()

        video_layout = QHBoxLayout()
        video_layout.addWidget(self.video_path_input)
        video_layout.addWidget(browse_btn)
        video_layout.addWidget(record_btn)

        layout.addWidget(QLabel("훈련 명령어"))
        layout.addWidget(self.training_text_input)
        layout.addWidget(QLabel("키워드"))
        layout.addWidget(self.keyword_text_input)
        layout.addWidget(QLabel("제스처 영상 경로"))
        layout.addLayout(video_layout)
        layout.addWidget(QLabel("훈련시킬 내용"))
        layout.addWidget(self.gesture_input)
        layout.addWidget(save_btn)
        layout.addWidget(QLabel("등록된 훈련 목록"))
        layout.addWidget(self.training_list)

        self.setLayout(layout)

    def browse_video_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "제스처 영상 선택", "", "Video Files (*.mp4 *.avi)")
        if file_path:
            self.video_path_input.setText(file_path)

    def record_video(self):
        # 입력된 훈련 명령어(gesture)를 가져옵니다.
        training_command = self.training_text_input.text().strip()
        if not training_command:
            QMessageBox.warning(self, "입력 오류", "먼저 훈련 명령어를 입력하세요.")
            return

        # gesture_train.py 스크립트를 실행합니다.
        # 여기서는 gesture_train.py의 경로가 ./ai/training/gesture_train.py라고 가정합니다.
        try:
            subprocess.Popen(["python", "./ai/gesture_train.py", training_command])
            QMessageBox.information(self, "촬영 시작", "gesture_train.py가 실행되었습니다.\n콘솔에서 진행 상황을 확인하세요.")
        except Exception as e:
            QMessageBox.critical(self, "실행 오류", f"gesture_train.py 실행 중 오류가 발생했습니다:\n{str(e)}")

    def save_training(self):
        text = self.training_text_input.text().strip()
        keyword = self.keyword_text_input.text().strip()
        video_path = self.video_path_input.text().strip()
        gesture = self.gesture_input.toPlainText().strip()

        if not (text and keyword and video_path and gesture):
            QMessageBox.warning(self, "입력 오류", "모든 항목을 입력해야 합니다.")
            return

        response = handle_set_training_request(
            user_id=self.user_id,
            training_text=text,
            keyword_text=keyword,
            gesture_video_path=video_path,
            gesture_recognition_id=0,
            recognized_gesture=gesture
        )

        if response.get("result") == "success":
            QMessageBox.information(self, "저장 완료", "훈련 정보가 저장되었습니다.")
            self.load_training_list()
            self.clear_inputs()
        else:
            QMessageBox.warning(self, "저장 실패", response.get("reason", "알 수 없는 오류입니다."))

    def load_training_list(self):
        self.training_list.clear()
        response = handle_get_training_request(self.user_id)
        if response.get("result") == "success":
            trainings = response.get("data", [])
            for t in trainings:
                text = f"[{t.get('trainingText')}] → {t.get('recognizedGesture')}"
                self.training_list.addItem(text)

    def clear_inputs(self):
        self.training_text_input.clear()
        self.keyword_text_input.clear()
        self.video_path_input.clear()
        self.gesture_input.clear()
