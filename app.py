import streamlit as st
import pandas as pd
import requests
import base64
import json
from io import StringIO
from datetime import datetime

# ==========================================
# ⚙️ CONFIGURATION GITHUB
# ==========================================
REPO_NOM = "zachariepays-debug/Hartur-ia" 
FICHIER_COMPTES = "comptes.csv"
FICHIER_CHATS = "conversations.json"
FICHIER_SYSTEM = "system_state.json"
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
MASTER_CODE = "babar"

st.set_page_config(page_title="HARTUR | NEURAL OS", layout="wide", page_icon="💀")

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
        payload = {"message": "HARTUR_UPDATE", "content": base64.b64encode(content.encode('utf-8')).decode('utf-8')}
        if sha: payload["sha"] = sha
        requests.put(url, headers=headers, data=json.dumps(payload))
        return None, None

# ==========================================
# 🔐 SYSTÈME D'ARRÊT PERSISTANT
# ==========================================
raw_sys, sha_sys = sync_github(FICHIER_SYSTEM)
sys_state = json.loads(raw_sys) if raw_sys else {"active": True}

if not sys_state["active"]:
    st.markdown("<style>.stApp { background-color: black !important; color: white !important; }</style>", unsafe_allow_html=True)
    st.markdown("<div style='text-align:center; padding-top:30vh;'><h1>HARTUR EST ÉTEINT</h1><p>SYSTÈME VERROUILLÉ</p></div>", unsafe_allow_html=True)
    unlock = st.text_input("CODE CORE", type="password", label_visibility="collapsed")
    if unlock == MASTER_CODE:
        sync_github(FICHIER_SYSTEM, "PUT", json.dumps({"active": True}), sha_sys)
        st.rerun()
    st.stop()

# ==========================================
# 🚀 INITIALISATION
# ==========================================
if "user" not in st.session_state: st.session_state.user = None
if "admin_mode" not in st.session_state: st.session_state.admin_mode = False
if "msgs" not in st.session_state: st.session_state.msgs = []

# ==========================================
# 🛠️ MODE ADMIN
# ==========================================
if st.session_state.admin_mode:
    st.title("🛠️ PANNEAU DE CONTRÔLE ADMIN")
    
    with st.sidebar:
        if st.button("🔴 ÉTEINDRE HARTUR (GLOBAL)"):
            sync_github(FICHIER_SYSTEM, "PUT", json.dumps({"active": False}), sha_sys)
            st.rerun()
        if st.button("🚪 QUITTER ADMIN"):
            st.session_state.admin_mode = False
            st.rerun()

    tab1, tab2, tab3 = st.tabs(["👥 COMPTES", "📂 DOSSIERS UTILISATEURS", "🌐 FLUX GLOBAL"])
    
    c_data, _ = sync_github(FICHIER_CHATS)
    all_chats = json.loads(c_data) if c_data else {}

    with tab1:
        u_raw, _ = sync_github(FICHIER_COMPTES)
        if u_raw:
            st.dataframe(pd.read_csv(StringIO(u_raw)), use_container_width=True)

    with tab2:
        # Bouton placé à côté de la sélection
        col_sel, col_btn = st.columns([3, 1])
        u_select = col_sel.selectbox("Voir la discussion de :", ["Choisir..."] + list(all_chats.keys()), label_visibility="collapsed")
        
        if u_select != "Choisir...":
            col_btn.download_button(f"📥 Dossier {u_select}", json.dumps(all_chats[u_select], indent=4), f"{u_select}.json")
            st.divider()
            for i, m in enumerate(all_chats[u_select][::-1]):
                role = u_select if m['role'] == 'user' else "IA"
                st.text_area(f"Source : {role}", m['content'], key=f"file_{u_select}_{i}", height=80)

    with tab3:
        st.subheader("Flux Global des Conversations")
        st.download_button("📥 TÉLÉCHARGER TOUTES LES ARCHIVES", json.dumps(all_chats, indent=4), "archives_globales.json")
        
        tous_messages = []
        for user_name, messages in all_chats.items():
            for m in messages:
                tous_messages.append({"user": user_name, "role": m['role'], "content": m['content']})
        
        for i, m in enumerate(tous_messages[::-1]):
            role_label = f"👤 {m['user']}" if m['role'] == 'user' else "💀 HARTUR"
            st.markdown(f"**{role_label}** : {m['content']}")
            st.divider()

# ==========================================
# 💬 INTERFACE CHAT (IA POTE)
# ==========================================
elif st.session_state.user:
    st.markdown(f"<h3 style='text-align:center;'>SESSION : {st.session_state.user}</h3>", unsafe_allow_html=True)
    if st.sidebar.button("DÉCONNEXION"):
        st.session_state.user = None
        st.rerun()

    for m in st.session_state.msgs:
        with st.chat_message(m["role"]): st.write(m["content"])

    if prompt := st.chat_input("HARTUR t'écoute..."):
        # Enregistrement Question
        st.session_state.msgs.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.write(prompt)
        
        with st.chat_message("assistant"):
            reponse = f"Écoute mon pote, tu me parles de '{prompt}', mais entre nous..."
            st.write(reponse)
            # Enregistrement Réponse
            st.session_state.msgs.append({"role": "assistant", "content": reponse})
            
        # Synchro GitHub
        raw_c, sha_c = sync_github(FICHIER_CHATS)
        hist = json.loads(raw_c) if raw_c else {}
        hist[st.session_state.user] = st.session_state.msgs
        sync_github(FICHIER_CHATS, "PUT", json.dumps(hist), sha_c)

# ==========================================
# 🔐 CONNEXION
# ==========================================
else:
    st.markdown("<h1 style='text-align:center;'>HARTUR</h1>", unsafe_allow_html=True)
    u = st.text_input("PSEUDO")
    p = st.text_input("MOT DE PASSE", type="password")
    if st.button("DÉVERROUILLER"):
        if u == "6" and p == "6":
            st.session_state.admin_mode = True
            st.rerun()
