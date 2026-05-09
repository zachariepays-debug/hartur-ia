import streamlit as st
import pandas as pd
import requests
import base64
import json
from io import StringIO
from datetime import datetime

# ==========================================
# ⚙️ CONFIGURATION GITHUB & DESIGN
# ==========================================
REPO_NOM = "zachariepays-debug/Hartur-ia" 
FICHIER_COMPTES = "comptes.csv"
FICHIER_CHATS = "conversations.json"
FICHIER_SYSTEM = "system_state.json"
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
MASTER_CODE = "babar"

st.set_page_config(page_title="HARTUR | NEURAL OS", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #030507; color: white; }
    .stChatInputContainer { max-width: 600px !important; margin: 0 auto !important; }
    .stChatInput { border-radius: 20px !important; border: 1px solid #333 !important; }
    .giant-title { font-size: 60px; font-weight: 900; letter-spacing: 10px; text-align: center; color: white; margin-bottom: 0px;}
    .sub-title { text-align: center; color: #ff4b4b; font-weight: bold; letter-spacing: 3px; font-size: 12px; margin-bottom: 30px;}
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
        payload = {"message": "HARTUR_UPDATE", "content": base64.b64encode(content.encode('utf-8')).decode('utf-8')}
        if sha: payload["sha"] = sha
        requests.put(url, headers=headers, data=json.dumps(payload))
        return None, None

# ==========================================
# 🔐 SÉCURITÉ SYSTÈME
# ==========================================
raw_sys, sha_sys = sync_github(FICHIER_SYSTEM)
sys_state = json.loads(raw_sys) if raw_sys else {"active": True}

if not sys_state["active"]:
    st.markdown("<div style='text-align:center; padding-top:35vh;'><h1>HARTUR EST ÉTEINT</h1></div>", unsafe_allow_html=True)
    unlock = st.text_input("", type="password", placeholder="CODE CORE", label_visibility="collapsed")
    if unlock == MASTER_CODE:
        sync_github(FICHIER_SYSTEM, "PUT", json.dumps({"active": True}), sha_sys)
        st.rerun()
    st.stop()

if "user" not in st.session_state: st.session_state.user = None
if "admin_mode" not in st.session_state: st.session_state.admin_mode = False
if "msgs" not in st.session_state: st.session_state.msgs = []

# ==========================================
# 🛠️ MODE ADMIN (CONTRÔLE TOTAL)
# ==========================================
if st.session_state.admin_mode:
    st.title("🛠️ GESTIONNAIRE HARTUR")
    with st.sidebar:
        if st.button("🔴 ÉTEINDRE LE SYSTÈME"):
            sync_github(FICHIER_SYSTEM, "PUT", json.dumps({"active": False}), sha_sys)
            st.rerun()
        if st.button("🚪 QUITTER ADMIN"):
            st.session_state.admin_mode = False; st.rerun()

    t1, t2, t3 = st.tabs(["👥 COMPTES", "📂 DOSSIERS", "🌐 FLUX"])
    
    with t1:
        u_raw, _ = sync_github(FICHIER_COMPTES)
        if u_raw:
            df_comptes = pd.read_csv(StringIO(u_raw))
            # Nouveau bouton pour télécharger les mots de passe
            st.download_button("📥 TÉLÉCHARGER LA LISTE DES COMPTES (CSV)", u_raw, "comptes_hartur.csv")
            st.dataframe(df_comptes, use_container_width=True)

    c_data, _ = sync_github(FICHIER_CHATS)
    all_chats = json.loads(c_data) if c_data else {}

    with t2:
        col_sel, col_btn = st.columns([3, 1])
        u_select = col_sel.selectbox("Dossier :", ["Choisir..."] + list(all_chats.keys()), label_visibility="collapsed")
        if u_select != "Choisir...":
            col_btn.download_button(f"📥 {u_select}", json.dumps(all_chats[u_select]), f"{u_select}.json")
            for i, m in enumerate(all_chats[u_select][::-1]):
                st.text_area(f"{u_select if m['role']=='user' else 'IA'}", m['content'], key=f"a_{u_select}_{i}", height=70)

    with t3:
        st.download_button("📥 ARCHIVE GLOBALE DES MESSAGES", json.dumps(all_chats), "global_chats.json")
        tous = []
        for u_n, msgs in all_chats.items():
            for m in msgs: tous.append({"u": u_n, "r": m['role'], "c": m['content']})
        for m in tous[::-1]:
            st.markdown(f"**{'👤 ' + m['u'] if m['r']=='user' else '💀 IA'}** : {m['c']}")
            st.divider()

# ==========================================
# 💬 CHAT & RÉPONSE FORCÉE
# ==========================================
elif st.session_state.user:
    st.markdown(f"<h3 style='text-align:center;'>SESSION : {st.session_state.user}</h3>", unsafe_allow_html=True)
    if st.sidebar.button("LOGOUT"): st.session_state.user = None; st.rerun()
    
    for m in st.session_state.msgs:
        with st.chat_message(m["role"]): st.write(m["content"])

    if prompt := st.chat_input("HARTUR t'écoute..."):
        st.session_state.msgs.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.write(prompt)
        
        with st.chat_message("assistant"):
            reponse = f"Écoute mon pote, tu me parles de '{prompt}', mais entre nous..."
            st.write(reponse)
            st.session_state.msgs.append({"role": "assistant", "content": reponse})
        
        raw_c, sha_c = sync_github(FICHIER_CHATS)
        hist = json.loads(raw_c) if raw_c else {}
        hist[st.session_state.user] = st.session_state.msgs
        sync_github(FICHIER_CHATS, "PUT", json.dumps(hist), sha_c)

# ==========================================
# 🔐 ACCÈS
# ==========================================
else:
    st.markdown('<h1 class="giant-title">HARTUR</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">SYSTÈME NEURAL OS</p>', unsafe_allow_html=True)
    
    auth_tabs = st.tabs(["CONNEXION", "S'INSCRIRE"])
    with auth_tabs[0]:
        u, p = st.text_input("PSEUDO"), st.text_input("MOT DE PASSE", type="password")
        if st.button("ACCÉDER"):
            if u == "6" and p == "6": st.session_state.admin_mode = True; st.rerun()
            u_raw, _ = sync_github(FICHIER_COMPTES)
            df = pd.read_csv(StringIO(u_raw)) if u_raw else pd.DataFrame()
            if not df.empty and not df[(df['pseudo'] == u) & (df['password'] == p)].empty:
                st.session_state.user = u
                c_raw, _ = sync_github(FICHIER_CHATS)
                st.session_state.msgs = json.loads(c_raw).get(u, []) if c_raw else []
                st.rerun()
            else: st.error("Accès refusé.")
    with auth_tabs[1]:
        nu, np = st.text_input("NOM"), st.text_input("CLE", type="password")
        if st.button("CRÉER"):
            u_raw, u_sha = sync_github(FICHIER_COMPTES)
            df = pd.read_csv(StringIO(u_raw)) if u_raw else pd.DataFrame(columns=["pseudo", "password"])
            if nu and np and nu not in df['pseudo'].values:
                new_df = pd.concat([df, pd.DataFrame({"pseudo":[nu], "password":[np]})])
                sync_github(FICHIER_COMPTES, "PUT", new_df.to_csv(index=False), u_sha)
                st.success("Opération réussie.")
