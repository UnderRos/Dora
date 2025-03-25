from gpt4all import GPT4All
import os

# 모델 경로와 이름 설정
MODEL_NAME = "Meta-Llama-3-8B-Instruct.Q4_0.gguf"
ROOT_DIR = os.getcwd()  # main.py 기준 실행 디렉토리
MODEL_DIR = os.path.join(ROOT_DIR, 'ai', 'models')

# 모델 로딩 (최초 1회)
model = GPT4All(model_name=MODEL_NAME, model_path=MODEL_DIR)

### 시스템 프롬프트 설정
# SYSTEM_PROMPT = (
#     "너는 감정 케어를 도와주는 대화형 AI 'DORA'야. "
#     "항상 밝고 따뜻한 성격으로, 상대방을 위로하고 응원해줘. "
#     "항상 한국어로 대답하고, 말투는 존댓말로 공손하고 친절해야 해. "
#     "지나치게 길거나 장황하게 설명하지 말고, 핵심적으로 응답해."
# )

SYSTEM_PROMPT = (
    "You are DORA, a conversational AI that provides emotional support and encouragement.\n"
    "You always speak in Korean using a polite and respectful tone.\n"
    "You respond in a warm, cheerful, and encouraging personality.\n"
    "Do not make responses too long or overly detailed — be clear, concise, and emotionally supportive.\n"
    "You must always respond entirely in Korean, never mixing English. Always use 존댓말."
)


# 텍스트 응답 생성 함수
def generate_reply(prompt: str, max_tokens: int = 200) -> str:
    full_prompt = f"{SYSTEM_PROMPT}\n\n사용자: {prompt}\nDORA:"
    with model.chat_session():
        reply = model.generate(full_prompt, max_tokens=max_tokens)
        return reply.strip()
