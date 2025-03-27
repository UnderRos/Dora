# DORA

## 프로젝트 소개
본 프로젝트는 사용자의 외로움을 덜어주고, 일상생활에서 필요한 정보를 비서처럼 알려주며, 정신 건강을 챙겨주는 **돌봄 챗봇 GUI 프로그램**입니다. 향후에는 실제 돌봄 로봇과 결합하여 정서적 교감과 실질적 도움을 동시에 제공하는 통합 서비스를 목표로 합니다.

---

## 주요 기능

| 기능 분류         | 세부 내용 |
|------------------|-----------|
| 정서적 돌봄       | - 일상 대화 및 교감 제공<br>- 가상 펫 또는 캐릭터 형태로 정서적 연결 지원 |
| 정보 및 일정 관리 | - 일정 알림, 할 일 목록 제공<br>- 일상 정보 및 유용한 생활 팁 전달 |
| 정신 건강 모니터링 | - 감정 인식 및 상태 모니터링<br>- 위급 상황 감지 시 경고 및 알림 제공 |

---

## 개발 배경
별도의 센서 없이 신체적 건강 상태를 파악하는 데에는 현실적인 한계가 존재합니다. 따라서 본 프로젝트는 사용자의 대화와 감정을 바탕으로 한 **정신 건강 관리와 정서적 돌봄**에 집중하고 있습니다.

---

## 시스템 구성

| 구성 요소           | 설명 |
|--------------------|------|
| 챗봇 인터페이스     | GUI 기반 사용자 대화 창 구성 |
| 자연어 처리 (NLP)   | 사용자 입력의 감정 및 의도 분석 |
| 감정 인식           | 표정(영상) 및 음성 기반의 감정 판단 |
| 대화 페르소나 시스템 | 사용자 맞춤형 대화 스타일 구현 (심심이, Character.AI 유사) |

---

## 참고 서비스

| 분류         | 사례 |
|--------------|------|
| 페르소나 챗봇 | [SimSimi](https://simsimi.com), [Character.AI](https://beta.character.ai/) |
| 로봇 + AI 펫  | Sony AIBO, RoboHon |
| 돌봄 로봇     | Pepper, ElliQ |

---

## **NangMan**팀 구성

| 역할   | 이름       |
|--------|------------|
| 팀장   | 김연우     |
| 팀원   | 나덕윤     |
| 팀원   | 심채훈     |
| 팀원   | 임동욱     |

---

## 기술 스택

| 분류 | 사용 기술 |
|------|-----------|
| **Language** | <img src="https://img.shields.io/badge/Python-3.10-blue?logo=python&logoColor=white"/> |
| **GUI Framework** | <img src="https://img.shields.io/badge/PyQt5-GUI%20Framework-green?logo=qt&logoColor=white"/> <img src="https://img.shields.io/badge/Tkinter-GUI%20Framework-lightgrey"/> |
| **영상 및 얼굴 인식** | <img src="https://img.shields.io/badge/OpenCV-Video%20Processing-orange?logo=opencv&logoColor=white"/> <img src="https://img.shields.io/badge/Mediapipe-Face%20Landmarks-red"/> |
| **음성 처리** | <img src="https://img.shields.io/badge/SpeechRecognition-Audio-yellow"/> |
| **딥러닝 프레임워크** | <img src="https://img.shields.io/badge/TensorFlow-ML-orange?logo=tensorflow"/> <img src="https://img.shields.io/badge/PyTorch-DeepLearning-red?logo=pytorch"/> |
| **자연어 처리 (NLP)** | <img src="https://img.shields.io/badge/Transformers-HuggingFace-yellow?logo=huggingface"/> <img src="https://img.shields.io/badge/KoBERT-Korean%20NLP-blue"/> |
| **Database** | <img src="https://img.shields.io/badge/MySQL-Database-blue?logo=mysql"/> <img src="https://img.shields.io/badge/SQLite-LightweightDB-lightblue?logo=sqlite"/> |

---

## 설치 및 실행 방법

```bash
# 의존성 설치
pip install -r requirements.txt

# 실행
python main.py
