from gtts import gTTS
import os
import tempfile
import playsound  # pip install playsound==1.2.2

def speak_text_korean(text: str):
    tts = gTTS(text=text, lang='ko')
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
        tts.save(fp.name)
        playsound.playsound(fp.name)
        os.unlink(fp.name)
