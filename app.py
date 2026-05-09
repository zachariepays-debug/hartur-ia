import streamlit as st
import pandas as pd
import requests
import base64
import json
from io import StringIO
from datetime import datetime

# ==========================================
# ⚙️ CONFIGURATION CORE
# ==========================================
REPO_NOM = "zachariepays-debug/Hartur-ia" 
FICHIER_COMPTES = "comptes.csv"
FICHIER_CHATS = "conversations.json"
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
MASTER_CODE = "babar"

st.set_page_config(page_title="HARTUR | OS", layout="wide", page_icon="💀")

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
        payload = {"message": "Update HARTUR", "content": base64.b64encode(content.encode('utf-8')).decode('utf-8')}
        if sha: payload["sha"] = sha
        requests.put(url, headers=headers, data=json.dumps(payload))
        return None, None

# Initialisation
if "user" not in st.session_state: st.session_state.user = None
if "admin_mode" not in st.session_state: st.session_state.admin_mode = False
if "msgs" not in st.session_state: st.session_state.msgs = []
if "system_active" not in st.session_state: st.session_state.system_active = True

# --- KILL SWITCH ---
if not st.session_state.system_active:
    st.markdown("<style>.stApp { background-color: black !important; }</style>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align:center; color:white; padding-top:30vh;'>RÉOUVRIR HARTUR</h1>", unsafe_allow_html=True)
    unlock = st.text_input("CODE", type="password", label_visibility="collapsed")
    if unlock == MASTER_CODE:
        st.session_state.system_active = True
        st.rerun()
    st.stop()

# ==========================================
# 🛠️ MODE ADMIN (VUE GLOBALE & DOSSIERS)
# ==========================================
if st.session_state.admin_mode:
    st.title("🛠️ PANNEAU DE CONTRÔLE")
    if st.sidebar.button("QUITTER ADMIN"): st.session_state.admin_mode = False; st.rerun()
    
    tab1, tab2, tab3 = st.tabs(["👥 COMPTES", "📂 DOSSIERS PAR NOM", "🌐 FLUX GLOBAL"])
    
    c_data, _ = sync_github(FICHIER_CHATS)
    all_chats = json.loads(c_data) if c_data else {}

    with tab1:
        u_raw, _ = sync_github(FICHIER_COMPTES)
        if u_raw:
            st.dataframe(pd.read_csv(StringIO(u_raw)), use_container_width=True)

    with tab2:
        selection = st.selectbox("Dossier de l'utilisateur :", ["Sélectionner..."] + list(all_chats.keys()))
        if selection != "Sélectionner...":
            for i, m in enumerate(all_chats[selection][::-1]):
                nom = selection if m['role'] == 'user' else "💀 HARTUR"
                st.text_area(f"De : {nom}", m['content'], height=70, key=f"file_{selection}_{i}")

    with tab3:
        st.subheader("Toutes les conversations mélangées (Dernières en haut)")
        tous_messages = []
        for user, messages in all_chats.items():
            for m in messages:
                tous_messages.append({
                    "user": user,
                    "role": "👤 UTILISATEUR" if m['role'] == 'user' else "💀 IA",
                    "content": m['content'],
                    "time": m.get("time", "Inconnue")
                })
        
        # Tri par date (si dispo) ou inversion simple pour avoir le dernier en haut
        for i, m in enumerate(tous_messages[::-1]):
            st.markdown(f"**[{m['user']}] {m['role']}** : {m['content']}")
            st.divider()

# ==========================================
# 💬 INTERFACE IA (AVEC CLÉ API & MÉMOIRE)
# ==========================================
elif st.session_state.user:
    st.markdown(f"<h2 style='text-align:center;'>SESSION : {st.session_state.user}</h2>", unsafe_allow_html=True)
    
    for m in st.session_state.msgs:
        with st.chat_message(m["role"]): st.write(m["content"])

    if prompt := st.chat_input("Dis-moi tout..."):
        # 1. Sauvegarde question utilisateur
        st.session_state.msgs.append({"role": "user", "content": prompt, "time": str(datetime.now())})
        
        # 2. Réponse de l'IA (Ton pote honnête)
        reponse = f"Écoute mon pote, tu me parles de '{prompt}', mais entre nous..."
        st.session_state.msgs.append({"role": "assistant", "content": reponse, "time": str(datetime.now())})
        
        # 3. Synchro GitHub (Questions + Réponses + Comptes)
        raw_c, sha_c = sync_github(FICHIER_CHATS)
        hist = json.loads(raw_c) if raw_c else {}
        hist[st.session_state.user] = st.session_state.msgs
        sync_github(FICHIER_CHATS, "PUT", json.dumps(hist), sha_c)
        st.rerun()

# ==========================================
# 🔐 LOGIN (6/6)
# ==========================================
else:
    u = st.text_input("NOM")
    p = st.text_input("MOT DE PASSE", type="password")
    if st.button("ENTRER"):
        if u == "6" and p == "6":
            st.session_state.admin_mode = True
            st.rerun()
        # Logique de connexion classique...
