import streamlit as st
import pandas as pd
import requests
import base64
import json
from io import StringIO
from datetime import datetime

# --- CONFIGURATION ---
REPO_NOM = "zachariepays-debug/Hartur-ia" 
FICHIER_COMPTES = "comptes.csv"
FICHIER_CHATS = "conversations.json"
FICHIER_SYSTEM = "system_state.json" # Nouveau fichier pour l'état ON/OFF
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
MASTER_CODE = "babar"

# --- FONCTION DE SYNC GITHUB ---
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
        payload = {"message": "Update System", "content": base64.b64encode(content.encode('utf-8')).decode('utf-8')}
        if sha: payload["sha"] = sha
        requests.put(url, headers=headers, data=json.dumps(payload))
        return None, None

# --- VÉRIFICATION DE L'ÉTAT DU SYSTÈME (PERSISTANT) ---
# On va chercher sur GitHub si le système est censé être ON ou OFF
raw_sys, sha_sys = sync_github(FICHIER_SYSTEM)
sys_state = json.loads(raw_sys) if raw_sys else {"active": True}

if not sys_state["active"]:
    st.markdown("<style>.stApp { background-color: black !important; }</style>", unsafe_allow_html=True)
    st.markdown("<div style='text-align:center; color:white; padding-top:30vh;'><h1>HARTUR EST ÉTEINT</h1><p>REOUVRIR HARTUR</p></div>", unsafe_allow_html=True)
    unlock = st.text_input("CODE MAÎTRE", type="password", label_visibility="collapsed")
    if unlock == MASTER_CODE:
        # On rallume sur GitHub pour tout le monde
        sync_github(FICHIER_SYSTEM, "PUT", json.dumps({"active": True}), sha_sys)
        st.rerun()
    st.stop()

# --- RESTE DU SCRIPT (ADMIN & CHAT) ---
if "user" not in st.session_state: st.session_state.user = None
if "admin_mode" not in st.session_state: st.session_state.admin_mode = False

# [Dans ton Mode Admin, pour éteindre]
if st.session_state.admin_mode:
    if st.button("🔴 ÉTEINDRE POUR TOUS (GITHUB SYNC)"):
        # On enregistre l'extinction sur GitHub
        sync_github(FICHIER_SYSTEM, "PUT", json.dumps({"active": False}), sha_sys)
        st.rerun()
    
    # ... le reste de tes onglets (Flux Global, Dossiers, etc.)
