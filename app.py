import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import requests
from datetime import datetime
import time

# ======================================================
# 🎨 CONFIGURATION VISUELLE & CSS AVANCÉ
# ======================================================
st.set_page_config(
    page_title="Hartur IA - Système Intégré",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Design personnalisé pour une interface propre
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 3.5em;
        background: linear-gradient(45deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0px 5px 15px rgba(0,0,0,0.1); }
    .chat-bubble-user {
        background-color: #007bff;
        color: white;
        padding: 15px;
        border-radius: 15px 15px 0px 15px;
        margin-bottom: 10px;
    }
    .chat-bubble-bot {
        background-color: #ffffff;
        color: #333;
        padding: 15px;
        border-radius: 15px 15px 15px 0px;
        margin-bottom: 10px;
        border: 1px solid #e0e0e0;
    }
    </style>
    """, unsafe_allow_html=True)

# ======================================================
# ⚙️ GESTION DES CONNEXIONS (SHEETS & MISTRAL)
# ======================================================

# Connexion sécurisée au Google Sheet
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"Erreur de liaison base de données : {e}")

# Récupération de la clé API Mistral
api_key = st.secrets.get("MISTRAL_KEY")

# ======================================================
# 💾 FONCTIONS DE GESTION DES DONNÉES
# ======================================================

def charger_donnees(onglet):
    """Récupère les données d'un onglet spécifique"""
    try:
        return conn.read(worksheet=onglet, ttl=0)
    except Exception:
        return pd.DataFrame()

def sauvegarder_donnees(onglet, df):
    """Met à jour les données dans le Google Sheet"""
    try:
        conn.update(worksheet=onglet, data=df)
        return True
    except Exception as e:
        st.error(f"Erreur de sauvegarde : {e}")
        return False

def verifier_identifiants(pseudo, password):
    """Vérifie la correspondance pseudo/mot de passe"""
    df = charger_donnees("comptes")
    if not df.empty:
        match = df[(df['pseudo'].astype(str) == str(pseudo)) & (df['password'].astype(str) == str(password))]
        return not match.empty
    return False

def inscription_nouvel_utilisateur(pseudo, password):
    """Inscrit un utilisateur si le pseudo est libre"""
    df = charger_donnees("comptes")
    if not df.empty and pseudo.lower() in df['pseudo'].astype(str).str.lower().values:
        return "existe"
    
    nouveau_df = pd.DataFrame([{"pseudo": pseudo, "password": str(password)}])
    maj_df = pd.concat([df, nouveau_df], ignore_index=True)
    if sauvegarder_donnees("comptes", maj_df):
        return "succes"
    return "erreur"

def enregistrer_historique(user, message, reponse):
    """Archive la discussion dans l'onglet logs"""
    df = charger_donnees("logs")
    maintenant = datetime.now()
    nouvelle_entree = pd.DataFrame([{
        "date": maintenant.strftime("%d/%m/%Y"),
        "heure": maintenant.strftime("%H:%M"),
        "pseudo": user,
        "message": message,
        "reponse": reponse
    }])
    df_final = pd.concat([df, nouvelle_entree], ignore_index=True)
    sauvegarder_donnees("logs", df_final)

# ======================================================
# 🧠 CŒUR IA (MISTRAL API)
# ======================================================

def interroger_hartur(prompt):
    """Envoie la requête à Mistral AI"""
    if not api_key:
        return "⚠️ Erreur : MISTRAL_KEY manquante dans les secrets Streamlit."
    
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
    data = {
        "model": "open-mistral-7b",
        "messages": [
            {"role": "system", "content": "Tu es Hartur, une IA puissante et polie."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=15)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"❌ Erreur IA : {str(e)}"

# ======================================================
# 🎮 NAVIGATION ET ÉTATS
# ======================================================

if "authentifie" not in st.session_state: st.session_state.authentifie = False
if "utilisateur" not in st.session_state: st.session_state.utilisateur = None
if "page_actuelle" not in st.session_state: st.session_state.page_actuelle = "accueil"

def naviguer_vers(nom_page):
    st.session_state.page_actuelle = nom_page
    st.rerun()

# --- BARRE LATÉRALE ---
with st.sidebar:
    st.title("🤖 Hartur Control")
    st.write("---")
    if st.session_state.authentifie:
        st.success(f"Connecté : **{st.session_state.utilisateur}**")
        if st.button("🚪 Déconnexion"):
            st.session_state.authentifie = False
            st.session_state.utilisateur = None
            naviguer_vers("accueil")
    else:
        if st.button("🏠 Accueil"):
            naviguer_vers("accueil")
    
    st.write("---")
    if st.button("🔐 Espace Admin"):
        naviguer_vers("admin")

# ======================================================
# 📑 PAGES DE L'APPLICATION
# ======================================================

# 1. PAGE D'ACCUEIL (LOGINS)
if st.session_state.page_actuelle == "accueil" and not st.session_state.authentifie:
    st.title("🚀 Accès Système Hartur IA")
    col_login, col_signup = st.columns(2)
    
    with col_login:
        st.subheader("🔑 Connexion")
        u_login = st.text_input("Pseudo", key="l1")
        p_login = st.text_input("Mot de passe", type="password", key="p1")
        if st.button("Se connecter"):
            if verifier_identifiants(u_login, p_login):
                st.session_state.authentifie = True
                st.session_state.utilisateur = u_login
                naviguer_vers("chat")
            else:
                st.error("Pseudo ou mot de passe incorrect.")

    with col_signup:
        st.subheader("🆕 Inscription")
        u_sign = st.text_input("Nouveau pseudo", key="l2")
        p_sign = st.text_input("Nouveau mot de passe", type="password", key="p2")
        if st.button("Créer un compte"):
            if u_sign and p_sign:
                res = inscription_nouvel_utilisateur(u_sign, p_sign)
                if res == "succes": st.success("Compte créé ! Vous pouvez vous connecter.")
                elif res == "existe": st.warning("Ce pseudo est déjà pris.")
                else: st.error("Erreur lors de l'inscription.")

# 2. PAGE DE CHAT
elif st.session_state.page_actuelle == "chat" or st.session_state.authentifie:
    if not st.session_state.authentifie: naviguer_vers("accueil")
    
    st.title(f"💬 Console Hartur - {st.session_state.utilisateur}")
    
    # Entrée du chat
    prompt_utilisateur = st.chat_input("Posez votre question ici...")
    
    if prompt_utilisateur:
        with st.chat_message("user"):
            st.markdown(f'<div class="chat-bubble-user">{prompt_utilisateur}</div>', unsafe_allow_html=True)
        
        with st.chat_message("assistant"):
            with st.spinner("Hartur réfléchit..."):
                reponse_ia = interroger_hartur(prompt_utilisateur)
                st.markdown(f'<div class="chat-bubble-bot">{reponse_ia}</div>', unsafe_allow_html=True)
                enregistrer_historique(st.session_state.utilisateur, prompt_utilisateur, reponse_ia)

# 3. PAGE ADMIN
elif st.session_state.page_actuelle == "admin":
    st.title("🔐 Administration")
    code_admin = st.text_input("Code de sécurité", type="password")
    
    if code_admin == "babar":
        tab1, tab2 = st.tabs(["📂 Comptes Utilisateurs", "📜 Logs des Discussions"])
        with tab1:
            st.dataframe(charger_donnees("comptes"), use_container_width=True)
        with tab2:
            st.dataframe(charger_donnees("logs"), use_container_width=True)
    elif code_admin != "":
        st.error("Code admin incorrect.")
    
    if st.button("Retour"): naviguer_vers("accueil")

# Pied de page
st.write("---")
st.caption("Hartur IA v3.1 | Opérationnel")
import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import requests
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="Hartur IA", layout="wide")

# --- CONNEXION ---
# On crée la connexion une seule fois pour toute l'app
conn = st.connection("gsheets", type=GSheetsConnection)

def lire_donnees(onglet):
    try:
        # Utilisation de la méthode simple sans arguments complexes
        return conn.read(worksheet=onglet, ttl=0)
    except:
        return pd.DataFrame()

def ecrire_donnees(onglet, df):
    try:
        conn.update(worksheet=onglet, data=df)
        return True
    except Exception as e:
        st.error(f"Erreur de sauvegarde : {e}")
        return False

# --- LOGIQUE IA ---
def demander_ia(prompt):
    key = st.secrets.get("MISTRAL_KEY")
    if not key: return "Erreur : Clé API manquante."
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {key}"}
    data = {
        "model": "open-mistral-7b",
        "messages": [{"role": "user", "content": prompt}]
    }
    try:
        r = requests.post(url, headers=headers, json=data)
        return r.json()['choices'][0]['message']['content']
    except:
        return "IA indisponible."

# --- NAVIGATION ---
if "user" not in st.session_state: st.session_state.user = None

if st.session_state.user is None:
    st.title("🚀 Inscription / Connexion")
    pseudo = st.text_input("Pseudo")
    mdp = st.text_input("Mot de passe", type="password")
    
    if st.button("Créer un compte"):
        df = lire_donnees("comptes")
        if not df.empty and pseudo in df['pseudo'].values:
            st.warning("Pseudo déjà pris.")
        else:
            nouveau_compte = pd.DataFrame([{"pseudo": pseudo, "password": str(mdp)}])
            # On fusionne et on sauvegarde
            if ecrire_donnees("comptes", pd.concat([df, nouveau_compte], ignore_index=True)):
                st.success("Compte créé ! Connectez-vous.")

    if st.button("Se connecter"):
        df = lire_donnees("comptes")
        if not df.empty and ((df['pseudo'] == pseudo) & (df['password'] == str(mdp))).any():
            st.session_state.user = pseudo
            st.rerun()
        else:
            st.error("Identifiants incorrects.")

else:
    st.title(f"💬 Chat avec Hartur ({st.session_state.user})")
    if st.button("Déconnexion"):
        st.session_state.user = None
        st.rerun()
    
    prompt = st.chat_input("Votre message...")
    if prompt:
        st.write(f"**Vous:** {prompt}")
        reponse = demander_ia(prompt)
        st.write(f"**Hartur:** {reponse}")
        
        # Log du message
        df_logs = lire_donnees("logs")
        nouveau_log = pd.DataFrame([{
            "date": datetime.now().strftime("%d/%m/%Y"),
            "pseudo": st.session_state.user,
            "message": prompt,
            "reponse": reponse
        }])
        ecrire_donnees("logs", pd.concat([df_logs, nouveau_log], ignore_index=True))
