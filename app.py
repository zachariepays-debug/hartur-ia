[17:17, 09/05/2026] Zach: import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import requests

# --- CONFIGURATION ---
st.set_page_config(page_title="Hartur IA", page_icon="🤖")

# Connexion au Google Sheet (utilise le lien dans tes Secrets)
conn = st.connection("gsheets", type=GSheetsConnection)

# --- FONCTIONS DE SAUVEGARDE ---

def inscrire_utilisateur(pseudo, password):
    try:
        # Lit le tableau actuel (onglet 'comptes')
        df = conn.read(worksheet="comptes", ttl=0)
        
        # Vérifie si le pseudo existe déjà
        if pseudo.lower() in df['pseudo'].astype(str).str.lower().values:
            return False
        
        # Ajoute le nouveau compte
        new_user = pd.DataFrame([{"pseudo": pseudo, "password": str(password)}])
        df = pd.concat([df, new_user], ignore_index=True)
        
        # Envoie la mise à jour vers Google Sheets
        conn.update(worksheet="comptes", data=df)
        return True
    except Exception as e:
        st.error(f"Erreur de connexion au Sheet : {e}")
        return False

def verifier_connexion(pseudo, password):
    try:
        df = conn.read(worksheet="comptes", ttl=0)
        match = df[(df['pseudo'].astype(str) == str(pseudo)) & (df['password'].astype(str) == str(password))]
        return not match.empty
    except:
        return False

# --- INTERFACE ---

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    tab1, tab2 = st.tabs(["Connexion", "Créer un compte"])
    
    with tab1:
        u = st.text_input("Pseudo", key="login_u")
        p = st.text_input("Mot de passe", type="password", key="login_p")
        if st.button("Se connecter"):
            if verifier_connexion(u, p):
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Pseudo ou mot de passe incorrect")

    with tab2:
        new_u = st.text_input("Choisir un Pseudo", key="reg_u")
        new_p = st.text_input("Choisir un Mot de passe", type="password", key="reg_p")
        if st.button("S'inscrire"):
            if inscrire_utilisateur(new_u, new_p):
                st.success("Compte créé avec succès ! Tu peux te connecter.")
            else:
                st.error("Ce pseudo est déjà pris ou erreur technique.")

else:
    st.title("🤖 Hartur IA est prêt")
    st.write(f"Bienvenue {st.session_state.get('login_u', 'ami')} !")
    
    if st.button("Se déconnecter"):
        st.session_state.logged_in = False
        st.rerun()
[17:18, 09/05/2026] Zach: import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import requests
from datetime import datetime

# ======================================================
# ⚙️ CONFIGURATION & CONNEXION
# ======================================================
st.set_page_config(page_title="Hartur IA", page_icon="🤖", layout="wide")

# Récupération des clés dans les Secrets
api_key = st.secrets.get("MISTRAL_KEY")
# Connexion au Google Sheet
conn = st.connection("gsheets", type=GSheetsConnection)

# ======================================================
# 💾 LOGIQUE DE STOCKAGE (GOOGLE SHEETS)
# ======================================================

def login_account(user, pwd):
    try:
        df = conn.read(worksheet="comptes", ttl=0)
        # Vérification exacte pseudo et mot de passe
        match = df[(df['pseudo'].astype(str) == str(user)) & (df['password'].astype(str) == str(pwd))]
        return not match.empty
    except:
        return False

def create_account(user, pwd):
    try:
        df = conn.read(worksheet="comptes", ttl=0)
        # Vérifie si le pseudo existe déjà
        if user.lower() in df['pseudo'].astype(str).str.lower().values:
            return False
        
        # Ajoute la ligne et met à jour Google Sheets
        new_row = pd.DataFrame([{"pseudo": user, "password": str(pwd)}])
        df = pd.concat([df, new_row], ignore_index=True)
        conn.update(worksheet="comptes", data=df)
        return True
    except:
        return False

def sauvegarder_log(user, texte, reponse):
    try:
        df_logs = conn.read(worksheet="logs", ttl=0)
        now = datetime.now()
        new_log = pd.DataFrame([{
            "date": now.strftime("%d-%m-%Y"),
            "heure": now.strftime("%H:%M"),
            "pseudo": user,
            "message": texte,
            "reponse": reponse
        }])
        df_logs = pd.concat([df_logs, new_log], ignore_index=True)
        conn.update(worksheet="logs", data=df_logs)
    except:
        pass

# ======================================================
# 🧠 IA MISTRAL
# ======================================================

def generer_reponse(prompt):
    if not api_key:
        return "Désolé, ma clé API est manquante dans les secrets."
    
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}"}
    data = {
        "model": "open-mistral-7b",
        "messages": [
            {"role": "system", "content": "Tu es Hartur, une IA polie et efficace."},
            {"role": "user", "content": prompt}
        ]
    }
    try:
        r = requests.post(url, headers=headers, json=data)
        return r.json()['choices'][0]['message']['content']
    except:
        return "Une erreur est survenue lors de la connexion à l'IA."

# ======================================================
# 🖥️ INTERFACE UTILISATEUR
# ======================================================

if "page" not in st.session_state: st.session_state.page = "home"
if "username" not in st.session_state: st.session_state.username = None

# --- ACCUEIL ---
if st.session_state.page == "home":
    st.title("🤖 Hartur IA Permanent")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔑 Connexion"):
            st.session_state.page = "login"
            st.rerun()
    with col2:
        if st.button("🆕 Créer un compte"):
            st.session_state.page = "signup"
            st.rerun()

# --- INSCRIPTION ---
elif st.session_state.page == "signup":
    st.subheader("Créer un nouveau compte")
    new_u = st.text_input("Pseudo choisi")
    new_p = st.text_input("Mot de passe choisi", type="password")
    if st.button("Valider l'inscription"):
        if create_account(new_u, new_p):
            st.success("Compte créé ! Tu peux maintenant te connecter.")
            st.session_state.page = "login"
            st.rerun()
        else:
            st.error("Ce pseudo est déjà pris ou le tableau est mal configuré.")
    if st.button("Retour"):
        st.session_state.page = "home"
        st.rerun()

# --- CONNEXION ---
elif st.session_state.page == "login":
    st.subheader("Connexion")
    u = st.text_input("Pseudo")
    p = st.text_input("Mot de passe", type="password")
    if st.button("Entrer"):
        if login_account(u, p):
            st.session_state.username = u
            st.session_state.page = "chat"
            st.rerun()
        else:
            st.error("Identifiants incorrects.")
    if st.button("Retour"):
        st.session_state.page = "home"
        st.rerun()

# --- CHAT ---
elif st.session_state.page == "chat":
    st.title(f"💬 Session de {st.session_state.username}")
    
    if st.sidebar.button("Se déconnecter"):
        st.session_state.page = "home"
        st.session_state.username = None
        st.rerun()

    prompt = st.chat_input("Pose ta question à Hartur...")
    if prompt:
        st.chat_message("user").write(prompt)
        reponse = generer_reponse(prompt)
        st.chat_message("assistant").write(reponse)
        # Sauvegarde automatique dans l'onglet 'logs'
        sauvegarder_log(st.session_state.username, prompt, reponse)

# --- PANEL ADMIN ---
if st.sidebar.button("🔐 Admin"):
    st.session_state.page = "admin"
    st.rerun()

if st.session_state.page == "admin":
    st.title("Panneau d'administration")
    admin_p = st.text_input("Mot de passe maître", type="password")
    if admin_p == "babar":
        st.write("### Liste des utilisateurs (Google Sheets)")
        st.dataframe(conn.read(worksheet="comptes", ttl=0))
        st.write("### Historique des messages")
        st.dataframe(conn.read(worksheet="logs", ttl=0))
    if st.button("Quitter l'admin"):
        st.session_state.page = "home"
        st.rerun()
