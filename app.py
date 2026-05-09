import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import requests
from datetime import datetime
import time

# ======================================================
# 🎨 DESIGN & INTERFACE (CSS AVANCÉ)
# ======================================================
st.set_page_config(
    page_title="Hartur IA - Système Ultime",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Injection de style pour une interface moderne
st.markdown("""
    <style>
    /* Global */
    .main { background-color: #f0f2f6; }
    
    /* Boutons personnalisés */
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        border: none;
        height: 3.5em;
        background: linear-gradient(45deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        font-weight: bold;
        transition: 0.3s;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0px 6px 15px rgba(0,0,0,0.2);
        color: #ffeb3b;
    }
    
    /* Inputs */
    .stTextInput>div>div>input {
        border-radius: 15px;
        border: 1px solid #d1d8e0;
    }

    /* Bulles de Chat */
    .user-msg {
        background-color: #007bff;
        color: white;
        padding: 15px;
        border-radius: 20px 20px 0px 20px;
        margin-bottom: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    .bot-msg {
        background-color: white;
        color: #333;
        padding: 15px;
        border-radius: 20px 20px 20px 0px;
        margin-bottom: 10px;
        border: 1px solid #eee;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# ======================================================
# ⚙️ CONNEXIONS RÉSEAU & CLÉS
# ======================================================

# Initialisation de la connexion Google Sheets
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"❌ Erreur de liaison Google Sheets : {e}")

# Récupération sécurisée de la clé Mistral
MISTRAL_KEY = st.secrets.get("MISTRAL_KEY")

# ======================================================
# 💾 LOGIQUE DE DONNÉES (CRUD GOOGLE SHEETS)
# ======================================================

def charger_feuille(nom_feuille):
    """Charge les données d'un onglet spécifique sans cache (ttl=0)"""
    try:
        return conn.read(worksheet=nom_feuille, ttl=0)
    except Exception as e:
        st.sidebar.error(f"Erreur lecture '{nom_feuille}': {e}")
        return pd.DataFrame()

def sauvegarder_feuille(nom_feuille, dataframe):
    """Écrase les données de l'onglet par le nouveau dataframe"""
    try:
        conn.update(worksheet=nom_feuille, data=dataframe)
        return True
    except Exception as e:
        st.error(f"❌ Échec de l'écriture dans '{nom_feuille}': {e}")
        return False

def verifier_utilisateur(pseudo, password):
    """Vérifie si le combo pseudo/pass est dans 'comptes'"""
    df = charger_feuille("comptes")
    if not df.empty and "pseudo" in df.columns:
        res = df[(df['pseudo'].astype(str) == str(pseudo)) & (df['password'].astype(str) == str(password))]
        return not res.empty
    return False

def inscrire_utilisateur(pseudo, password):
    """Tente d'inscrire un utilisateur s'il n'existe pas"""
    df = charger_feuille("comptes")
    if not df.empty and "pseudo" in df.columns:
        if pseudo.lower() in df['pseudo'].astype(str).str.lower().values:
            return "existe"
    
    # Création de la nouvelle ligne
    nouveau_df = pd.DataFrame([{"pseudo": pseudo, "password": str(password)}])
    final_df = pd.concat([df, nouveau_df], ignore_index=True)
    
    if sauvegarder_feuille("comptes", final_df):
        return "ok"
    return "erreur"

def archive_log(user, question, reponse):
    """Enregistre l'interaction dans l'onglet 'logs'"""
    df = charger_feuille("logs")
    maintenant = datetime.now()
    nouvelle_ligne = pd.DataFrame([{
        "date": maintenant.strftime("%d/%m/%Y"),
        "heure": maintenant.strftime("%H:%M"),
        "pseudo": user,
        "message": question,
        "reponse": reponse
    }])
    updated_logs = pd.concat([df, nouvelle_ligne], ignore_index=True)
    sauvegarder_feuille("logs", updated_logs)

# ======================================================
# 🧠 CŒUR IA (MISTRAL API)
# ======================================================

def appeler_hartur(prompt):
    """Envoie une requête à l'API Mistral"""
    if not MISTRAL_KEY:
        return "⚠️ Erreur : La clé API 'MISTRAL_KEY' est absente des secrets Streamlit."
    
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {MISTRAL_KEY}"
    }
    corps = {
        "model": "open-mistral-7b",
        "messages": [
            {"role": "system", "content": "Tu es Hartur, une IA d'élite. Tu es poli et tu donnes des réponses précises."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }
    
    try:
        r = requests.post(url, headers=headers, json=corps, timeout=15)
        r.raise_for_status()
        return r.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"❌ Erreur de connexion IA : {str(e)}"

# ======================================================
# 🎮 NAVIGATION & ÉTATS DE SESSION
# ======================================================

if "statut" not in st.session_state: st.session_state.statut = "accueil"
if "user_nom" not in st.session_state: st.session_state.user_nom = None

def change_page(nom_page):
    st.session_state.statut = nom_page
    st.rerun()

# --- BARRE LATÉRALE (SIDEBAR) ---
with st.sidebar:
    st.title("🤖 Hartur Control")
    st.write("---")
    if st.session_state.user_nom:
        st.success(f"Connecté : **{st.session_state.user_nom}**")
        if st.button("🚪 Déconnexion"):
            st.session_state.user_nom = None
            change_page("accueil")
    else:
        st.info("Mode Invité")
        if st.button("🏠 Retour Accueil"):
            change_page("accueil")
    
    st.write("---")
    if st.button("🛡️ Administration"):
        change_page("admin")

# ======================================================
# 📑 PAGES DE L'APPLICATION
# ======================================================

# 1. PAGE ACCUEIL (CONNEXION / INSCRIPTION)
if st.session_state.statut == "accueil":
    st.title("🚀 Système Central Hartur IA")
    st.write("Identifiez-vous pour accéder à l'interface de commande.")
    
    col_conn, col_ins = st.columns(2)
    
    with col_conn:
        st.markdown("### 🔑 Connexion")
        u_log = st.text_input("Pseudo", key="ul")
        p_log = st.text_input("Mot de passe", type="password", key="pl")
        if st.button("Se connecter"):
            if verifier_utilisateur(u_log, p_log):
                st.session_state.user_nom = u_log
                change_page("chat")
            else:
                st.error("Identifiants incorrects.")

    with col_ins:
        st.markdown("### 🆕 Inscription")
        u_reg = st.text_input("Pseudo choisi", key="ur")
        p_reg = st.text_input("Mot de passe choisi", type="password", key="pr")
        if st.button("Créer le compte"):
            if u_reg and p_reg:
                resultat = inscrire_utilisateur(u_reg, p_reg)
                if resultat == "ok":
                    st.success("✅ Compte créé avec succès ! Connectez-vous.")
                elif resultat == "existe":
                    st.warning("⚠️ Ce pseudo est déjà utilisé.")
                else:
                    st.error("❌ Erreur technique lors de l'inscription.")
            else:
                st.error("Veuillez remplir tous les champs.")

# 2. PAGE CHAT (INTERFACE UTILISATEUR)
elif st.session_state.statut == "chat":
    if not st.session_state.user_nom:
        change_page("accueil")
    
    st.title(f"💬 Console de Communication : {st.session_state.user_nom}")
    
    # Zone d'interaction
    query = st.chat_input("Envoyez un message à Hartur...")
    
    if query:
        # Affichage utilisateur
        with st.chat_message("user"):
            st.markdown(f'<div class="user-msg">{query}</div>', unsafe_allow_html=True)
        
        # Réponse IA
        with st.chat_message("assistant"):
            with st.spinner("Analyse en cours..."):
                rep = appeler_hartur(query)
                st.markdown(f'<div class="bot-msg">{rep}</div>', unsafe_allow_html=True)
                # Archivage immédiat dans Google Sheets
                archive_log(st.session_state.user_nom, query, rep)

# 3. PAGE ADMIN (GESTION & LOGS)
elif st.session_state.statut == "admin":
    st.title("🔐 Panneau de Contrôle Administrateur")
    admin_pass = st.text_input("Entrez le code de sécurité", type="password")
    
    if admin_pass == "babar":
        st.success("Accès autorisé.")
        t1, t2 = st.tabs(["📂 Base Utilisateurs", "📊 Historique Messages"])
        
        with t1:
            st.write("### Liste des comptes enregistrés")
            data_u = charger_feuille("comptes")
            st.dataframe(data_u, use_container_width=True)
            if st.button("🔄 Actualiser Comptes"): st.rerun()

        with t2:
            st.write("### Logs des conversations")
            data_l = charger_feuille("logs")
            st.dataframe(data_l, use_container_width=True)
            if st.button("🔄 Actualiser Logs"): st.rerun()
            
    elif admin_pass != "":
        st.error("Code de sécurité invalide.")

# ======================================================
# 🏁 PIED DE PAGE
# ======================================================
st.write("---")
st.caption(f"Hartur IA Framework v3.0 | État : Opérationnel | Utilisateur : {st.session_state.user_nom or 'Anonyme'}")
