from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QListWidget, QListWidgetItem
)
from db.query import get_user_emotion_analysis

class UserPanel(QWidget):
    def __init__(self, user_id: int):
        super().__init__()
        self.user_id = user_id
        self.init_ui()
        self.load_emotion_history()

    def init_ui(self):
        layout = QVBoxLayout()

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

    def load_emotion_history(self):
        results = get_user_emotion_analysis(self.user_id)

        if results:
            latest = results[0]
            summary = latest.get("summary", "")
            self.today_summary_label.setText(f"오늘은 기분이 '{summary}'으로 감지되었어요.")
        else:
            self.today_summary_label.setText("최근 감정 데이터가 없습니다.")

        # 단순 요약 (향후 통계 비교로 개선 예정)
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

        self.history_list.clear()
        for row in results:
            text = f"[{row.get('time', '')}] {row.get('summary', '')}"
            self.history_list.addItem(QListWidgetItem(text))
