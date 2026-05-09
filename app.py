import streamlit as st
import subprocess
import sys
import json
import base64
import requests

# --- FORCE L'INSTALLATION SI MISTRAL MANQUE ---
try:
    from mistralai import Mistral
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "mistralai"])
    from mistralai import Mistral

# --- CONFIGURATION ---
MISTRAL_KEY = st.secrets["MISTRAL_KEY"]
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
REPO_NOM = "zachariepays-debug/Hartur-ia"
client = Mistral(api_key=MISTRAL_KEY)

st.set_page_config(page_title="HARTUR | NEURAL OS", layout="wide")

# STYLE
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #00FF41; font-family: 'Courier New', monospace; }
    header, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# CONNEXION
if "user" not in st.session_state:
    st.title("HARTUR CONNECT")
    u = st.text_input("IDENTIFIANT")
    if st.button("ENTRER"):
        st.session_state.user = u
        st.rerun()
else:
    st.title(f"INTERFACE : {st.session_state.user}")
    st.write("Le système est opérationnel.")
    
    if prompt := st.chat_input("Message..."):
        st.chat_message("user").write(prompt)
        res = client.chat.complete(model="mistral-large-latest", messages=[{"role":"user","content":prompt}])
        st.chat_message("assistant").write(res.choices[0].message.content)
