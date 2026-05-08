import streamlit as st
import os
import requests
from datetime import datetime

# ======================================================
# ⚙️ CONFIGURATION ET SECRETS
# ======================================================
st.set_page_config(page_title="Hartur IA", page_icon="🤖", layout="wide")

# Récupération de ta clé Mistral
api_key = st.secrets.get("MISTRAL_KEY")

# ======================================================
# 💾 GESTION DE LA SESSION (SESSION STATE)
# ======================================================
if "page" not in st.session_state: st.session_state.page = "home"
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "username" not in st.session_state: st.session_state.username = None
if "messages" not in st.session_state: st.session_state.messages = []
if "humeur" not in st.session_state: st.session_state.humeur = "Cool"

# ======================================================
# 📁 SYSTÈME DE FICHIERS (COMPTES ET LOGS)
# ======================================================
os.makedirs("accounts", exist_ok=True)
os.makedirs("data", exist_ok=True)

def create_account(user, pwd):
    file = f"accounts/{user.lower()}.txt"
    if os.path.exists(file): return False
    with open(file, "w", encoding="utf-8") as f:
        f.write(pwd)
    return True

def login_account(user, pwd):
    file = f"accounts/{user.lower()}.txt"
    if not os.path.exists(file): return False
    with open(file, "r", encoding="utf-8") as f:
        return f.read().strip() == pwd

def sauvegarder_message_local(user, texte, reponse):
    # CRÉATION D'UN SEUL FICHIER PAR DATE (ex: data/08-05-2026.txt)
    date_jour = datetime.now().strftime("%d-%m-%Y")
    chemin_fichier = f"data/{date_jour}.txt"
    horaire = datetime.now().strftime("%H:%M")
    
    with open(chemin_fichier, "a", encoding="utf-8") as f:
        f.write(f"--- UTILISATEUR : {user.upper()} ({horaire}) ---\n")
        f.write(f"LUI : {texte}\n")
        f.write(f"IA  : {reponse}\n")
        f.write("-" * 50 + "\n\n")

# ======================================================
# 🧠 INTELLIGENCE ARTIFICIELLE (FLUIDE)
# ======================================================
def generer_reponse(prompt):
    if not api_key:
        return "⚠️ Erreur : Clé Mistral manquante."

    instructions = {
        "Cool": "Tu es Hartur, un ado cool. Réponds directement, sans listes, tutoie l'utilisateur.",
        "Drôle": "Sois très drôle, fais des blagues et utilise des emojis.",
        "Sérieux": "Réponds de façon brève, précise et professionnelle.",
        "Sarcastique": "Sois ironique et un peu piquant dans tes réponses.",
        "Raisonnement complexe": "Réponds avec intelligence mais reste fluide, pas de formatage rigide."
    }
    
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}"}
    data = {
        "model": "open-mistral-7b",
        "messages": [
            {"role": "system", "content": instructions.get(st.session_state.humeur, "Tu es Hartur.")},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }
    try:
        response = requests.post(url, headers=headers, json=data, timeout=12)
        return response.json()['choices'][0]['message']['content']
    except:
        return "Petit souci technique, on peut reprendre ?"

# ======================================================
# 🏠 NAVIGATION ET BOUTON ADMIN
# ======================================================
col1, col2 = st.columns([9, 1])
with col2:
    if st.button("🔐 Admin"):
        st.session_state.page = "admin"
        st.rerun()

# --- PAGE D'ACCUEIL ---
if st.session_state.page == "home":
    st.title("🤖 Hartur IA")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🔑 Connexion"): st.session_state.page = "login"; st.rerun()
    with c2:
        if st.button("🆕 Créer un compte"): st.session_state.page = "signup"; st.rerun()

# --- PAGE SIGNUP ---
elif st.session_state.page == "signup":
    st.subheader("🆕 Inscription")
    u = st.text_input("Identifiant")
    p = st.text_input("Mot de passe", type="password")
    if st.button("Valider l'inscription"):
        if u and p:
            if create_account(u, p):
                st.success("Compte créé avec succès !")
                st.session_state.page = "login"; st.rerun()
            else: st.error("Ce pseudo est déjà pris.")

# --- PAGE LOGIN ---
elif st.session_state.page == "login":
    st.subheader("🔑 Connexion")
    u = st.text_input("Pseudo")
    p = st.text_input("Pass", type="password")
    if st.button("Se connecter"):
        if login_account(u, p):
            st.session_state.logged_in = True
            st.session_state.username = u
            st.session_state.page = "chat"; st.rerun()
        else: st.error("Identifiants incorrects.")

# --- PAGE CHAT ---
elif st.session_state.page == "chat":
    st.title(f"🤖 Chat avec Hartur")
    st.sidebar.write(f"Utilisateur : **{st.session_state.username}**")
    st.session_state.humeur = st.sidebar.selectbox("Mode de l'IA", ["Cool", "Drôle", "Sérieux", "Sarcastique", "Raisonnement complexe"])
    
    # Affichage de l'historique de la session
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    prompt = st.chat_input("Écris ici...")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        reponse = generer_reponse(prompt)
        
        st.session_state.messages.append({"role": "assistant", "content": reponse})
        with st.chat_message("assistant"): st.markdown(reponse)
        
        # Sauvegarde automatique dans le fichier texte journalier
        sauvegarder_message_local(st.session_state.username, prompt, reponse)

    if st.sidebar.button("Déconnexion"):
        st.session_state.logged_in = False
        st.session_state.messages = []
        st.session_state.page = "home"; st.rerun()

# ======================================================
# 🔐 PANNEAU ADMIN (TOUT SUR UN FICHIER PAR DATE)
# ======================================================
elif st.session_state.page == "admin":
    st.title("🔐 Administration")
    if st.text_input("Mot de passe Admin", type="password") == "babar":
        
        tab1, tab2 = st.tabs(["👤 Comptes Utilisateurs", "💬 Conversations par Jour"])

        with tab1:
            st.subheader("Liste des comptes")
            for f in os.listdir("accounts"):
                if f.endswith(".txt"):
                    with open(f"accounts/{f}", "r", encoding="utf-8") as file:
                        st.write(f"👤 **{f.replace('.txt', '')}** | MDP: `{file.read()}`")

        with tab2:
            st.subheader("Fichiers de logs journaliers")
            # On liste les fichiers .txt dans data/
            fichiers = sorted([f for f in os.listdir("data") if f.endswith(".txt")], reverse=True)
            
            if not fichiers:
                st.info("Aucune conversation enregistrée.")
            else:
                for f in fichiers:
                    # Chaque fichier (ex: 08-05-2026.txt) devient un menu déroulant
                    with st.expander(f"📅 Archive : {f.replace('.txt', '')}"):
                        with open(f"data/{f}", "r", encoding="utf-8") as file:
                            st.text(file.read())

    if st.button("⬅ Retour"):
        st.session_state.page = "home"; st.rerun()
