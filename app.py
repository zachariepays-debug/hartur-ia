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
# 🔐 SYSTÈME D'ARRÊT (PERSISTANT SUR GITHUB)
# ==========================================
raw_sys, sha_sys = sync_github(FICHIER_SYSTEM)
sys_state = json.loads(raw_sys) if raw_sys else {"active": True}

if not sys_state["active"]:
    st.markdown("<style>.stApp { background-color: black !important; color: white !important; }</style>", unsafe_allow_html=True)
    st.markdown("<div style='text-align:center; padding-top:30vh;'><h1>HARTUR EST ÉTEINT</h1><p>COMMANDE DE SÉCURITÉ ACTIVÉE</p></div>", unsafe_allow_html=True)
    unlock = st.text_input("CODE MAÎTRE", type="password", label_visibility="collapsed")
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
# 🛠️ MODE ADMIN (CONTRÔLE TOTAL)
# ==========================================
if st.session_state.admin_mode:
    st.title("🛠️ GESTIONNAIRE HARTUR")
    
    with st.sidebar:
        st.error("SÉCURITÉ SYSTÈME")
        if st.button("🔴 ÉTEINDRE HARTUR (POUR TOUS)"):
            sync_github(FICHIER_SYSTEM, "PUT", json.dumps({"active": False}), sha_sys)
            st.rerun()
        if st.button("🚪 QUITTER MODE ADMIN"):
            st.session_state.admin_mode = False
            st.rerun()

    tab1, tab2, tab3 = st.tabs(["👥 COMPTES", "📂 DOSSIERS", "🌐 FLUX GLOBAL"])
    
    c_data, _ = sync_github(FICHIER_CHATS)
    all_chats = json.loads(c_data) if c_data else {}

    with tab1:
        u_raw, _ = sync_github(FICHIER_COMPTES)
        if u_raw:
            df_comptes = pd.read_csv(StringIO(u_raw))
            st.dataframe(df_comptes, use_container_width=True)

    with tab2:
        col_sel, col_btn = st.columns([3, 1])
        u_select = col_sel.selectbox("Dossier de l'utilisateur :", ["Choisir..."] + list(all_chats.keys()))
        
        if u_select != "Choisir...":
            col_btn.download_button(f"📥 Dossier {u_select}", json.dumps(all_chats[u_select], indent=4), f"{u_select}.json")
            st.divider()
            for i, m in enumerate(all_chats[u_select][::-1]):
                role = u_select if m['role'] == 'user' else "💀 IA"
                st.text_area(f"Source : {role}", m['content'], key=f"file_{u_select}_{i}", height=80)

    with tab3:
        st.subheader("Historique Universel")
        st.download_button("📥 TÉLÉCHARGER TOUTES LES ARCHIVES", json.dumps(all_chats, indent=4), "archives_globales.json")
        tous_messages = []
        for u_name, messages in all_chats.items():
            for m in messages:
                tous_messages.append({"user": u_name, "role": m['role'], "content": m['content']})
        
        for i, m in enumerate(tous_messages[::-1]):
            tag = f"👤 {m['user']}" if m['role'] == 'user' else "💀 HARTUR"
            st.markdown(f"**{tag}** : {m['content']}")
            st.divider()

# ==========================================
# 💬 INTERFACE CHAT
# ==========================================
elif st.session_state.user:
    st.markdown(f"<h3 style='text-align:center;'>SESSION : {st.session_state.user}</h3>", unsafe_allow_html=True)
    if st.sidebar.button("DÉCONNEXION"):
        st.session_state.user = None; st.rerun()

    for m in st.session_state.msgs:
        with st.chat_message(m["role"]): st.write(m["content"])

    if prompt := st.chat_input("Balance ce que t'as sur le coeur..."):
        st.session_state.msgs.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.write(prompt)
        
        with st.chat_message("assistant"):
            reponse = f"Écoute mon pote, tu me parles de '{prompt}', mais si on est honnête..."
            st.write(reponse)
            st.session_state.msgs.append({"role": "assistant", "content": reponse})
            
        raw_c, sha_c = sync_github(FICHIER_CHATS)
        hist = json.loads(raw_c) if raw_c else {}
        hist[st.session_state.user] = st.session_state.msgs
        sync_github(FICHIER_CHATS, "PUT", json.dumps(hist), sha_c)

# ==========================================
# 🔐 ÉCRAN DE CONNEXION COMPLET
# ==========================================
else:
    st.markdown("<h1 style='text-align:center;'>HARTUR</h1>", unsafe_allow_html=True)
    tab_auth = st.tabs(["CONNEXION", "S'INSCRIRE"])
    
    with tab_auth[0]:
        u = st.text_input("PSEUDO")
        p = st.text_input("MOT DE PASSE", type="password")
        if st.button("ENTRER"):
            if u == "6" and p == "6":
                st.session_state.admin_mode = True; st.rerun()
            
            u_raw, _ = sync_github(FICHIER_COMPTES)
            df = pd.read_csv(StringIO(u_raw)) if u_raw else pd.DataFrame()
            if not df.empty and not df[(df['pseudo'] == u) & (df['password'] == p)].empty:
                st.session_state.user = u
                c_raw, _ = sync_github(FICHIER_CHATS)
                if c_raw: st.session_state.msgs = json.loads(c_raw).get(u, [])
                st.rerun()
            else: st.error("Inconnu ou erreur.")

    with tab_auth[1]:
        nu = st.text_input("NOUVEAU PSEUDO")
        np = st.text_input("NOUVEAU MOT DE PASSE", type="password")
        if st.button("CRÉER COMPTE"):
            u_raw, u_sha = sync_github(FICHIER_COMPTES)
            df = pd.read_csv(StringIO(u_raw)) if u_raw else pd.DataFrame(columns=["pseudo", "password"])
            if nu and np and nu not in df['pseudo'].values:
                new_df = pd.concat([df, pd.DataFrame({"pseudo":[nu], "password":[np]})])
                sync_github(FICHIER_COMPTES, "PUT", new_df.to_csv(index=False), u_sha)
                st.success("Enregistré sur GitHub !")
