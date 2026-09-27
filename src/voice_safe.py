"""صوت آمن — بدون مكتبات ثقيلة"""
import os
import io
import tempfile
import base64


def text_to_speech(text: str, lang: str = "ar") -> bytes:
    """يحوّل النص لصوت عبر gTTS"""
    try:
        from gtts import gTTS
        # نظّف النص
        clean = text.replace("*", "").replace("#", "").replace("`", "")
        clean = clean.replace("🤰", "").replace("⚕️", "").replace("✅", "")
        clean = clean.replace("🔧", "").replace("📊", "").replace("💬", "")
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
    """يحوّل الصوت لنص عبر Groq Whisper"""
    try:
        from openai import OpenAI
        from dotenv import load_dotenv
        load_dotenv()

        client = OpenAI(
            api_key=os.getenv("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1"
        )

        # احفظ الصوت مؤقتاً
        with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as f:
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


def get_voice_recorder_html() -> str:
    """HTML5 MediaRecorder — بدون مكتبات"""
    return """
    <div style="display: flex; gap: 8px; align-items: center;">
        <button id="rec-btn" onclick="toggleRec()" 
                style="background: linear-gradient(135deg, #e91e63, #9c27b0);
                       color: white; border: none; border-radius: 12px;
                       padding: 12px 20px; font-size: 16px; font-weight: 600;
                       cursor: pointer; transition: all 0.2s;
                       box-shadow: 0 4px 12px rgba(233,30,99,0.3);">
            🎤 تسجيل
        </button>
        <span id="status" style="color: #666; font-size: 14px;"></span>
        <audio id="audio-playback" controls style="display:none; height: 40px;"></audio>
    </div>
    
    <script>
    let mediaRecorder = null;
    let audioChunks = [];
    let isRecording = false;
    
    async function toggleRec() {
        const btn = document.getElementById('rec-btn');
        const status = document.getElementById('status');
        
        if (!isRecording) {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                mediaRecorder = new MediaRecorder(stream);
                audioChunks = [];
                
                mediaRecorder.ondataavailable = event => {
                    audioChunks.push(event.data);
                };
                
                mediaRecorder.onstop = async () => {
                    const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                    const reader = new FileReader();
                    reader.readAsDataURL(audioBlob);
                    reader.onloadend = () => {
                        const base64 = reader.result.split(',')[1];
                        // إرسال لـ Streamlit عبر sessionStorage
                        window.parent.postMessage({
                            type: 'streamlit:setComponentValue',
                            value: base64
                        }, '*');
                        // حفظ محلياً
                        sessionStorage.setItem('voice_data', base64);
                        status.innerText = '✅ تم التسجيل — جاري التحويل...';
                    };
                    
                    // أوقف الميكروفون
                    stream.getTracks().forEach(track => track.stop());
                };
                
                mediaRecorder.start();
                isRecording = true;
                btn.innerText = '⏹️ إيقاف';
                btn.style.background = 'linear-gradient(135deg, #d32f2f, #f44336)';
                status.innerText = '🔴 جاري التسجيل...';
                
            } catch (err) {
                status.innerText = '⚠️ الميكروفون غير متاح: ' + err.message;
                status.style.color = '#d32f2f';
            }
        } else {
            mediaRecorder.stop();
            isRecording = false;
            btn.innerText = '🎤 تسجيل';
            btn.style.background = 'linear-gradient(135deg, #e91e63, #9c27b0)';
        }
    }
    </script>
    """
