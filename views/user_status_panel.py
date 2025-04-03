from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, QCheckBox
)
from PyQt5.QtCore import pyqtSignal
from db.query import get_user_emotion_analysis

class UserPanel(QWidget):
    # 외부(메인 뷰 등)에서 체크박스 상태 변경을 감지할 수 있도록 시그널 정의
    cameraToggled = pyqtSignal(bool)
    micToggled = pyqtSignal(bool)
    gestureToggled = pyqtSignal(bool)

    def __init__(self, user_id: int):
        super().__init__()
        self.user_id = user_id
        self.init_ui()
        self.load_emotion_history()

    def init_ui(self):
        layout = QVBoxLayout()

        # 체크박스 영역 (카메라, 마이크, 제스처)
        toggles_layout = QHBoxLayout()
        self.camera_checkbox = QCheckBox("카메라 ON")
        self.mic_checkbox = QCheckBox("마이크 ON")
        self.gesture_checkbox = QCheckBox("제스처 ON")
        self.camera_checkbox.toggled.connect(self.emit_camera_toggled)
        self.mic_checkbox.toggled.connect(self.emit_mic_toggled)
        self.gesture_checkbox.toggled.connect(self.emit_gesture_toggled)
        toggles_layout.addWidget(self.camera_checkbox)
        toggles_layout.addWidget(self.mic_checkbox)
        toggles_layout.addWidget(self.gesture_checkbox)
        layout.addLayout(toggles_layout)

        # 오늘의 감정 요약
        self.today_summary_label = QLabel("오늘의 감정 요약을 불러오는 중...")
        layout.addWidget(QLabel("\u25CF 오늘의 감정"))
        layout.addWidget(self.today_summary_label)

        # 표정 정보 요약
        self.face_summary_label = QLabel("표정 정보를 분석하는 중...")
        layout.addWidget(QLabel("\u25CF 표정 정보"))
        layout.addWidget(self.face_summary_label)

        # 목소리 정보 요약
        self.voice_summary_label = QLabel("목소리 정보를 분석하는 중...")
        layout.addWidget(QLabel("\u25CF 목소리 정보"))
        layout.addWidget(self.voice_summary_label)

        # 감정 분석 이력
        layout.addWidget(QLabel("\u25CF 감정 분석 이력"))
        self.history_list = QListWidget()
        layout.addWidget(self.history_list)

        self.setLayout(layout)

    def emit_camera_toggled(self, checked: bool):
        self.cameraToggled.emit(checked)

    def emit_mic_toggled(self, checked: bool):
        self.micToggled.emit(checked)

    def emit_gesture_toggled(self, checked: bool):
        self.gestureToggled.emit(checked)

    def load_emotion_history(self):
        results = get_user_emotion_analysis(self.user_id)

        if results:
            latest = results[0]
            summary = latest.get("summary", "")
            self.today_summary_label.setText(f"오늘은 기분이 '{summary}'으로 감지되었어요.")
        else:
            self.today_summary_label.setText("최근 감정 데이터가 없습니다.")

        # 간단 요약 (추후 통계 분석으로 개선 가능)
        face_emotions = [r.get("face_emotion", "") for r in results if r.get("face_emotion")]
        voice_emotions = [r.get("voice_emotion", "") for r in results if r.get("voice_emotion")]

        if face_emotions:
            self.face_summary_label.setText(f"최근 감지된 표정: {', '.join(face_emotions[:5])}...")
        else:
            self.face_summary_label.setText("표정 정보 없음")

        if voice_emotions:
            self.voice_summary_label.setText(f"최근 감지된 목소리: {', '.join(voice_emotions[:5])}...")
        else:
            self.voice_summary_label.setText("목소리 정보 없음")

        # 이력 리스트 갱신
        self.history_list.clear()
        for row in results:
            time_str = row.get('time', '')
            summary_str = row.get('summary', '')
            item_text = f"[{time_str}] {summary_str}"
            self.history_list.addItem(QListWidgetItem(item_text))

    def update_face_expression(self, expression_text: str):
        """UserPanel에서 표정 정보를 업데이트하는 메서드"""
        self.face_summary_label.setText(expression_text)
