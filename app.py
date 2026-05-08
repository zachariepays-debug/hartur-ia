import streamlit as st
import os
import requests
from datetime import datetime

# ======================================================
# ⚙️ CONFIGURATION DU SITE
# ======================================================
st.set_page_config(page_title="Hartur IA", page_icon="🤖", layout="wide")

# Récupération de ta clé Mistral dans les Secrets de Streamlit
api_key = st.secrets.get("MISTRAL_KEY")

# ======================================================
# 💾 INITIALISATION DES VARIABLES (SESSION STATE)
# ======================================================
if "page" not in st.session_state: st.session_state.page = "home"
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "username" not in st.session_state: st.session_state.username = None
if "messages" not in st.session_state: st.session_state.messages = []
if "humeur" not in st.session_state: st.session_state.humeur = "Cool"

# ======================================================
# 📁 SYSTÈME DE FICHIERS (COMPTES & LOGS)
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
    # Dossier par date : data/08-05-2026/
    date_jour = datetime.now().strftime("%d-%m-%Y")
    chemin_dossier = f"data/{date_jour}"
    os.makedirs(chemin_dossier, exist_ok=True)
    
    # Fichier par utilisateur : data/08-05-2026/pseudo.txt
    chemin_fichier = f"{chemin_dossier}/{user.lower()}.txt"
    horaire = datetime.now().strftime("%H:%M")
    
    with open(chemin_fichier, "a", encoding="utf-8") as f:
        f.write(f"[{horaire}] LUI: {texte}\n")
        f.write(f"[{horaire}] IA: {reponse}\n")
        f.write("-" * 40 + "\n")

# ======================================================
# 🧠 INTELLIGENCE ARTIFICIELLE (MISTRAL)
# ======================================================
def generer_reponse(prompt):
    if not api_key:
        return "⚠️ Erreur : Clé Mistral non configurée dans les Secrets."

    instructions = {
        "Cool": "Tu es Hartur, un ado cool. Réponds directement, sans listes, sois bref et tutoie.",
        "Drôle": "Réponds avec beaucoup d'humour et des emojis, sois très vivant.",
        "Sérieux": "Réponds de manière pro et très courte.",
        "Sarcastique": "Sois moqueur et ironique dans tes réponses.",
        "Raisonnement complexe": "Réponds intelligemment mais reste fluide, pas de format scolaire."
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
        return "Désolé, petit souci technique. Recommence ?"

# ======================================================
# 🏠 NAVIGATION ET BOUTON ADMIN
# ======================================================
col1, col2 = st.columns([9, 1])
with col2:
    if st.button("🔐 Admin"):
        st.session_state.page = "admin"
        st.rerun()

# --- ACCUEIL ---
if st.session_state.page == "home":
    st.title("🤖 Hartur IA")
    st.write("Bienvenue sur ton IA perso.")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🔑 Connexion"): st.session_state.page = "login"; st.rerun()
    with c2:
        if st.button("🆕 Créer un compte"): st.session_state.page = "signup"; st.rerun()

# --- CRÉATION DE COMPTE ---
elif st.session_state.page == "signup":
    st.subheader("🆕 Création de compte")
    u = st.text_input("Choisis un pseudo")
    p = st.text_input("Choisis un mot de passe", type="password")
    if st.button("S'enregistrer"):
        if u and p:
            if create_account(u, p):
                st.success("Compte créé ! Tu peux te connecter.")
                st.session_state.page = "login"; st.rerun()
            else: st.error("Ce pseudo existe déjà.")
    if st.button("Retour"): st.session_state.page = "home"; st.rerun()

# --- CONNEXION ---
elif st.session_state.page == "login":
    st.subheader("🔑 Connexion")
    u = st.text_input("Pseudo")
    p = st.text_input("Mot de passe", type="password")
    if st.button("Entrer"):
        if login_account(u, p):
            st.session_state.logged_in = True
            st.session_state.username = u
            st.session_state.page = "chat"; st.rerun()
        else: st.error("Pseudo ou mot de passe faux.")
    if st.button("Retour"): st.session_state.page = "home"; st.rerun()

# --- ZONE DE CHAT ---
elif st.session_state.page == "chat":
    st.title(f"🤖 Discussion avec Hartur")
    st.sidebar.write(f"Connecté en tant que : **{st.session_state.username}**")
    st.session_state.humeur = st.sidebar.selectbox("Humeur de Hartur", ["Cool", "Drôle", "Sérieux", "Sarcastique", "Raisonnement complexe"])
    
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    prompt = st.chat_input("Dis quelque chose...")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        reponse = generer_reponse(prompt)
        st.session_state.messages.append({"role": "assistant", "content": reponse})
        with st.chat_message("assistant"): st.markdown(reponse)
        
        # Sauvegarde dans le fichier texte local
        sauvegarder_message_local(st.session_state.username, prompt, reponse)

    if st.sidebar.button("Déconnexion"):
        st.session_state.logged_in = False
        st.session_state.messages = []
        st.session_state.page = "home"; st.rerun()

# ======================================================
# 🔐 PANNEAU ADMIN (COMPTES + CONVERSATIONS)
# ======================================================
elif st.session_state.page == "admin":
    st.title("🔐 Administration")
    if st.text_input("Mot de passe Admin", type="password") == "babar":
        st.success("Accès Maître autorisé")
        
        t1, t2 = st.tabs(["👤 Liste des Comptes", "💬 Historique des Chats"])

        with t1:
            st.subheader("Identifiants & Mots de passe")
            for f in os.listdir("accounts"):
                if f.endswith(".txt"):
                    with open(f"accounts/{f}", "r", encoding="utf-8") as file:
                        st.write(f"👤 **User :** `{f.replace('.txt', '')}` | 🔑 **MDP :** `{file.read()}`")

        with t2:
            st.subheader("Conversations archivées")
            # Gestion des dates et des fichiers orphelins (teste, san...)
            elements = os.listdir("data")
            dossiers = sorted([e for e in elements if os.path.isdir(f"data/{e}")], reverse=True)
            fichiers_seuls = [e for e in elements if os.path.isfile(f"data/{e}") and e.endswith(".txt")]

            if dossiers:
                for d in dossiers:
                    with st.expander(f"📅 Date : {d}"):
                        for user_txt in os.listdir(f"data/{d}"):
                            st.markdown(f"**👤 Utilisateur : {user_txt.replace('.txt', '')}**")
                            with open(f"data/{d}/{user_txt}", "r", encoding="utf-8") as f:
                                st.text(f.read())
                            st.divider()
            
            if fichiers_seuls:
                st.markdown("### 🗄️ Anciens fichiers (Hors date)")
                for f in fichiers_seuls:
                    with st.expander(f"👤 {f.replace('.txt', '')}"):
                        with open(f"data/{f}", "r", encoding="utf-8") as file:
                            st.text(file.read())

    if st.button("⬅ Quitter Admin"):
        st.session_state.page = "home"; st.rerun()
