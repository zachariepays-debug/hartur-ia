import streamlit as st
import pandas as pd
import requests
import base64
import json
from io import StringIO

# --- CONFIGURATION GITHUB ---
REPO_NOM = "zachariepays-debug/Hartur-ia" 
FICHIER_COMPTES = "comptes.csv"
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
MASTER_CODE = "babar"

st.set_page_config(page_title="HARTUR | SYSTEM", layout="wide", page_icon="🔥")

# --- STYLE CSS ÉPURÉ ---
st.markdown("""
    <style>
    .stApp { background-color: #05070a; color: #e6edf3; }
    .giant-title { font-size: 60px; font-weight: 900; letter-spacing: 10px; color: white; text-align: center; margin: 0; }
    .signature-zac { color: #58a6ff; font-weight: bold; text-align: center; margin-bottom: 30px; }
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

def sauvegarder_comptes(df, sha):
    url = f"https://api.github.com/repos/{REPO_NOM}/contents/{FICHIER_COMPTES}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    csv_content = df.to_csv(index=False)
    data = {
        "message": "Mise à jour des comptes",
        "content": base64.b64encode(csv_content.encode('utf-8')).decode('utf-8'),
        "sha": sha
    }
    requests.put(url, headers=headers, data=json.dumps(data))

# --- INTERFACE ---
st.markdown('<h1 class="giant-title">HARTUR</h1>', unsafe_allow_html=True)
st.markdown('<p class="signature-zac">Créé par zacmite</p>', unsafe_allow_html=True)

if "user" not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    tab1, tab2 = st.tabs(["CONNEXION", "INSCRIPTION"])
    
    with tab1:
        p_login = st.text_input("Pseudo", key="l_user")
        m_login = st.text_input("Mot de passe", type="password", key="l_pass")
        if st.button("Se connecter"):
            df, _ = charger_comptes()
            user_data = df[(df['pseudo'] == p_login) & (df['password'] == m_login)]
            if not user_data.empty:
                st.session_state.user = p_login
                st.rerun()
            else:
                st.error("Identifiants incorrects")

    with tab2:
        new_u = st.text_input("Nouveau Pseudo")
        new_p = st.text_input("Nouveau Mot de passe", type="password")
        m_code = st.text_input("Code Maître", type="password")
        if st.button("Créer le compte"):
            if m_code == MASTER_CODE:
                df, sha = charger_comptes()
                if new_u in df['pseudo'].values:
                    st.warning("Pseudo déjà utilisé")
                else:
                    new_row = pd.DataFrame({"pseudo": [new_u], "password": [new_p]})
                    df = pd.concat([df, new_row], ignore_index=True)
                    sauvegarder_comptes(df, sha)
                    st.success("Compte créé ! Connecte-toi.")
            else:
                st.error("Code Maître invalide")
else:
    st.success(f"Bienvenue, {st.session_state.user}")
    if st.button("Déconnexion"):
        st.session_state.user = None
        st.rerun()
    
    st.chat_input("Le terminal est à toi...")
