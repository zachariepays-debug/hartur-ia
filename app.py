import streamlit as st
import pandas as pd
import requests
import base64
import json
from io import StringIO
from datetime import datetime

# ==========================================
# ⚙️ CONFIGURATION & SECRETS
# ==========================================
REPO_NOM = "zachariepays-debug/Hartur-ia" 
FICHIER_COMPTES = "comptes.csv"
FICHIER_CHATS = "conversations.json"
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
MASTER_CODE = "babar" # Ton code pour le God Mode

st.set_page_config(page_title="HARTUR | NEURAL OS", layout="wide", page_icon="💀")

# ==========================================
# 🎨 DESIGN SYSTÈME (FLASHY & CLEAN)
# ==========================================
st.markdown(f"""
    <style>
    /* Fond OLED et suppression des bordures Streamlit */
    .stApp {{ background-color: #030507; color: #e6edf3; font-family: 'Inter', sans-serif; }}
    header {{ visibility: hidden; }}
    
    /* Titre HARTUR Blanc Flashy */
    .giant-title {{ 
        font-size: clamp(40px, 10vw, 80px); 
        font-weight: 900; 
        letter-spacing: 20px; 
        color: #ffffff; 
        text-align: center;
        text-shadow: 0 0 30px rgba(255, 255, 255, 0.5);
        margin-top: 50px;
        margin-bottom: 0px;
    }}
    .signature-zac {{ 
        color: #ff4b4b; text-align: center; font-size: 14px; 
        letter-spacing: 6px; font-weight: 900; margin-bottom: 40px; 
        opacity: 0.8;
    }}

    /* Bouton Admin "Fantôme" à droite */
    .admin-trigger {{
        position: fixed; top: 20px; right: 20px; z-index: 1000;
        background: rgba(255,255,255,0.05); border: 1px solid #30363d;
        padding: 10px; border-radius: 8px; cursor: pointer;
    }}

    /* Optimisation Mobile du pavé de connexion */
    .stTabs [data-baseweb="tab-list"] {{ justify-content: center; }}
    div.stButton > button {{
        background: #ffffff !important; color: #000000 !important;
        font-weight: 900 !important; border: none !important;
        width: 100% !important; border-radius: 5px !important;
    }}
    
    /* Mode Chat : On cache le titre pour l'immersion */
    .chat-active .giant-title, .chat-active .signature-zac {{ display: none; }}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 💾 LOGIQUE GITHUB (PERSISTENCE TOTALE)
# ==========================================
def charger_github(chemin):
    url = f"https://api.github.com/repos/{{REPO_NOM}}/contents/{{chemin}}"
    headers = {{"Authorization": f"token {{GITHUB_TOKEN}}"}}
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        j = r.json()
        return base64.b64decode(j['content']).decode('utf-8'), j['sha']
    return None, None

def sauvegarder_github(chemin, contenu, msg, sha=None):
    url = f"https://api.github.com/repos/{{REPO_NOM}}/contents/{{chemin}}"
    headers = {{"Authorization": f"token {{GITHUB_TOKEN}}"}}
    data = {{"message": msg, "content": base64.b64encode(contenu.encode('utf-8')).decode('utf-8')}}
    if sha: data["sha"] = sha
    requests.put(url, headers=headers, data=json.dumps(data))

# ==========================================
# 🚀 INITIALISATION DU SYSTÈME
# ==========================================
if "user" not in st.session_state: st.session_state.user = None
if "admin" not in st.session_state: st.session_state.admin = False
if "msgs" not in st.session_state: st.session_state.msgs = []

# ==========================================
# 🛡️ COIN ADMIN (GOD MODE)
# ==========================================
st.sidebar.markdown("### ⚙️")
if st.sidebar.checkbox("Accès Core"):
    pwd = st.sidebar.text_input("Clé Admin", type="password")
    if pwd == MASTER_CODE:
        st.session_state.admin = True

if st.session_state.admin:
    st.title("🛠️ COIN ADMIN : GOD MODE")
    if st.button("QUITTER ADMIN"):
        st.session_state.admin = False
        st.rerun()
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📁 RÉPERTOIRE COMPTES")
        raw, _ = charger_github(FICHIER_COMPTES)
        if raw: st.dataframe(pd.read_csv(StringIO(raw)), use_container_width=True)
    with col2:
        st.subheader("📁 HISTORIQUE GLOBAL")
        # Ici tu peux charger et lire toutes les discussions

# ==========================================
# 💬 INTERFACE DE DISCUSSION (ADDICTIVE)
# ==========================================
elif st.session_state.user:
    st.markdown('<div class="chat-active"></div>', unsafe_allow_html=True)
    
    if st.sidebar.button("DÉCONNEXION"):
        st.session_state.user = None
        st.rerun()

    # Affichage de l'historique
    for m in st.session_state.msgs:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    # Entrée utilisateur
    if prompt := st.chat_input("Dis-moi tout, je suis là..."):
        st.session_state.msgs.append({{"role": "user", "content": prompt}})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        with st.chat_message("assistant"):
            # Personnalité "Confident / Pote"
            reponse = f"Écoute, entre nous, pour ton histoire de '{{prompt}}', voilà ce que je pense vraiment..."
            st.markdown(reponse)
            st.session_state.msgs.append({{"role": "assistant", "content": reponse}})
            
        # SAUVEGARDE GITHUB AUTOMATIQUE
        convs, sha = charger_github(FICHIER_CHATS)
        data_convs = json.loads(convs) if convs else {{}}
        data_convs[st.session_state.user] = st.session_state.msgs
        sauvegarder_github(FICHIER_CHATS, json.dumps(data_convs), f"Chat update: {{st.session_state.user}}", sha)

# ==========================================
# 🔐 ÉCRAN D'ACCUEIL (CONNEXION / INSCRIPTION)
# ==========================================
else:
    st.markdown('<h1 class="giant-title">HARTUR</h1>', unsafe_allow_html=True)
    st.markdown('<p class="signature-zac">CRÉÉ PAR ZACMITE</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.8, 1])
    with col2:
        t1, t2 = st.tabs(["CONNEXION", "S'INSCRIRE"])
        
        with t1:
            u = st.text_input("Pseudo")
            p = st.text_input("Mot de passe", type="password")
            if st.button("DÉVERROUILLER"):
                raw, _ = charger_github(FICHIER_COMPTES)
                if raw:
                    df = pd.read_csv(StringIO(raw))
                    if not df[(df['pseudo'] == u) & (df['password'] == p)].empty:
                        st.session_state.user = u
                        # Récupérer l'historique au login
                        c, _ = charger_github(FICHIER_CHATS)
                        if c: st.session_state.msgs = json.loads(c).get(u, [])
                        st.rerun()
                    else: st.error("Accès refusé.")

        with t2:
            nu = st.text_input("Nouveau Pseudo")
            np = st.text_input("Clé de sécurité", type="password")
            if st.button("CRÉER MON ACCÈS"):
                raw, sha = charger_github(FICHIER_COMPTES)
                df = pd.read_csv(StringIO(raw)) if raw else pd.DataFrame(columns=["pseudo", "password"])
                if nu and np and nu not in df['pseudo'].values:
                    new_df = pd.concat([df, pd.DataFrame({{"pseudo":[nu], "password":[np]}})])
                    sauvegarder_github(FICHIER_COMPTES, new_df.to_csv(index=False), f"New user: {{nu}}", sha)
                    st.success("Compte activé. Connecte-toi !")
