import streamlit as st
import requests
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase
import av
import numpy as np

# --- PAGE CONFIG ---
st.set_page_config(page_title="Barn's Coffee AI Chat", page_icon="☕", layout="wide")

# --- INJECT CSS FOR BRANDING ---
st.markdown("""
<style>
html, body, [data-testid="stAppViewContainer"] {
    height: 100vh;
    width: 100vw;
    background-color: #f2f4f8;
}

header { visibility: hidden; }
footer { visibility: hidden; }

.block-container {
    padding-top: 0rem;
    padding-bottom: 0rem;
}

.chat-message.user {
    background-color: #0cdc0cd6 !important;
    color: white !important;
    border-radius: 0.8rem;
    padding: 0.5rem;
}

.chat-message.assistant {
    background-color: white !important;
    color: #105e10 !important;
    border-radius: 0.8rem;
    padding: 0.5rem;
}
</style>
""", unsafe_allow_html=True)

# --- LOGO AND WELCOME HEADER ---
#st.image("Barn's.png", width=150)
st.markdown("""
# Welcome to Barn's Coffee ☕
Experience your personalized coffee assistant. 🌿
""")

# --- SESSION STATE FOR CHAT HISTORY ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi there! 👋 Welcome to Barn’s! 🌿 Would you like coffee today or prefer something sweet?"}
    ]

# --- DISPLAY CHAT HISTORY ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        self.recorded_frames = []

    def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
        self.recorded_frames.append(frame)
        return frame

st.markdown("### 🎤 Voice Recording")

webrtc_ctx = webrtc_streamer(
    key="voice",
    mode="sendrecv",
    audio_receiver_size=256,
    media_stream_constraints={"audio": True, "video": False},
    rtc_configuration={ "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}] },
    audio_processor_factory=AudioProcessor,
)

if webrtc_ctx and webrtc_ctx.state.playing:
    st.info("Recording... Stop when done and the audio will process automatically.")

# You can expand this to convert audio frames to wav and transcribe using Whisper or Google STT.

# --- CHAT INPUT ---
if prompt := st.chat_input("Type your message..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Adjust payload to match n8n webhook
    payload = {"chatInput": prompt}

    with st.spinner("Barn's AI is preparing your coffee..."):
        try:
            response = requests.post(
                "https://faisal442101210.app.n8n.cloud/webhook/5e0a08b1-b0d4-41e8-be5c-96f93b5df20f/chat",
                json=payload,
                timeout=60
            )
            if response.status_code == 200:
                ai_reply = response.json().get("output", "⚠️ AI did not return a reply.")
            else:
                ai_reply = f"⚠️ Error from backend (status {response.status_code})."

        except Exception as e:
            ai_reply = f"⚠️ Exception: {e}"

    st.session_state.messages.append({"role": "assistant", "content": ai_reply})
    with st.chat_message("assistant"):
        st.markdown(ai_reply)

