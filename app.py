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
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
MASTER_CODE = "babar"

st.set_page_config(page_title="HARTUR | OS", layout="wide", page_icon="💀")

# --- DESIGN & CENTRAGE ---
st.markdown("""
    <style>
    .stApp { background-color: #030507; color: #e6edf3; }
    header { visibility: hidden; }
    
    /* Header synchronisé */
    .header-box { text-align: center; padding: 40px 0 10px 0; }
    .giant-title { font-size: 60px; font-weight: 900; letter-spacing: 15px; color: white; margin: 0; }
    .hook-text { color: #8b949e; font-size: 16px; letter-spacing: 4px; }
    .signature-zac { color: #ff4b4b; font-size: 13px; letter-spacing: 5px; font-weight: 900; }

    /* Admin en haut à droite */
    .admin-anchor { position: fixed; top: 20px; right: 20px; z-index: 1000; }
    
    /* Pavé de connexion plus haut */
    .stTabs { margin-top: -20px; }
    </style>
    """, unsafe_allow_html=True)

# --- FONCTIONS GITHUB (PERSISTENCE) ---
def charger_data(chemin):
    url = f"https://api.github.com/repos/{REPO_NOM}/contents/{chemin}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
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

# --- INITIALISATION ---
if "user" not in st.session_state: st.session_state.user = None
if "admin_mode" not in st.session_state: st.session_state.admin_mode = False

# --- AFFICHAGE DU HEADER ---
st.markdown('<div class="header-box"><h1 class="giant-title">HARTUR</h1><p class="hook-text">SYSTÈME NEURAL AVANCÉ</p><p class="signature-zac">CRÉÉ PAR ZACMITE</p></div>', unsafe_allow_html=True)

# --- BOUTON ADMIN (GOD MODE) ---
st.markdown('<div class="admin-anchor">', unsafe_allow_html=True)
if st.button("⚙️"):
    st.session_state.show_admin_login = not st.session_state.get("show_admin_login", False)
st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.get("show_admin_login"):
    with st.sidebar:
        st.title("🛡️ ZONE ADMIN")
        cl_admin = st.text_input("Code Maître", type="password")
        if cl_admin == MASTER_CODE:
            st.session_state.admin_mode = True
            st.success("Accès God Mode activé")

# --- LOGIQUE DE NAVIGATION ---

# 1. SI ADMIN ACTIVÉ
if st.session_state.admin_mode:
    st.subheader("🛠️ Panneau de contrôle")
    if st.button("Quitter le mode Admin"):
        st.session_state.admin_mode = False
        st.rerun()
    # Ici tu retrouveras tes dossiers de comptes et conversations

# 2. SI UTILISATEUR CONNECTÉ
elif st.session_state.user:
    st.chat_input(f"HARTUR t'écoute, {st.session_state.user}...")
    if st.sidebar.button("Déconnexion"):
        st.session_state.user = None
        st.rerun()

# 3. ÉCRAN D'ACCUEIL (CONNEXION & INSCRIPTION LIBRE)
else:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        t1, t2 = st.tabs(["CONNEXION", "S'INSCRIRE"])
        
        with t1:
            u = st.text_input("Pseudo", key="log_u")
            p = st.text_input("Mot de passe", type="password", key="log_p")
            if st.button("CONNEXION"):
                raw, _ = charger_data(FICHIER_COMPTES)
                df = pd.read_csv(StringIO(raw)) if raw else pd.DataFrame(columns=["pseudo", "password"])
                if not df[(df['pseudo'] == u) & (df['password'] == p)].empty:
                    st.session_state.user = u
                    st.rerun()
                else: st.error("Identifiants inconnus.")

        with t2:
            st.markdown("### Créer ton accès")
            new_u = st.text_input("Choisis un Pseudo")
            new_p = st.text_input("Choisis un Mot de passe", type="password")
            if st.button("CRÉER MON COMPTE"):
                raw, sha = charger_data(FICHIER_COMPTES)
                df = pd.read_csv(StringIO(raw)) if raw else pd.DataFrame(columns=["pseudo", "password"])
                if new_u in df['pseudo'].values:
                    st.error("Ce pseudo est déjà pris.")
                elif new_u and new_p:
                    new_row = pd.DataFrame({"pseudo": [new_u], "password": [new_p]})
                    df = pd.concat([df, new_row], ignore_index=True)
                    push_github(FICHIER_COMPTES, df.to_csv(index=False), f"Nouvel inscrit: {new_u}", sha)
                    st.success("Compte créé ! Tu peux maintenant te connecter.")
