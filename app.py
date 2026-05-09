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
FICHIER_CHATS = "conversations.json" # Fichier pour sauvegarder l'historique
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
MASTER_CODE = "babar"

st.set_page_config(page_title="HARTUR | OS", layout="wide", page_icon="⚡")

# --- DESIGN & STYLE ---
st.markdown("""
    <style>
    /* Fond OLED et textes */
    .stApp { background-color: #05070a; color: #e6edf3; }
    
    /* Header claque */
    .main-header { text-align: center; padding: 40px 0 20px 0; }
    .giant-title { font-size: 65px; font-weight: 900; letter-spacing: 15px; color: white; margin: 0; text-shadow: 0 0 20px rgba(255, 75, 75, 0.2); }
    .hook-text { color: #8b949e; font-size: 16px; font-weight: bold; margin-top: 5px; letter-spacing: 2px; }
    .signature-zac { color: #ff4b4b; font-size: 14px; letter-spacing: 4px; text-transform: uppercase; margin-bottom: 20px; font-weight: 900; }
    
    /* Bouton Admin discret */
    .admin-btn { position: fixed; bottom: 15px; right: 15px; opacity: 0.2; transition: 0.3s; z-index: 1000; }
    .admin-btn:hover { opacity: 1; }
    
    /* Personnalisation des boutons */
    div.stButton > button {
        background: #161b22 !important;
        border: 1px solid #30363d !important;
        color: white !important;
        border-radius: 8px !important;
        padding: 10px 20px !important;
        transition: 0.3s;
    }
    div.stButton > button:hover { border-color: #ff4b4b !important; box-shadow: 0 0 15px rgba(255, 75, 75, 0.3) !important; }
    
    /* Message d'erreur HARTUR OFFLINE */
    .offline-msg { text-align: center; color: #ff4b4b; font-size: 40px; font-weight: 900; margin-top: 100px; text-shadow: 0 0 20px red; }
    </style>
    """, unsafe_allow_html=True)

# --- FONCTIONS GITHUB ---
def charger_fichier(chemin):
    url = f"https://api.github.com/repos/{REPO_NOM}/contents/{chemin}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        content = base64.b64decode(response.json()['content']).decode('utf-8')
        return content, response.json()['sha']
    return None, None

def charger_comptes():
    content, sha = charger_fichier(FICHIER_COMPTES)
    if content:
        return pd.read_csv(StringIO(content)), sha
    return pd.DataFrame(columns=["pseudo", "password"]), None

def charger_conversations():
    content, sha = charger_fichier(FICHIER_CHATS)
    if content:
        try:
            return json.loads(content), sha
        except:
            return {}, sha
    return {}, None

# --- INITIALISATION ---
if "user" not in st.session_state: st.session_state.user = None
if "admin_mode" not in st.session_state: st.session_state.admin_mode = False
if "hartur_actif" not in st.session_state: st.session_state.hartur_actif = True

# --- HEADER (Accroche stylée) ---
st.markdown("""
    <div class="main-header">
        <h1 class="giant-title">HARTUR</h1>
        <p class="hook-text">SYSTÈME NEURAL AVANCÉ</p>
        <p class="signature-zac">CRÉÉ PAR ZACMITE</p>
    </div>
""", unsafe_allow_html=True)

# --- ACCÈS ADMIN DISCRET ---
with st.sidebar:
    st.markdown("### ⚙️")
    if st.checkbox("Système Core", help="Accès restreint"):
        code = st.text_input("Clé de déchiffrement", type="password")
        if code == MASTER_CODE:
            st.session_state.admin_mode = True
        else:
            st.session_state.admin_mode = False

# --- LOGIQUE D'AFFICHAGE ---

# 1. HARTUR EST DÉSACTIVÉ (KILL SWITCH)
if not st.session_state.hartur_actif and not st.session_state.admin_mode:
    st.markdown('<div class="offline-msg">⚠️ SYSTÈME HARTUR HORS LIGNE ⚠️<br><span style="font-size:20px; color:#8b949e;">Maintenance en cours. Rallumage prévu par zacmite.</span></div>', unsafe_allow_html=True)
    st.stop()

# 2. PANNEAU ADMIN COMPLET (LE RETOUR)
elif st.session_state.admin_mode:
    st.subheader("🛠️ Interface Administrateur Globale")
    
    # Interrupteur Général (Kill Switch)
    st.session_state.hartur_actif = st.toggle("🟢 Alimentation HARTUR (ON/OFF)", value=st.session_state.hartur_actif)
    if not st.session_state.hartur_actif:
        st.warning("HARTUR est actuellement éteint pour les utilisateurs.")

    st.write("---")
    
    # Dossier 1 : Comptes
    with st.expander("📁 Registre : Comptes et Accès"):
        df_comptes, _ = charger_comptes()
        st.dataframe(df_comptes, use_container_width=True)
        st.info("La modification directe nécessite un push GitHub via l'API (à implémenter si besoin).")

    # Dossier 2 : Conversations
    with st.expander("📁 Archives : Base de données des Conversations"):
        chats, _ = charger_conversations()
        if not chats:
            st.write("Aucune conversation archivée pour le moment.")
        else:
            for pseudo, messages in chats.items():
                with st.expander(f"👤 Discussion de {pseudo}"):
                    if messages:
                        st.caption(f"Premier message : {messages[0].get('timestamp', 'Inconnu')}")
                        st.caption(f"Dernier message : {messages[-1].get('timestamp', 'Inconnu')}")
                        st.write("---")
                        # Affichage propre Question / Réponse
                        for msg in messages:
                            if msg["role"] == "user":
                                st.markdown(f"**{pseudo}** : {msg['content']}")
                            else:
                                st.markdown(f"**🤖 HARTUR** : {msg['content']}")
                        
                        # Bouton de téléchargement
                        chat_str = json.dumps(messages, indent=4, ensure_ascii=False)
                        st.download_button(
                            label=f"⬇️ Télécharger le log de {pseudo}",
                            data=chat_str,
                            file_name=f"log_hartur_{pseudo}.json",
                            mime="application/json"
                        )

    if st.button("Fermer l'interface Admin"):
        st.session_state.admin_mode = False
        st.rerun()

# 3. CHAT IA (HARTUR)
elif st.session_state.user:
    # Retrait du "Terminal connecté". Remplacé par une interface épurée.
    if st.sidebar.button("Déconnexion"):
        st.session_state.user = None
        st.rerun()

    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "🤖 Salut, je suis HARTUR. Que puis-je faire pour toi aujourd'hui ?"}]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Initialiser une requête..."):
        # 1. Afficher message user
        st.session_state.messages.append({"role": "user", "content": prompt, "timestamp": str(datetime.now())})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # 2. Réponse de HARTUR
        with st.chat_message("assistant"):
            response = f"🤖 C'est noté. Voici la réponse pour : {prompt}" # Lier à ton API IA ici
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response, "timestamp": str(datetime.now())})
            
        # 3. (Optionnel) Ici tu mettras la fonction pour sauvegarder st.session_state.messages dans FICHIER_CHATS sur GitHub

# 4. CONNEXION (Style Classe)
else:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["DÉVERROUILLER", "S'ENREGISTRER"])
        
        with tab1:
            u = st.text_input("Identifiant")
            p = st.text_input("Clé d'authentification", type="password")
            if st.button("Authentification"):
                df, _ = charger_comptes()
                if not df[(df['pseudo'] == u) & (df['password'] == p)].empty:
                    st.session_state.user = u
                    st.rerun()
                else:
                    st.error("Accès refusé.")
        
        with tab2:
            st.info("Veuillez demander l'accès à zacmite.")
