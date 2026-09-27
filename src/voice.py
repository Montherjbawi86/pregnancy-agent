"""معالجة الصوت — تسجيل واستماع"""
import os
import io
import tempfile
from gtts import gTTS


def text_to_speech(text: str, lang: str = "ar") -> bytes:
    """يحوّل النص لصوت"""
    try:
        # نظّف النص من الرموز
        clean = text.replace("*", "").replace("#", "").replace("`", "")
        clean = clean.replace("🤰", "").replace("⚕️", "").replace("✅", "")
        # اقتصر على 500 حرف (حد gTTS)
        clean = clean[:500]
        if not clean.strip():
            return b""
        tts = gTTS(text=clean, lang=lang, slow=False)
        buf = io.BytesIO()
        tts.write_to_fp(buf)
        buf.seek(0)
        return buf.read()
    except Exception as e:
        print(f"TTS error: {e}")
        return b""


def speech_to_text(audio_bytes: bytes) -> str:
    """يحوّل الصوت لنص — يستخدم Whisper من Groq"""
    try:
        from openai import OpenAI
        from dotenv import load_dotenv
        load_dotenv()
        
        client = OpenAI(
            api_key=os.getenv("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1"
        )
        
        # احفظ الصوت مؤقتاً
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(audio_bytes)
            temp_path = f.name
        
        try:
            with open(temp_path, "rb") as audio_file:
                response = client.audio.transcriptions.create(
                    model="whisper-large-v3",
                    file=audio_file,
                    language="ar"
                )
            return response.text
        finally:
            os.unlink(temp_path)
    except Exception as e:
        print(f"STT error: {e}")
        return ""
