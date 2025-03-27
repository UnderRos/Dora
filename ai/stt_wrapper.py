from whispercpp_kit import WhisperCPP

whisper = WhisperCPP(model_name="base")
whisper.setup() # First-time setup (automatically done on first transcribe)

def transcribe_audio(file_path: str) -> str:
    """
    Whisper.cpp-ki를 이용해 음성 파일을 텍스트로 변환
    :param file_path: wav 파일 경로
    :return: 텍스트 변환 결과
    """
    try:
        result = whisper.transcribe(file_path, language="ko")
        return result.strip()
    except Exception as e:
        print(f"[STT] 변환 오류: {e}")
        return ""
