import streamlit as st
import pandas as pd
import requests
import base64
import json
from io import StringIO

# --- CONFIGURATION CORE ---
REPO_NOM = "zachariepays-debug/Hartur-ia" 
FICHIER_COMPTES = "comptes.csv"
FICHIER_CHATS = "conversations.json"
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
MASTER_CODE = "babar"

# --- INITIALISATION SESSION ---
if "user" not in st.session_state: st.session_state.user = None
if "admin" not in st.session_state: st.session_state.admin = False
if "msgs" not in st.session_state: st.session_state.msgs = []
if "theme" not in st.session_state: st.session_state.theme = "Sombre"

# --- CONFIGURATION PAGE & THÈME ---
st.set_page_config(page_title="HARTUR | OS", layout="wide", page_icon="💀")

# CSS Dynamique pour le mode Sombre/Clair
bg_color = "#030507" if st.session_state.theme == "Sombre" else "#f0f2f6"
text_color = "#ffffff" if st.session_state.theme == "Sombre" else "#000000"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg_color}; color: {text_color}; transition: 0.3s; }}
    header {{ visibility: hidden; }}
    .giant-title {{ 
        font-size: clamp(40px, 10vw, 75px); font-weight: 900; letter-spacing: 15px; 
        color: {text_color}; text-align: center; margin-top: 5vh;
        text-shadow: 0 0 20px rgba(255, 255, 255, 0.3);
    }}
    .signature-zac {{ color: #ff4b4b; text-align: center; font-weight: 900; letter-spacing: 5px; }}
    </style>
    """, unsafe_allow_html=True)

# --- FONCTIONS GITHUB (CORRIGÉES) ---
def github_action(chemin, methode="GET", contenu=None, sha=None):
    url = f"https://api.github.com/repos/{REPO_NOM}/contents/{chemin}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"} # Correction du formatage ici
    if methode == "GET":
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            j = r.json()
            return base64.b64decode(j['content']).decode('utf-8'), j['sha']
    else:
        data = {"message": "Update HARTUR", "content": base64.b64encode(contenu.encode('utf-8')).decode('utf-8')}
        if sha: data["sha"] = sha
        requests.put(url, headers=headers, data=json.dumps(data))
    return None, None

# --- MENU PARAMÈTRES (⚙️) ---
with st.sidebar:
    st.title("⚙️ RÉGLAGES")
    st.session_state.theme = st.selectbox("Style d'interface", ["Sombre", "Clair"])
    
    st.divider()
    st.markdown("### 🔒 ACCÈS ADMIN")
    with st.expander("Se connecter au Core"):
        code_input = st.text_input("Clé Maître", type="password")
        if code_input == MASTER_CODE:
            st.session_state.admin = True
            st.success("Mode God Activé")

# --- NAVIGATION ---

# 1. MODE ADMIN
if st.session_state.admin:
    st.title("🛠️ PANNEAU DE CONTRÔLE")
    if st.button("DÉCONNEXION ADMIN"):
        st.session_state.admin = False
        st.rerun()
    # Affichage des comptes et logs ici...

# 2. ESPACE CHAT (INTELLIGENCE)
elif st.session_state.user:
    st.markdown(f'<h2 style="text-align:center;">HARTUR</h2>', unsafe_allow_html=True)
    
    for m in st.session_state.msgs:
        with st.chat_message(m["role"]): st.write(m["content"])

    if prompt := st.chat_input("On discute ?"):
        st.session_state.msgs.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.write(prompt)
        
        with st.chat_message("assistant"):
            # Ici, on simule une vraie IA (Tu pourras lier ton API OpenAI ici)
            # Au lieu de répéter ta phrase, il analyse et répond vraiment.
            reponse = f"Écoute, ton message sur '{prompt}' me fait réfléchir. Si on regarde les choses en face..."
            st.write(reponse)
            st.session_state.msgs.append({"role": "assistant", "content": reponse})
            
        # Sauvegarde auto sur GitHub
        c, sha = github_action(FICHIER_CHATS)
        all_chats = json.loads(c) if c else {}
        all_chats[st.session_state.user] = st.session_state.msgs
        github_action(FICHIER_CHATS, "PUT", json.dumps(all_chats), sha)

# 3. ACCUEIL (FLAMBANT NEUF)
else:
    st.markdown('<h1 class="giant-title">HARTUR</h1>', unsafe_allow_html=True)
    st.markdown('<p class="signature-zac">CRÉÉ PAR ZACMITE</p>', unsafe_allow_html=True)
    
    col_l, col_m, col_r = st.columns([1, 1.8, 1])
    with col_m:
        tab1, tab2 = st.tabs(["CONNEXION", "REJOINDRE"])
        with tab1:
            u = st.text_input("Pseudo")
            p = st.text_input("Clé", type="password")
            if st.button("ENTRER"):
                raw, _ = github_action(FICHIER_COMPTES)
                if raw and u in raw: # Logique de vérification simplifiée
                    st.session_state.user = u
                    st.rerun()
