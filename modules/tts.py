import io
from gtts import gTTS


def text_to_audio(text: str, lang: str = "es") -> io.BytesIO:
    tts = gTTS(text=text, lang=lang, slow=False)
    buffer = io.BytesIO()
    tts.write_to_fp(buffer)
    buffer.seek(0)
    return buffer
