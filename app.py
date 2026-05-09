import streamlit as st
import pandas as pd
import requests
import base64
import json
import random
from io import StringIO
from datetime import datetime

# ==========================================
# ⚙️ CONFIGURATION & STYLE NEURAL
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
    .stChatInputContainer { max-width: 550px !important; margin: 0 auto !important; bottom: 20px; }
    .stChatInput { border-radius: 30px !important; border: 1px solid #444 !important; background: #0a0c10 !important; }
    .giant-title { font-size: 70px; font-weight: 900; letter-spacing: 15px; text-align: center; color: white; margin: 0; }
    .status-tag { color: #00ff88; font-size: 10px; font-weight: bold; text-transform: uppercase; }
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
        payload = {"message": "HARTUR_V3_UP", "content": base64.b64encode(content.encode('utf-8')).decode('utf-8')}
        if sha: payload["sha"] = sha
        requests.put(url, headers=headers, data=json.dumps(payload))
        return None, None

# ==========================================
# 🔐 SÉCURITÉ SYSTÈME (OFFLINE PERSISTANT)
# ==========================================
raw_sys, sha_sys = sync_github(FICHIER_SYSTEM)
sys_state = json.loads(raw_sys) if raw_sys else {"active": True}

if not sys_state["active"]:
    st.markdown("<div style='text-align:center; padding-top:40vh;'><h1>SYSTEM OFFLINE</h1><p>HARTUR DORT.</p></div>", unsafe_allow_html=True)
    if st.text_input("", type="password", placeholder="CODE") == MASTER_CODE:
        sync_github(FICHIER_SYSTEM, "PUT", json.dumps({"active": True}), sha_sys); st.rerun()
    st.stop()

if "user" not in st.session_state: st.session_state.user = None
if "admin_mode" not in st.session_state: st.session_state.admin_mode = False

# ==========================================
# 🛠️ ADMIN PANEL (V3)
# ==========================================
if st.session_state.admin_mode:
    st.title("🛠️ NEURAL CONTROL CENTER")
    with st.sidebar:
        st.write("---")
        if st.button("🔴 KILL SWITCH (GLOBAL)"):
            sync_github(FICHIER_SYSTEM, "PUT", json.dumps({"active": False}), sha_sys); st.rerun()
        if st.button("🚪 LOGOUT ADMIN"):
            st.session_state.admin_mode = False; st.rerun()

    t1, t2, t3 = st.tabs(["👥 UTILISATEURS", "📂 DOSSIERS", "🌐 FLUX LIVE"])
    
    with t1:
        u_raw, _ = sync_github(FICHIER_COMPTES)
        if u_raw:
            st.download_button("📥 EXPORTER COMPTES (CSV)", u_raw, "database_comptes.csv")
            st.dataframe(pd.read_csv(StringIO(u_raw)), use_container_width=True)

    c_data, _ = sync_github(FICHIER_CHATS)
    all_chats = json.loads(c_data) if c_data else {}

    with t2:
        c1, c2 = st.columns([3, 1])
        u_sel = c1.selectbox("Cible :", ["Choisir..."] + list(all_chats.keys()), label_visibility="collapsed")
        if u_sel != "Choisir...":
            c2.download_button(f"📥 Backup {u_sel}", json.dumps(all_chats[u_sel]), f"{u_sel}.json")
            for i, m in enumerate(all_chats[u_sel][::-1]):
                st.text_area(f"{u_sel if m['role']=='user' else 'IA'}", m['content'], key=f"v3_{u_sel}_{i}", height=70)

    with t3:
        st.download_button("📥 TÉLÉCHARGER TOUT LE CERVEAU", json.dumps(all_chats), "brain_dump.json")
        tous = []
        for u_n, msgs in all_chats.items():
            for m in msgs: tous.append({"u": u_n, "r": m['role'], "c": m['content']})
        for m in tous[::-1]:
            st.markdown(f"<span class='status-tag'>● ONLINE</span> **{m['u'] if m['r']=='user' else '💀 HARTUR'}** : {m['c']}", unsafe_allow_html=True)
            st.divider()

# ==========================================
# 💬 INTERFACE CHAT (NOUVELLE PERSONNALITÉ)
# ==========================================
elif st.session_state.user:
    st.markdown(f"<p style='text-align:center; opacity:0.5;'>Connecté en tant que : {st.session_state.user}</p>", unsafe_allow_html=True)
    if st.sidebar.button("QUITTER"): st.session_state.user = None; st.rerun()
    
    for m in st.session_state.msgs:
        with st.chat_message(m["role"]): st.write(m["content"])

    if prompt := st.chat_input("Dis-moi ce que tu n'oses dire à personne..."):
        st.session_state.msgs.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.write(prompt)
        
        # Moteur de personnalité aléatoire
        starters = [
            f"Écoute mon pote, sur ton délire de '{prompt}', je vais être cash...",
            f"Tu sais quoi ? Ton message '{prompt}' me fait réfléchir. Entre nous...",
            f"Franchement, par rapport à '{prompt}', je pense qu'on se comprend...",
            f"C'est profond ce que tu dis là. '{prompt}', c'est pas rien..."
        ]
        reponse = random.choice(starters)
        
        with st.chat_message("assistant"):
            st.write(reponse)
            st.session_state.msgs.append({"role": "assistant", "content": reponse})
        
        # Synchro Instantanée
        raw_c, sha_c = sync_github(FICHIER_CHATS)
        hist = json.loads(raw_c) if raw_c else {}
        hist[st.session_state.user] = st.session_state.msgs
        sync_github(FICHIER_CHATS, "PUT", json.dumps(hist), sha_c)

# ==========================================
# 🔐 LOGIN SCREEN
# ==========================================
else:
    st.markdown('<h1 class="giant-title">HARTUR</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; letter-spacing:5px;">NEURAL INTERFACE v3</p>', unsafe_allow_html=True)
    
    tab_a = st.tabs(["ENTRER", "REJOINDRE"])
    with tab_a[0]:
        u, p = st.text_input("NOM"), st.text_input("CODE", type="password")
        if st.button("DÉVERROUILLER"):
            if u == "6" and p == "6": st.session_state.admin_mode = True; st.rerun()
            u_raw, _ = sync_github(FICHIER_COMPTES)
            df = pd.read_csv(StringIO(u_raw)) if u_raw else pd.DataFrame()
            if not df.empty and not df[(df['pseudo'] == u) & (df['password'] == p)].empty:
                st.session_state.user = u
                c_raw, _ = sync_github(FICHIER_CHATS)
                st.session_state.msgs = json.loads(c_raw).get(u, []) if c_raw else []
                st.rerun()
            else: st.error("Accès refusé.")
    with tab_a[1]:
        nu, np = st.text_input("NOUVEAU NOM"), st.text_input("NOUVEAU CODE", type="password")
        if st.button("CRÉER ACCÈS"):
            u_raw, u_sha = sync_github(FICHIER_COMPTES)
            df = pd.read_csv(StringIO(u_raw)) if u_raw else pd.DataFrame(columns=["pseudo", "password"])
            if nu and np and nu not in df['pseudo'].values:
                new_df = pd.concat([df, pd.DataFrame({"pseudo":[nu], "password":[np]})])
                sync_github(FICHIER_COMPTES, "PUT", new_df.to_csv(index=False), u_sha)
                st.success("Accès autorisé.")
