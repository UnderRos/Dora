import os
from PyQt5.QtWidgets import (
    QDialog, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QMessageBox, QListWidget
)
import subprocess  # subprocess 모듈 임포트
from core.controller import handle_set_training_request  # handle_get_training_request 대신 로컬 파일 목록 사용

class TrainingPopup(QDialog):
    def __init__(self, user_id: int, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.setWindowTitle("훈련 추가")
        self.setFixedSize(500, 400)
        self.init_ui()
        self.load_training_list()

    def init_ui(self):
        layout = QVBoxLayout()

        self.training_text_input = QLineEdit()
        self.training_text_input.setPlaceholderText("훈련 명령어 입력")

        record_btn = QPushButton("촬영")
        record_btn.clicked.connect(self.record_video)  # 촬영 버튼 클릭 시 record_video 호출

        save_btn = QPushButton("저장")
        save_btn.clicked.connect(self.save_training)

        self.training_list = QListWidget()

        layout.addWidget(QLabel("훈련 명령어"))
        layout.addWidget(self.training_text_input)
        layout.addWidget(record_btn)
        layout.addWidget(save_btn)
        layout.addWidget(QLabel("등록된 훈련 목록"))
        layout.addWidget(self.training_list)

        self.setLayout(layout)

    def record_video(self):
        # 입력된 훈련 명령어(gesture)를 가져옵니다.
        training_command = self.training_text_input.text().strip()
        if not training_command:
            QMessageBox.warning(self, "입력 오류", "먼저 훈련 명령어를 입력하세요.")
            return

        # gesture_train.py 스크립트를 실행합니다.
        # 여기서는 gesture_train.py의 경로가 ./ai/gesture_train.py라고 가정합니다.
        try:
            subprocess.Popen(["python", "./ai/gesture_train.py", training_command])
            QMessageBox.information(self, "촬영 시작", "gesture_train.py가 실행되었습니다.\n콘솔에서 진행 상황을 확인하세요.")
        except Exception as e:
            QMessageBox.critical(self, "실행 오류", f"gesture_train.py 실행 중 오류가 발생했습니다:\n{str(e)}")

    def save_training(self):
        text = self.training_text_input.text().strip()
        if not text:
            QMessageBox.warning(self, "입력 오류", "훈련 명령어를 입력해야 합니다.")
            return

        # 나머지 항목은 빈 문자열로 전달
        response = handle_set_training_request(
            user_id=self.user_id,
            training_text=text,
            keyword_text="",
            gesture_video_path="",
            gesture_recognition_id=0,
            recognized_gesture=""
        )

        if response.get("result") == "success":
            QMessageBox.information(self, "저장 완료", "훈련 정보가 저장되었습니다.")
            self.load_training_list()
            self.clear_inputs()
        else:
            QMessageBox.warning(self, "저장 실패", response.get("reason", "알 수 없는 오류입니다."))

    def load_training_list(self):
        """로컬 디렉토리의 학습 데이터 파일명에서 제스처 이름만 추출하여 등록된 훈련 목록에 표시합니다."""
        self.training_list.clear()
        data_dir = "./ai/training/data"  # 저장된 학습 데이터 디렉토리 경로 (필요에 따라 수정)
        try:
            files = os.listdir(data_dir)
            # seq_로 시작하며 .npy로 끝나는 파일들 필터링
            seq_files = [f for f in files if f.startswith("seq_") and f.endswith(".npy")]
            gesture_names = set()
            for file in seq_files:
                parts = file.split("_")
                if len(parts) >= 3:
                    # 예: "seq_굳_1743661342.npy"에서 index 1가 제스처 이름 ("굳")
                    gesture_names.add(parts[1])
            for name in sorted(gesture_names):
                self.training_list.addItem(name)
        except Exception as e:
            print(f"Error loading training files from {data_dir}: {e}")

    def clear_inputs(self):
        self.training_text_input.clear()

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    # 예시: user_id를 1로 설정
    popup = TrainingPopup(user_id=1)
    popup.exec_()
