import os
import subprocess
import sys
import time

# --- INSTALLATION FORCÉE AVEC ATTENTE ---
def assure_module(package):
    try:
        __import__(package)
    except ImportError:
        # On tente l'installation
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        # On attend 5 secondes pour que le système de fichiers se mette à jour
        time.sleep(5)

assure_module("mistralai")

# Maintenant on peut importer sans peur
from mistralai import Mistral
import streamlit as st

# --- CONFIGURATION ---
try:
    MISTRAL_KEY = st.secrets["MISTRAL_KEY"]
    GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
except:
    st.error("⚠️ Les SECRETS ne sont pas configurés dans Streamlit Cloud.")
    st.stop()

client = Mistral(api_key=MISTRAL_KEY)

st.set_page_config(page_title="HARTUR | NEURAL OS", layout="wide")

# DESIGN
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #00FF41; font-family: 'Courier New', monospace; }
    header, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# SESSION
if "user" not in st.session_state:
    st.title("HARTUR CONNECT")
    u = st.text_input("IDENTIFIANT")
    if st.button("DÉVERROUILLER"):
        st.session_state.user = u
        st.rerun()
else:
    st.title(f"SYSTÈME : {st.session_state.user}")
    st.write("Connexion établie avec Mistral.")
    
    if prompt := st.chat_input("..."):
        st.chat_message("user").write(prompt)
        res = client.chat.complete(model="mistral-large-latest", messages=[{"role":"user","content":prompt}])
        st.chat_message("assistant").write(res.choices[0].message.content)
