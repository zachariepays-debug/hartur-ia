import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import requests
from datetime import datetime

# ======================================================
# 🎨 CONFIGURATION VISUELLE & CSS
# ======================================================
st.set_page_config(
    page_title="Hartur IA - Système Intégré",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style CSS personnalisé pour améliorer l'interface
st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background-color: #4CAF50;
        color: white;
    }
    .stTextInput>div>div>input {
        border-radius: 10px;
    }
    .chat-bubble {
        padding: 15px;
        border-radius: 15px;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# ======================================================
# ⚙️ CONNEXIONS (GOOGLE SHEETS & API)
# ======================================================

# Connexion au Google Sheet (doit être configuré dans les Secrets Streamlit)
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"Erreur de configuration Google Sheets : {e}")

# Clé API Mistral
api_key = st.secrets.get("MISTRAL_KEY")

# ======================================================
# 💾 FONCTIONS BASE DE DONNÉES
# ======================================================

def get_data(sheet_name):
    """Récupère les données d'un onglet spécifique"""
    try:
        return conn.read(worksheet=sheet_name, ttl=0)
    except Exception as e:
        st.error(f"Erreur lors de la lecture de l'onglet {sheet_name}: {e}")
        return pd.DataFrame()

def save_data(sheet_name, dataframe):
    """Sauvegarde les données dans un onglet spécifique"""
    try:
        conn.update(worksheet=sheet_name, data=dataframe)
        return True
    except Exception as e:
        st.error(f"Erreur lors de la sauvegarde dans {sheet_name}: {e}")
        return False

def check_login(user, pwd):
    """Vérifie les identifiants"""
    df = get_data("comptes")
    if not df.empty:
        # Conversion en string pour éviter les erreurs de type
        user_str = str(user)
        pwd_str = str(pwd)
        match = df[(df['pseudo'].astype(str) == user_str) & (df['password'].astype(str) == pwd_str)]
        return not match.empty
    return False

def signup_user(user, pwd):
    """Inscrit un nouvel utilisateur"""
    df = get_data("comptes")
    if user.lower() in df['pseudo'].astype(str).str.lower().values:
        return "existe"
    
    new_user = pd.DataFrame([{"pseudo": user, "password": str(pwd)}])
    updated_df = pd.concat([df, new_user], ignore_index=True)
    if save_data("comptes", updated_df):
        return "succes"
    return "erreur"

def add_log(user, message, response):
    """Enregistre une interaction dans les logs"""
    df = get_data("logs")
    now = datetime.now()
    new_log = pd.DataFrame([{
        "date": now.strftime("%d/%m/%Y"),
        "heure": now.strftime("%H:%M"),
        "pseudo": user,
        "message": message,
        "reponse": response
    }])
    updated_df = pd.concat([df, new_log], ignore_index=True)
    save_data("logs", updated_df)

# ======================================================
# 🧠 LOGIQUE IA (MISTRAL)
# ======================================================

def ask_hartur(prompt):
    if not api_key:
        return "⚠️ Configuration manquante : MISTRAL_KEY non trouvée."
    
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    data = {
        "model": "open-mistral-7b",
        "messages": [
            {"role": "system", "content": "Tu es Hartur, une IA performante. Réponds de façon claire."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"❌ Erreur IA : {str(e)}"

# ======================================================
# 🖥️ NAVIGATION & ÉTATS DE SESSION
# ======================================================

if "auth" not in st.session_state: st.session_state.auth = False
if "user" not in st.session_state: st.session_state.user = None
if "page" not in st.session_state: st.session_state.page = "accueil"

def logout():
    st.session_state.auth = False
    st.session_state.user = None
    st.session_state.page = "accueil"
    st.rerun()

# --- BARRE LATÉRALE ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712035.png", width=100)
    st.title("Menu Hartur")
    
    if st.session_state.auth:
        st.write(f"👤 Connecté en tant que : **{st.session_state.user}**")
        if st.button("Déconnexion"):
            logout()
    else:
        if st.button("🏠 Accueil"):
            st.session_state.page = "accueil"
            st.rerun()
    
    st.markdown("---")
    if st.button("🔐 Accès Admin"):
        st.session_state.page = "admin"
        st.rerun()

# --- LOGIQUE DES PAGES ---

# 1. PAGE ACCUEIL
if st.session_state.page == "accueil" and not st.session_state.auth:
    st.title("🤖 Système Hartur IA")
    st.info("Bienvenue. Veuillez vous connecter ou créer un compte pour accéder à l'IA.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Connexion")
        l_user = st.text_input("Pseudo", key="l_u")
        l_pwd = st.text_input("Mot de passe", type="password", key="l_p")
        if st.button("Se connecter"):
            if check_login(l_user, l_pwd):
                st.session_state.auth = True
                st.session_state.user = l_user
                st.session_state.page = "chat"
                st.success("Connexion réussie !")
                st.rerun()
            else:
                st.error("Identifiants incorrects.")

    with col2:
        st.subheader("Inscription")
        s_user = st.text_input("Nouveau Pseudo", key="s_u")
        s_pwd = st.text_input("Nouveau Mot de passe", type="password", key="s_p")
        if st.button("Créer mon compte"):
            if s_user and s_pwd:
                res = signup_user(s_user, s_pwd)
                if res == "succes":
                    st.success("Compte créé ! Connectez-vous à gauche.")
                elif res == "existe":
                    st.warning("Ce pseudo est déjà utilisé.")
                else:
                    st.error("Erreur lors de l'enregistrement.")
            else:
                st.error("Veuillez remplir tous les champs.")

# 2. PAGE CHAT (Connecté)
elif st.session_state.auth or st.session_state.page == "chat":
    st.title(f"💬 Espace de Discussion - {st.session_state.user}")
    
    # Zone d'affichage des messages
    chat_container = st.container()
    
    # Entrée utilisateur
    user_query = st.chat_input("Posez votre question à Hartur...")
    
    if user_query:
        with st.chat_message("user"):
            st.write(user_query)
        
        with st.chat_message("assistant"):
            with st.spinner("Hartur réfléchit..."):
                response = ask_hartur(user_query)
                st.write(response)
                # Sauvegarde automatique dans l'onglet logs
                add_log(st.session_state.user, user_query, response)

# 3. PAGE ADMIN
elif st.session_state.page == "admin":
    st.title("🔐 Administration du Système")
    master_key = st.text_input("Code Maître", type="password")
    
    if master_key == "babar":
        tab_users, tab_logs = st.tabs(["👥 Gestion Comptes", "📜 Historique Logs"])
        
        with tab_users:
            st.subheader("Base de données des utilisateurs")
            df_u = get_data("comptes")
            st.dataframe(df_u, use_container_width=True)
            
        with tab_logs:
            st.subheader("Historique complet des conversations")
            df_l = get_data("logs")
            st.dataframe(df_l, use_container_width=True)
            
    elif master_key != "":
        st.error("Code incorrect.")
        
    if st.button("Retour à l'accueil"):
        st.session_state.page = "accueil"
        st.rerun()

# ======================================================
# PIED DE PAGE
# ======================================================
st.markdown("---")
st.caption("Hartur IA v2.4 - Système sécurisé par Google Sheets")
