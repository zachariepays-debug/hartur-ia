import streamlit as st
import pandas as pd
import requests
import base64
import json
from io import StringIO
from datetime import datetime

# --- CONFIGURATION CORE ---
REPO_NOM = "zachariepays-debug/Hartur-ia" 
FICHIER_COMPTES = "comptes.csv"
FICHIER_CHATS = "conversations.json"
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
MASTER_CODE = "babar"

st.set_page_config(page_title="HARTUR | NEURAL OS", layout="wide", page_icon="💀")

# --- DESIGN SYSTEM (CSS AVANCÉ) ---
st.markdown("""
    <style>
    /* Global */
    .stApp { background-color: #030507; color: #e6edf3; font-family: 'Inter', sans-serif; }
    header { visibility: hidden; }
    
    /* Centrage Header */
    .header-box { text-align: center; padding: 60px 0 30px 0; width: 100%; }
    .giant-title { font-size: clamp(50px, 10vw, 90px); font-weight: 900; letter-spacing: 20px; color: white; margin: 0; text-shadow: 0 0 30px rgba(255, 75, 75, 0.4); }
    .hook-text { color: #8b949e; font-size: 18px; letter-spacing: 5px; margin-top: 10px; }
    .signature-zac { color: #ff4b4b; font-size: 14px; letter-spacing: 6px; text-transform: uppercase; margin-bottom: 20px; font-weight: 900; opacity: 0.8; }

    /* Bouton Admin en haut à droite */
    .st-emotion-cache-17l0fky { display: none; } /* Cache le menu Streamlit */
    .admin-anchor { position: fixed; top: 20px; right: 20px; z-index: 9999; }
    
    /* Bulles de Chat Custom */
    .stChatMessage { background: transparent !important; border: none !important; }
    [data-testid="stChatMessageAvatarAssistant"] { background-color: #ff4b4b !important; border-radius: 50%; border: 2px solid white; }
    [data-testid="stChatMessageAvatarUser"] { background-color: #58a6ff !important; border-radius: 5px; }

    /* Offline Screen */
    .offline-screen {
        height: 80vh; display: flex; flex-direction: column; align-items: center; justify-content: center;
        background: radial-gradient(circle, #1a0505 0%, #030507 100%);
    }
    .offline-title { font-size: 40px; color: #ff4b4b; font-weight: 900; text-transform: uppercase; letter-spacing: 10px; animation: pulse 2s infinite; }
    @keyframes pulse { 0% { opacity: 0.6; } 50% { opacity: 1; } 100% { opacity: 0.6; } }

    /* Boutons */
    div.stButton > button {
        background: #0d1117 !important; border: 1px solid #30363d !important; color: white !important;
        padding: 12px 24px !important; border-radius: 4px !important; font-weight: bold !important; transition: 0.3s;
    }
    div.stButton > button:hover { border-color: #ff4b4b !important; color: #ff4b4b !important; box-shadow: 0 0 20px rgba(255,75,75,0.2); }
    </style>
    """, unsafe_allow_html=True)

# --- FONCTIONS GITHUB (PERSISTENCE INFINIE) ---
def push_to_github(chemin, contenu_str, message_commit, sha=None):
    url = f"https://api.github.com/repos/{REPO_NOM}/contents/{chemin}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    data = {
        "message": message_commit,
        "content": base64.b64encode(contenu_str.encode('utf-8')).decode('utf-8')
    }
    if sha: data["sha"] = sha
    requests.put(url, headers=headers, data=json.dumps(data))

def charger_fichier(chemin):
    url = f"https://api.github.com/repos/{REPO_NOM}/contents/{chemin}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        j = r.json()
        return base64.b64decode(j['content']).decode('utf-8'), j['sha']
    return None, None

# --- INITIALISATION ---
if "user" not in st.session_state: st.session_state.user = None
if "admin_mode" not in st.session_state: st.session_state.admin_mode = False
if "hartur_power" not in st.session_state: st.session_state.hartur_power = True

# --- HEADER SYNCHRONISÉ ---
st.markdown(f"""
    <div class="header-box">
        <h1 class="giant-title">HARTUR</h1>
        <p class="hook-text">SYSTÈME NEURAL AVANCÉ</p>
        <p class="signature-zac">BY ZACMITE</p>
    </div>
""", unsafe_allow_html=True)

# --- BOUTON ADMIN EN HAUT À DROITE ---
st.markdown('<div class="admin-anchor">', unsafe_allow_html=True)
if st.button("⚙️"):
    st.session_state.admin_access_trigger = True
st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.get("admin_access_trigger"):
    code = st.sidebar.text_input("CLÉ ADMIN", type="password")
    if code == MASTER_CODE:
        st.session_state.admin_mode = True
        st.session_state.admin_access_trigger = False

# --- LOGIQUE D'AFFICHAGE ---

# 1. MODE ADMIN (LE COIN ADMIN)
if st.session_state.admin_mode:
    st.markdown("### 🛠️ COIN ADMIN")
    if st.button("← RETOUR"):
        st.session_state.admin_mode = False
        st.rerun()

    st.session_state.hartur_power = st.toggle("ALIMENTATION GÉNÉRALE", value=st.session_state.hartur_power)
    
    col_a, col_b = st.columns(2)
    df_c, _ = charger_comptes()
    col_a.metric("UTILISATEURS INSCRITS", len(df_c))
    
    with st.expander("📁 RÉPERTOIRE DES COMPTES"):
        st.dataframe(df_c, use_container_width=True)

    with st.expander("📁 HISTORIQUE DES CONVERSATIONS"):
        chats_json, _ = charger_fichier(FICHIER_CHATS)
        if chats_json:
            data = json.loads(chats_json)
            for pseudo, msgs in data.items():
                with st.expander(f"👤 {pseudo} (Dernier : {msgs[-1]['timestamp'] if msgs else 'N/A'})"):
                    for m in msgs:
                        st.write(f"**{'Lui' if m['role']=='user' else 'HARTUR'}** : {m['content']}")
                    st.download_button("Télécharger Log", json.dumps(msgs), f"log_{pseudo}.json")

# 2. HARTUR ÉTEINT
elif not st.session_state.hartur_power:
    st.markdown("""
        <div class="offline-screen">
            <div class="offline-title">HARTUR HORS TENSION</div>
            <p style="color:#8b949e; font-family:monospace;">Le système est actuellement en veille profonde.</p>
        </div>
    """, unsafe_allow_html=True)

# 3. CHAT (SI CONNECTÉ)
elif st.session_state.user:
    # Personnalité de HARTUR : Le pote confident un peu brut
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Ouais, c'est HARTUR. T'es connecté, balance ce que t'as sur le cœur, je garde tout pour moi. On fait quoi ?"}]

    for m in st.session_state.messages:
        avatar = "🤖" if m["role"] == "assistant" else "👤"
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    if prompt := st.chat_input("Parle-moi..."):
        st.session_state.messages.append({"role": "user", "content": prompt, "timestamp": str(datetime.now())})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        with st.chat_message("assistant"):
            # Ici la personnalité est injectée
            response = f"Écoute, pour ton truc de '{prompt}', voilà ce que je pense : [Réponse IA avec ton style]" 
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response, "timestamp": str(datetime.now())})

# 4. CONNEXION / INSCRIPTION
else:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        t1, t2 = st.tabs(["CONNEXION", "S'INSCRIRE"])
        with t1:
            u = st.text_input("PSEUDO")
            p = st.text_input("MOT DE PASSE", type="password")
            if st.button("ENTRER"):
                df, _ = charger_comptes()
                if not df[(df['pseudo'] == u) & (df['password'] == p)].empty:
                    st.session_state.user = u
                    st.rerun()
        with t2:
            st.warning("Veuillez demander l'accès directement à Zacmite.")
