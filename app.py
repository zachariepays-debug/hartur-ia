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

# --- DESIGN & NETTOYAGE ---
st.markdown("""
    <style>
    .stApp { background-color: #030507; color: #e6edf3; }
    header { visibility: hidden; }
    
    /* Centrage du Header */
    .header-box { text-align: center; padding: 30px 0 10px 0; }
    .giant-title { font-size: 55px; font-weight: 900; letter-spacing: 12px; color: white; margin: 0; }
    .signature-zac { color: #ff4b4b; font-size: 12px; letter-spacing: 4px; font-weight: 900; margin-bottom: 20px; }

    /* Bouton Admin à droite */
    .admin-anchor { position: fixed; top: 50%; right: 20px; transform: translateY(-50%); z-index: 1000; }
    
    /* Cacher le header quand on discute */
    .chat-mode .header-box { display: none; }
    </style>
    """, unsafe_allow_html=True)

# --- FONCTIONS GITHUB ---
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
if "messages" not in st.session_state: st.session_state.messages = []

# --- BOUTON ADMIN (CÔTÉ DROIT) ---
if not st.session_state.admin_mode:
    st.markdown('<div class="admin-anchor">', unsafe_allow_html=True)
    if st.button("⚙️"):
        st.session_state.show_admin_input = not st.session_state.get("show_admin_input", False)
    st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.get("show_admin_input"):
    with st.sidebar:
        code = st.text_input("CODE ADMIN", type="password")
        if code == MASTER_CODE:
            st.session_state.admin_mode = True
            st.rerun()

# --- NAVIGATION ---

# 1. COIN ADMIN
if st.session_state.admin_mode:
    st.title("🛠️ COIN ADMIN")
    if st.button("RETOUR"):
        st.session_state.admin_mode = False
        st.rerun()
    # Dossiers de gestion
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📁 Comptes")
        raw, _ = charger_data(FICHIER_COMPTES)
        if raw: st.dataframe(pd.read_csv(StringIO(raw)))
    with col2:
        st.subheader("📁 Historiques")
        # Affichage des convs GitHub

# 2. ESPACE CHAT (ÉPURÉ)
elif st.session_state.user:
    # On vide l'écran du titre pour la discussion
    st.markdown('<div class="chat-mode"></div>', unsafe_allow_html=True)
    
    if st.sidebar.button("Se déconnecter"):
        st.session_state.user = None
        st.session_state.messages = []
        st.rerun()

    # Affichage de la discussion style "Messenger/WhatsApp"
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.write(m["content"])

    if prompt := st.chat_input("Dis-moi tout..."):
        # Ajout message user
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        
        # Réponse HARTUR (Personnalité de confident)
        with st.chat_message("assistant"):
            response = f"Écoute, je t'ai bien reçu. Tu me dis '{prompt}', voilà ce que j'en pense..." 
            st.write(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

# 3. ÉCRAN D'ACCUEIL (CONNEXION)
else:
    st.markdown('<div class="header-box"><h1 class="giant-title">HARTUR</h1><p class="signature-zac">CRÉÉ PAR ZACMITE</p></div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        t1, t2 = st.tabs(["CONNEXION", "S'INSCRIRE"])
        with t1:
            u = st.text_input("Pseudo")
            p = st.text_input("Mot de passe", type="password")
            if st.button("ENTRER"):
                raw, _ = charger_data(FICHIER_COMPTES)
                df = pd.read_csv(StringIO(raw)) if raw else pd.DataFrame(columns=["pseudo", "password"])
                if not df[(df['pseudo'] == u) & (df['password'] == p)].empty:
                    st.session_state.user = u
                    st.rerun()
                else: st.error("Accès refusé.")
        with t2:
            new_u = st.text_input("Nouveau Pseudo")
            new_p = st.text_input("Nouveau Mot de passe", type="password")
            if st.button("VALIDER L'INSCRIPTION"):
                raw, sha = charger_data(FICHIER_COMPTES)
                df = pd.read_csv(StringIO(raw)) if raw else pd.DataFrame(columns=["pseudo", "password"])
                if new_u and new_p and new_u not in df['pseudo'].values:
                    new_df = pd.concat([df, pd.DataFrame({"pseudo":[new_u], "password":[new_p]})])
                    push_github(FICHIER_COMPTES, new_df.to_csv(index=False), f"Inscrit: {new_u}", sha)
                    st.success("Compte créé, connecte-toi !")
