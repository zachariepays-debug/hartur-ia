import streamlit as st
import pandas as pd
import requests
import base64
import json
from io import StringIO

# --- CONFIGURATION ---
REPO_NOM = "zachariepays-debug/Hartur-ia" 
FICHIER_COMPTES = "comptes.csv"
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
MASTER_CODE = "babar"

st.set_page_config(page_title="HARTUR | SYSTEM", layout="wide", page_icon="⚡")

# --- DESIGN & STYLE ---
st.markdown("""
    <style>
    .stApp { background-color: #05070a; color: #e6edf3; }
    .main-header { text-align: center; padding: 30px 0; }
    .giant-title { font-size: 60px; font-weight: 900; letter-spacing: 12px; color: white; margin: 0; }
    .signature-zac { color: #58a6ff; font-size: 14px; letter-spacing: 4px; text-transform: uppercase; margin-bottom: 20px; }
    
    /* Bouton Admin flottant discret */
    .admin-btn { position: fixed; bottom: 10px; right: 10px; opacity: 0.3; transition: 0.3s; }
    .admin-btn:hover { opacity: 1; }
    </style>
    """, unsafe_allow_html=True)

# --- FONCTIONS GITHUB ---
def charger_comptes():
    url = f"https://api.github.com/repos/{REPO_NOM}/contents/{FICHIER_COMPTES}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        content = base64.b64decode(response.json()['content']).decode('utf-8')
        return pd.read_csv(StringIO(content)), response.json()['sha']
    return pd.DataFrame(columns=["pseudo", "password"]), None

# --- INITIALISATION ---
if "user" not in st.session_state:
    st.session_state.user = None
if "admin_mode" not in st.session_state:
    st.session_state.admin_mode = False

# --- HEADER ---
st.markdown('<div class="main-header"><h1 class="giant-title">HARTUR</h1><p class="signature-zac">Interface par zacmite</p></div>', unsafe_allow_html=True)

# --- ACCÈS ADMIN DISCRET ---
with st.sidebar:
    st.markdown("### ⚙️ Paramètres")
    if st.checkbox("Mode Admin"):
        code = st.text_input("Code Secret", type="password")
        if code == MASTER_CODE:
            st.session_state.admin_mode = True
        else:
            st.error("Code erroné")

# --- AFFICHAGE LOGIQUE ---

# 1. PANNEAU ADMIN
if st.session_state.admin_mode:
    st.subheader("🛠️ Gestion des utilisateurs")
    df, _ = charger_comptes()
    st.dataframe(df, use_container_width=True)
    if st.button("Fermer Admin"):
        st.session_state.admin_mode = False
        st.rerun()

# 2. CHAT IA (SI CONNECTÉ)
elif st.session_state.user:
    st.markdown(f"### 🟢 Terminal Connecté : **{st.session_state.user}**")
    
    # Zone de Chat
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Demande n'importe quoi à HARTUR..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Réponse simulée de l'IA (à lier à ton API IA)
        with st.chat_message("assistant"):
            response = f"Analyse en cours pour : {prompt}..."
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

    if st.sidebar.button("Se déconnecter"):
        st.session_state.user = None
        st.rerun()

# 3. FORMULAIRE DE CONNEXION
else:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab1, tab2 = st.tabs(["CONNEXION", "CRÉER UN COMPTE"])
        
        with tab1:
            u = st.text_input("Pseudo", key="login_u")
            p = st.text_input("Mot de passe", type="password", key="login_p")
            if st.button("Accéder au terminal"):
                df, _ = charger_comptes()
                if not df[(df['pseudo'] == u) & (df['password'] == p)].empty:
                    st.session_state.user = u
                    st.rerun()
                else:
                    st.error("Pseudo ou mot de passe incorrect.")

        with tab2:
            st.write("L'inscription nécessite l'autorisation de Zacmite.")
            # ... Logique d'inscription ici ...
