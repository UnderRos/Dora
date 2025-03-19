from gtts import gTTS
import io
from pydub import AudioSegment
from pydub.playback import play

def text_to_speech(text: str) -> None:
    tts = gTTS(text=text, lang='ko')
    
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)

    audio = AudioSegment.from_file(fp, format="mp3")
    
    play(audio)
    print("음성 재생이 완료되었습니다.")

if __name__ == "__main__":
    sample_text = "나덕윤 10분뒤 사망"
    text_to_speech(sample_text)
