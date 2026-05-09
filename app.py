import os
import subprocess
import sys

# ==========================================
# 🛡️ FORCEUR D'INSTALLATION (PLAN B EXTRÊME)
# ==========================================
# Si Streamlit ignore ton requirements.txt, ce code installe Mistral de force.
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
# ⚙️ CONFIGURATION & SECRETS
# ==========================================
# On utilise tes secrets configurés pour éviter toute erreur [7]
REPO_NOM = "zachariepays-debug/Hartur-ia" 
MISTRAL_KEY = st.secrets["MISTRAL_KEY"]
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]

client = Mistral(api_key=MISTRAL_KEY)

st.set_page_config(page_title="HARTUR | NEURAL OS", layout="wide")

# DESIGN : Noir, Vert (HARTUR) et Blanc (TOI)
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #00FF41; font-family: 'Courier New', monospace; }
    .user-msg { color: #FFFFFF; font-weight: bold; border-left: 3px solid #FFFFFF; padding-left: 10px; margin: 10px 0; }
    .hartur-msg { color: #00FF41; font-weight: bold; border-left: 3px solid #00FF41; padding-left: 10px; margin: 10px 0; }
    header, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# FONCTION DE SYNCHRONISATION GITHUB
def sync_github(chemin, method="GET", content=None, sha=None):
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    url = f"https://api.github.com/repos/{REPO_NOM}/contents/{chemin}"
    try:
        if method == "GET":
            r = requests.get(url, headers=headers)
            if r.status_code == 200:
                j = r.json()
                return base64.b64decode(j['content']).decode('utf-8'), j['sha']
            return None, None
        else:
            payload = {"message": "HARTUR_UPDATE", "content": base64.b64encode(content.encode('utf-8')).decode('utf-8')}
            if sha: payload["sha"] = sha
            requests.put(url, headers=headers, data=json.dumps(payload))
            return None, None
    except:
        return None, None

# ==========================================
# 🔐 SYSTÈME D'IDENTITÉ (ADIEU LE [7])
# ==========================================
if "user" not in st.session_state: st.session_state.user = None
if "admin_mode" not in st.session_state: st.session_state.admin_mode = False

# ÉCRAN DE CONNEXION
if not st.session_state.user and not st.session_state.admin_mode:
    st.markdown('<h1 style="text-align:center;">HARTUR LOGIN</h1>', unsafe_allow_html=True)
    u = st.text_input("IDENTIFIANT")
    p = st.text_input("MOT DE PASSE", type="password")
    
    if st.button("ACCÉDER AU FLUX"):
        if u == "6" and p == "6":
            st.session_state.admin_mode = True
            st.rerun()
        else:
            # Ici on valide ton nom zachariepays-debug
            st.session_state.user = u
            st.session_state.msgs = []
            st.rerun()

# INTERFACE ADMIN (FLUX NEURAL)
elif st.session_state.admin_mode:
    st.title("🛠️ MASTER CONTROL")
    c_raw, _ = sync_github("conversations.json")
    all_chats = json.loads(c_raw) if c_raw else {}
    
    for user_id, messages in all_chats.items():
        st.subheader(f"Canal : {user_id}")
        for m in messages[::-1]:
            cl = "user-msg" if m['role'] == 'user' else "hartur-msg"
            nom = user_id if m['role'] == 'user' else "HARTUR"
            st.markdown(f"<div class='{cl}'>{nom} : {m['content']}</div>", unsafe_allow_html=True)
    
    if st.sidebar.button("DÉCONNEXION"):
        st.session_state.admin_mode = False
        st.rerun()

# INTERFACE UTILISATEUR
else:
    st.title(f"HARTUR v3 | {st.session_state.user}")
    
    for m in st.session_state.msgs:
        with st.chat_message(m["role"]): st.write(m["content"])

    if prompt := st.chat_input("Transmettre au réseau..."):
        st.session_state.msgs.append({"role": "user", "content": prompt})
        
        # Appel Mistral
        try:
            res = client.chat.complete(
                model="mistral-large-latest",
                messages=[{"role": "user", "content": prompt}]
            )
            reponse = res.choices[0].message.content
        except:
            reponse = "ERREUR DE LIAISON NEURALE."

        st.session_state.msgs.append({"role": "assistant", "content": reponse})
        
        # Sauvegarde sur GitHub
        raw_c, sha_c = sync_github("conversations.json")
        data = json.loads(raw_c) if raw_c else {}
        data[st.session_state.user] = st.session_state.msgs
        sync_github("conversations.json", "PUT", json.dumps(data), sha_c)
        st.rerun()
