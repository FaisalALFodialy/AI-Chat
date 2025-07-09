import streamlit as st
import requests

# --- PAGE CONFIG ---
st.set_page_config(page_title="Barn's Coffee AI Chat", page_icon="☕", layout="wide")

# --- INJECT CSS FOR BRANDING ---
st.markdown("""
<style>
html, body, [data-testid="stAppViewContainer"] {
    height: 100vh;
    width: 100vw;
}

header { visibility: hidden; }
footer { visibility: hidden; }

.block-container {
    padding-top: 0rem;
    padding-bottom: 0rem;
}

.chat-message.user {
    background-color: white !importent ;
    color: black !importent;
    border-radius: 0.8rem;
    padding: 0.5rem;
}

.chat-message.assistant {
    background-color: white !importent ;
    color: black !importent ;
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

