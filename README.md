# DORA
> 사용자 감정 분석 기반 정서 케어 챗봇  
> 표정/음성 인식, 자연어 처리, 일정 관리까지 GUI 통합 제공  
> PyQt5 기반 데스크탑 앱 + 딥러닝 기반 감정 분석 + KoBERT 의도 분석

---

## 프로젝트 소개
사용자의 외로움을 덜어주고, 일상생활에서 필요한 정보를 비서처럼 알려주며, 정신 건강을 챙겨주는 **돌봄 챗봇 GUI 프로그램**입니다. 향후에는 실제 돌봄 로봇과 결합하여 정서적 교감과 실질적 도움을 동시에 제공하는 통합 서비스를 목표로 합니다.

---

## **NangMan**팀 구성

| 역할   | 이름       |
|--------|------------|
| 팀장   | 김연우     |
| 팀원   | 나덕윤     |
| 팀원   | 심채훈     |
| 팀원   | 임동욱     |

---

## 폴더 구조 요약

```bash
├── ai/           # 딥러닝 모델 및 감정 분석 관련 코드
├── common/       # 공통 유틸리티 함수
├── core/         # 챗봇 핵심 로직 (감정 처리, 의도 분석 등)
├── db/           # 데이터베이스 초기화 및 연동 모듈
├── interface/    # 사용자 인터페이스 관련 모듈
├── views/        # PyQt5 기반 화면 구성 파일
├── network/      # 네트워크/서버 통신 관련 모듈 (확장 대비)
├── main.py       # 프로그램 실행 진입점
```

---

## 핵심 기술 요약 (Tech Highlights)
### 감정 인식 및 표현 분석
- **영상 기반 표정 분석**: Mediapipe를 통해 얼굴 랜드마크를 추출하고, CNN 기반 모델로 감정을 분류 (happy, sad, angry, neutral 등)
- **음성 기반 감정 판단**: 음성 톤을 분석하여 감정 상태를 파악 (추후 확장 고려)

### 자연어 처리 (NLP)
- **의도 분류 모델**: KoBERT 기반 분류기로 사용자의 입력 의도를 파악
- **대화 엔진**: HuggingFace Transformers 기반 문장 생성 또는 응답 템플릿 매칭

### 음성 입력 및 변환
- **음성 인식 입력**: SpeechRecognition을 통해 사용자 음성을 실시간 텍스트로 변환
- **TTS(Text-to-Speech)**: gTTS를 이용해 챗봇 응답을 음성으로 출력

### 정서 케어 및 페르소나 대화
- **심심이/캐릭터 스타일 페르소나**: 사용자 취향에 맞춰 다양한 대화 스타일 제공
- **감정 이력 기반 응답 튜닝**: 반복 감정 상태 저장을 통해 맞춤 대화 흐름 구현 중

### 시스템 구조 및 연동
- **PyQt5 기반 GUI 인터페이스**: 직관적인 감정 상태 시각화 및 대화 인터페이스
- **SQLite 연동**: 사용자 대화 로그, 감정 기록, 일정 등을 로컬 데이터베이스에 저장

---

## 기술 스택

| **분류**             | **사용 기술** |
|----------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **프로그래밍 언어**  | ![Python](https://img.shields.io/badge/Python-3.12-blue?style=flat-square&logo=Python&logoColor=white) |
| **GUI 프레임워크**   | ![PyQt5](https://img.shields.io/badge/PyQt5-GUI%20Framework-green?style=flat-square&logo=qt&logoColor=white) |
| **영상 처리**        | ![OpenCV](https://img.shields.io/badge/OpenCV-Video%20Processing-orange?style=flat-square&logo=opencv&logoColor=white) |
| **음성 처리**        | ![SpeechRecognition](https://img.shields.io/badge/SpeechRecognition-Audio-yellow?style=flat-square) &nbsp; ![gTTS](https://img.shields.io/badge/gTTS-Text_to_Speech-red?style=flat-square) |
| **자연어 처리 (NLP)**| ![KoNLPy](https://img.shields.io/badge/KoNLPy-Korean%20NLP-blue?style=flat-square) |
| **데이터베이스**     | ![SQLite](https://img.shields.io/badge/SQLite-LightweightDB-lightblue?style=flat-square&logo=sqlite) |

---

## 시스템 구성

| 구성 요소           | 설명 |
|--------------------|------|
| 챗봇 인터페이스     | GUI 기반 사용자 대화 창 구성 |
| 자연어 처리 (NLP)   | 사용자 입력의 감정 및 의도 분석 |
| 감정 인식           | 표정(영상) 및 음성 기반의 감정 판단 |
| 대화 페르소나 시스템 | 사용자 맞춤형 대화 스타일 구현 (심심이, Character.AI 유사) |

---

## 영상기반 표정 분석 모델 성능

- **모델 구조**: DeepFace(ArcFace) 임베딩 + MLPClassifier (2 hidden layers: 128 → 64)
- **입력 데이터**: 표정 이미지 → DeepFace 임베딩 (벡터화)
- **클래스 구성**: angry, happy, neutral, sad (총 4개)
- **데이터 분할**: 학습 80% / 테스트 20% (Stratified 방식)

- **평가 지표**:
  - 전반적인 **Accuracy**: 약 **89~92% 수준**
  - 클래스별 Precision / Recall / F1-score:

    <img src="./images/classification_report_bar.png" alt="Classification Report" width="600"/>

  - Confusion Matrix:

    <img src="./images/confusion_matrix.png" alt="Confusion Matrix" width="600"/>

  - 대용량 이미지 배치 처리 + 중간 저장 기능 탑재 (`.npy` 저장으로 중단 복구 가능)
  - 학습 모델 및 결과:
    - `./results/mlp_model.pkl`: 학습 완료된 모델 파일
      
---

## 참고 서비스

| 분류         | 사례 |
|--------------|------|
| 페르소나 챗봇 | [SimSimi](https://simsimi.com), [Character.AI](https://beta.character.ai/) |
| 로봇 + AI 펫  | Sony AIBO, RoboHon |
| 돌봄 로봇     | Pepper, ElliQ |

---

## 설치 및 실행 방법

```bash
# 의존성 설치
pip install -r requirements.txt

# 실행
python main.py
```
