import streamlit as st
import pandas as pd
import requests
import base64
import json
from io import StringIO
from datetime import datetime

# ==========================================
# ⚙️ CONFIGURATION CORE (GITHUB)
# ==========================================
REPO_NOM = "zachariepays-debug/Hartur-ia" 
FICHIER_COMPTES = "comptes.csv"
FICHIER_CHATS = "conversations.json"
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
MASTER_CODE = "babar"

st.set_page_config(page_title="HARTUR | OS", layout="wide", page_icon="💀")

# ==========================================
# 🎨 DESIGN SYSTÈME (FLASHY, NO-SCROLL, MOBILE)
# ==========================================
st.markdown("""
    <style>
    .stApp { background-color: #030507; color: #e6edf3; }
    header { visibility: hidden; }
    
    /* Titre HARTUR Blanc Flashy */
    .header-box { text-align: center; padding-top: 5vh; }
    .giant-title { 
        font-size: clamp(40px, 10vw, 75px); 
        font-weight: 900; letter-spacing: 15px; 
        color: #ffffff; margin: 0;
        text-shadow: 0 0 25px rgba(255, 255, 255, 0.4);
    }
    .signature-zac { 
        color: #ff4b4b; font-size: 14px; letter-spacing: 5px; 
        font-weight: 900; text-transform: uppercase; margin-top: 5px;
    }

    /* Bouton Admin Fixe à Droite */
    .admin-anchor { position: fixed; top: 20px; right: 20px; z-index: 1000; }
    
    /* Pavé de connexion haut (No-scroll) */
    .stTabs { margin-top: 20px; }
    
    /* Mode Chat : Masquer le titre pour l'immersion */
    .chat-active .header-box { display: none; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 💾 FONCTIONS GITHUB (CORRIGÉES)
# ==========================================
def charger_data(chemin):
    url = f"https://api.github.com/repos/{REPO_NOM}/contents/{chemin}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"} # Correction TypeError
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        j = r.json()
        return base64.b64decode(j['content']).decode('utf-8'), j['sha']
    return None, None

def push_github(chemin, contenu, msg, sha=None):
    url = f"https://api.github.com/repos/{REPO_NOM}/contents/{chemin}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    data = {"message": msg, "content": base64.b64encode(contenu.encode('utf-8')).decode('utf-8')}
    if sha: data["sha"] = sha
    requests.put(url, headers=headers, data=json.dumps(data))

# ==========================================
# 🚀 ÉTAT DU SYSTÈME
# ==========================================
if "user" not in st.session_state: st.session_state.user = None
if "admin" not in st.session_state: st.session_state.admin = False
if "msgs" not in st.session_state: st.session_state.msgs = []
if "hartur_on" not in st.session_state: st.session_state.hartur_on = True

# ==========================================
# 🛡️ LE COIN ADMIN (GOD MODE COMPLET)
# ==========================================
st.markdown('<div class="admin-anchor">', unsafe_allow_html=True)
if st.button("⚙️"):
    st.session_state.show_admin_input = not st.session_state.get("show_admin_input", False)
st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.get("show_admin_input"):
    with st.sidebar:
        st.title("🛡️ ZONE ADMIN")
        cl = st.text_input("PASSWORD", type="password")
        if cl == MASTER_CODE:
            st.session_state.admin = True
            st.success("God Mode Activé")

if st.session_state.admin:
    st.title("🛠️ PANNEAU DE CONTRÔLE")
    if st.button("← RETOUR"):
        st.session_state.admin = False
        st.rerun()

    # Fonctionnalités Admin
    st.session_state.hartur_on = st.toggle("ALIMENTATION HARTUR (KILL SWITCH)", value=st.session_state.hartur_on)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("👤 COMPTES")
        raw, _ = charger_data(FICHIER_COMPTES)
        if raw: st.dataframe(pd.read_csv(StringIO(raw)), use_container_width=True)
    with col2:
        st.subheader("📜 LOGS DISCUSSIONS")
        chats, _ = charger_data(FICHIER_CHATS)
        if chats:
            data = json.loads(chats)
            for u, h in data.items():
                with st.expander(f"Discussion de {u}"):
                    for m in h: st.write(f"**{m['role']}**: {m['content']}")

# ==========================================
# 💬 ESPACE CHAT (PERSONNALITÉ ACCRO)
# ==========================================
elif st.session_state.user:
    if not st.session_state.hartur_on:
        st.error("HARTUR est actuellement hors tension. Contacte Zacmite.")
        st.stop()

    st.markdown('<div class="chat-active"></div>', unsafe_allow_html=True)
    if st.sidebar.button("DÉCONNEXION"):
        st.session_state.user = None
        st.rerun()

    for m in st.session_state.msgs:
        with st.chat_message(m["role"]): st.write(m["content"])

    if prompt := st.chat_input("Balance ce que t'as sur le coeur..."):
        st.session_state.msgs.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.write(prompt)
        
        with st.chat_message("assistant"):
            # Personnalité Confident / Pote addictif
            resp = f"Écoute mon pote, pour ton histoire de '{prompt}', je vais être 100% honnête avec toi..."
            st.write(resp)
            st.session_state.msgs.append({"role": "assistant", "content": resp})
            
        # Sauvegarde GitHub Auto
        c, sha = charger_data(FICHIER_CHATS)
        all_chats = json.loads(c) if c else {}
        all_chats[st.session_state.user] = st.session_state.msgs
        push_github(FICHIER_CHATS, json.dumps(all_chats), f"Update {st.session_state.user}", sha)

# ==========================================
# 🔐 ACCUEIL (CONNEXION & INSCRIPTION)
# ==========================================
else:
    st.markdown('<div class="header-box"><h1 class="giant-title">HARTUR</h1><p class="signature-zac">CRÉÉ PAR ZACMITE</p></div>', unsafe_allow_html=True)
    
    col_l, col_m, col_r = st.columns([1, 1.8, 1])
    with col_m:
        t1, t2 = st.tabs(["CONNEXION", "S'INSCRIRE"])
        with t1:
            u = st.text_input("Pseudo")
            p = st.text_input("Mot de passe", type="password")
            if st.button("ENTRER"):
                raw, _ = charger_data(FICHIER_COMPTES)
                df = pd.read_csv(StringIO(raw)) if raw else pd.DataFrame(columns=["pseudo", "password"])
                if not df[(df['pseudo'] == u) & (df['password'] == p)].empty:
                    st.session_state.user = u
                    # Charger historique
                    c, _ = charger_data(FICHIER_CHATS)
                    if c: st.session_state.msgs = json.loads(c).get(u, [])
                    st.rerun()
                else: st.error("Accès refusé.")
        with t2:
            nu = st.text_input("Nouveau Pseudo")
            np = st.text_input("Ton Mot de passe", type="password")
            if st.button("CRÉER MON ACCÈS"):
                raw, sha = charger_data(FICHIER_COMPTES)
                df = pd.read_csv(StringIO(raw)) if raw else pd.DataFrame(columns=["pseudo", "password"])
                if nu and np and nu not in df['pseudo'].values:
                    new_df = pd.concat([df, pd.DataFrame({"pseudo":[nu], "password":[np]})])
                    push_github(FICHIER_COMPTES, new_df.to_csv(index=False), f"New user: {nu}", sha)
                    st.success("Compte créé ! Connecte-toi.")
