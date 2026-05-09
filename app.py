import os
import subprocess
import sys

# --- RÉPARATEUR DE DÉPENDANCES ---
try:
    from mistralai import Mistral
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "mistralai"])
    from mistralai import Mistral

import streamlit as st
import pandas as pd
import requests
import base64
import json
from io import StringIO

# ==========================================
# ⚙️ RÉCUPÉRATION DES SECRETS
# ==========================================
REPO_NOM = "zachariepays-debug/Hartur-ia" 
MISTRAL_KEY = st.secrets["MISTRAL_KEY"]
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]

client = Mistral(api_key=MISTRAL_KEY)

st.set_page_config(page_title="HARTUR | NEURAL OS", layout="wide")

# STYLE : Noir & Vert (Identité réelle forcée)
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #00FF41; font-family: 'Courier New', monospace; }
    .user-msg { color: #FFFFFF; font-weight: bold; border-left: 3px solid #FFFFFF; padding-left: 10px; margin: 10px 0; }
    .hartur-msg { color: #00FF41; font-weight: bold; border-left: 3px solid #00FF41; padding-left: 10px; margin: 10px 0; }
    header, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

def sync_github(chemin, method="GET", content=None, sha=None):
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    url = f"https://api.github.com/repos/{REPO_NOM}/contents/{chemin}"
    if method == "GET":
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            j = r.json()
            return base64.b64decode(j['content']).decode('utf-8'), j['sha']
        return None, None
    else:
        payload = {"message": "SYNC", "content": base64.b64encode(content.encode('utf-8')).decode('utf-8')}
        if sha: payload["sha"] = sha
        requests.put(url, headers=headers, data=json.dumps(payload))
        return None, None

# ==========================================
# 🔐 GESTION SESSION
# ==========================================
if "user" not in st.session_state: st.session_state.user = None
if "admin_mode" not in st.session_state: st.session_state.admin_mode = False

if st.session_state.admin_mode:
    st.title("🛠️ MASTER CONTROL")
    c_data, _ = sync_github("conversations.json")
    all_chats = json.loads(c_data) if c_data else {}
    
    for u_n, msgs in all_chats.items():
        st.subheader(f"Unité : {u_n}") # Affiche ton pseudo au lieu de [7]
        for m in msgs[::-1]:
            cl = "user-msg" if m['role'] == 'user' else "hartur-msg"
            nom = u_n if m['role'] == 'user' else "HARTUR"
            st.markdown(f"<div class='{cl}'>{nom} : {m['content']}</div>", unsafe_allow_html=True)
        st.divider()
    if st.button("QUITTER"): st.session_state.admin_mode = False; st.rerun()

elif st.session_state.user:
    st.write(f"Connecté en tant que : **{st.session_state.user}**")
    if prompt := st.chat_input("..."):
        # Logique Mistral ici...
        st.session_state.msgs.append({"role": "user", "content": prompt})
        res = client.chat.complete(model="mistral-large-latest", messages=[{"role":"user","content":prompt}])
        st.write(res.choices[0].message.content)

else:
    u = st.text_input("NOM")
    p = st.text_input("CODE", type="password")
    if st.button("DÉVERROUILLER"):
        if u == "6" and p == "6": st.session_state.admin_mode = True; st.rerun()
        st.session_state.user = u
        st.rerun()
