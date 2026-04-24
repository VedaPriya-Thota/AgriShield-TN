import base64
from gtts import gTTS
import tempfile
import streamlit as st

# Language mapping
LANG_MAP = {
    "EN": "en",
    "தமிழ்": "ta",
    "हिन्दी": "hi"
}

@st.cache_data(show_spinner=False)
def generate_speech(text, lang="en"):
    try:
        tts = gTTS(text=text, lang=lang)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            tts.save(fp.name)
            with open(fp.name, "rb") as f:
                audio_bytes = f.read()

        return base64.b64encode(audio_bytes).decode()

    except Exception as e:
        st.error(f"Voice error: {e}")
        return None


def autoplay_audio(audio_base64):
    if audio_base64 is None:
        return

    audio_html = f"""
        <audio autoplay>
        <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
        </audio>
    """

    st.markdown(audio_html, unsafe_allow_html=True)


def stop_audio():
    import streamlit.components.v1 as components
    components.html(
        "<script>"
        "var audios = window.parent.document.getElementsByTagName('audio');"
        "for(var i=0;i<audios.length;i++){audios[i].pause();audios[i].currentTime=0;}"
        "</script>",
        height=0,
    )


def transcribe_audio(audio_bytes, lang_key="en"):
    """
    Transcribe audio bytes using Groq Whisper.
    lang_key: "en" | "ta" | "hi"
    """
    try:
        from src.llm.groq_client import transcribe_audio as groq_stt
        
        # Standardize language code for Groq Whisper
        target_lang = lang_key.lower()
        if target_lang not in ["en", "ta", "hi"]:
            target_lang = "en"
        
        result = groq_stt(audio_bytes, language=target_lang)
        return result if result else "Could not understand audio"
        
    except Exception as e:
        st.error(f"STT error: {e}")
        return "Transcription failed"