# voice_copilot_component.py
"""
Simple Streamlit component wrapper to run browser TTS (speak text) and optionally listen.
Uses st.components.v1.html. No server credentials required.
"""
import streamlit as st
import streamlit.components.v1 as components
import json

_HTML = r"""
<div>
  <button id="speakBtn">Speak</button>
  <script>
    const payload = __PAYLOAD__;
    document.getElementById('speakBtn').onclick = () => {
      if ('speechSynthesis' in window) {
        const u = new SpeechSynthesisUtterance(payload.text);
        u.lang = payload.lang || 'en-US';
        u.rate = payload.rate || 1.0;
        window.speechSynthesis.speak(u);
      } else {
        alert('TTS not supported in this browser');
      }
    };
  </script>
</div>
"""

def tts_widget(text: str, lang: str = "en-US", rate: float = 1.0, key: str = "vc"):
    payload = json.dumps({"text": text, "lang": lang, "rate": rate})
    html = _HTML.replace("__PAYLOAD__", payload)
    components.html(html, height=60, scrolling=False, key=key)