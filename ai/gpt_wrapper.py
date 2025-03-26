from gpt4all import GPT4All
import os

# 모델 경로와 이름 설정
MODEL_NAME = "Meta-Llama-3-8B-Instruct.Q4_0.gguf"
ROOT_DIR = os.getcwd()  # main.py 기준 실행 디렉토리
MODEL_DIR = os.path.join(ROOT_DIR, 'ai', 'models')

# 모델 로딩 (최초 1회)
model = GPT4All(model_name=MODEL_NAME, model_path=MODEL_DIR)

### 시스템 프롬프트 설정
SYSTEM_PROMPT = (
    "너는 감정 케어를 도와주는 대화형 AI 'DORA'야.\n"
    "상대방의 감정에 공감하며 따뜻하고 정중한 말투로 응답해.\n"
    "이전 대화를 기억하고, 질문의 맥락에 맞는 구체적인 응답을 해야 해.\n"
    "인사말이나 반복적인 문구는 피하고, 간결하게 핵심만 전달해.\n"
    "응답은 반드시 한국어로만 해. 영어 혼용 금지."
)

def generate_reply_with_history(user_message: str, history: list[dict], max_tokens: int = 200) -> str:
    if not history:
        full_prompt = f"{SYSTEM_PROMPT}\n\n사용자: {user_message}\nDORA:"
    else:
        messages = "\n".join([f"사용자: {h['user']}\nDORA: {h['dora']}" for h in history])
        full_prompt = f"{SYSTEM_PROMPT}\n\n{messages}\n사용자: {user_message}\nDORA:"

    with model.chat_session():
        reply = model.generate(full_prompt, max_tokens=max_tokens)
        return reply.strip()
