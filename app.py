import streamlit as st
import os
import requests
import shutil
from datetime import datetime

# ======================================================
# ⚙️ CONFIGURATION
# ======================================================
st.set_page_config(page_title="Hartur IA", page_icon="🤖", layout="wide")
api_key = st.secrets.get("MISTRAL_KEY")

# ======================================================
# 💾 SESSION STATE
# ======================================================
if "page" not in st.session_state: st.session_state.page = "home"
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "username" not in st.session_state: st.session_state.username = None
if "messages" not in st.session_state: st.session_state.messages = []
if "humeur" not in st.session_state: st.session_state.humeur = "Cool"

# ======================================================
# 📁 GESTION DES FICHIERS ET HISTORIQUE
# ======================================================
os.makedirs("accounts", exist_ok=True)
os.makedirs("data", exist_ok=True)

def create_account(user, pwd):
    file = f"accounts/{user.lower()}.txt"
    if os.path.exists(file): return False
    with open(file, "w", encoding="utf-8") as f: f.write(pwd)
    return True

def login_account(user, pwd):
    file = f"accounts/{user.lower()}.txt"
    if not os.path.exists(file): return False
    with open(file, "r", encoding="utf-8") as f: return f.read().strip() == pwd

def charger_historique_utilisateur(user):
    """Charge les messages des jours précédents pour l'interface de chat"""
    historique = []
    # On parcourt les dossiers de dates pour trouver les messages de l'utilisateur
    if os.path.exists("data"):
        for date_dir in sorted(os.listdir("data")):
            chemin_conv = f"data/{date_dir}/{user.lower()}/conversation.txt"
            if os.path.exists(chemin_conv):
                with open(chemin_conv, "r", encoding="utf-8") as f:
                    lignes = f.readlines()
                    for ligne in lignes:
                        if "LUI :" in ligne:
                            contenu = ligne.split("LUI :")[1].strip()
                            historique.append({"role": "user", "content": contenu})
                        elif "IA  :" in ligne:
                            contenu = ligne.split("IA  :")[1].strip()
                            historique.append({"role": "assistant", "content": contenu})
    return historique

def sauvegarder_message_local(user, texte, reponse):
    date_jour = datetime.now().strftime("%d-%m-%Y")
    chemin_user = f"data/{date_jour}/{user.lower()}"
    os.makedirs(chemin_user, exist_ok=True)
    
    chemin_fichier = f"{chemin_user}/conversation.txt"
    horaire = datetime.now().strftime("%H:%M")
    
    with open(chemin_fichier, "a", encoding="utf-8") as f:
        f.write(f"[{horaire}] LUI : {texte}\n")
        f.write(f"[{horaire}] IA  : {reponse}\n")
        f.write("-" * 40 + "\n")

# ======================================================
# 🧠 IA LOGIQUE
# ======================================================
def generer_reponse(prompt):
    if not api_key: return "Clé API manquante."
    instructions = {
        "Cool": "Tu es Hartur, un ado cool. Réponds directement, sans listes, tutoie.",
        "Drôle": "Sois drôle, utilise des emojis.",
        "Sérieux": "Réponds de manière concise.",
        "Sarcastique": "Sois ironique.",
        "Raisonnement complexe": "Réponds avec intelligence mais reste fluide."
    }
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}"}
    data = {
        "model": "open-mistral-7b",
        "messages": [{"role": "system", "content": instructions.get(st.session_state.humeur, "Tu es Hartur.")}, {"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    try:
        response = requests.post(url, headers=headers, json=data, timeout=12)
        return response.json()['choices'][0]['message']['content']
    except: return "Erreur réseau..."

# ======================================================
# 🏠 NAVIGATION
# ======================================================
col1, col2 = st.columns([9, 1])
with col2:
    if st.button("🔐 Admin"): st.session_state.page = "admin"; st.rerun()

if st.session_state.page == "home":
    st.title("🤖 Hartur IA")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🔑 Connexion"): st.session_state.page = "login"; st.rerun()
    with c2:
        if st.button("🆕 Créer compte"): st.session_state.page = "signup"; st.rerun()

elif st.session_state.page == "signup":
    u = st.text_input("Pseudo")
    p = st.text_input("Pass", type="password")
    if st.button("Créer"):
        if create_account(u, p): st.session_state.page = "login"; st.rerun()
        else: st.error("Pseudo déjà pris.")

elif st.session_state.page == "login":
    u = st.text_input("Pseudo")
    p = st.text_input("Pass", type="password")
    if st.button("Entrer"):
        if login_account(u, p):
            st.session_state.logged_in = True
            st.session_state.username = u
            # CHARGEMENT DE L'HISTORIQUE ICI
            st.session_state.messages = charger_historique_utilisateur(u)
            st.session_state.page = "chat"; st.rerun()
        else: st.error("Erreur de login.")

elif st.session_state.page == "chat":
    st.title(f"🤖 Chat")
    st.sidebar.write(f"Utilisateur : **{st.session_state.username}**")
    st.session_state.humeur = st.sidebar.selectbox("Mood", ["Cool", "Drôle", "Sérieux", "Sarcastique", "Raisonnement complexe"])
    
    # Affichage de l'historique (anciens + nouveaux messages)
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    prompt = st.chat_input("Dis un truc...")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        reponse = generer_reponse(prompt)
        st.session_state.messages.append({"role": "assistant", "content": reponse})
        with st.chat_message("assistant"): st.markdown(reponse)
        sauvegarder_message_local(st.session_state.username, prompt, reponse)

    if st.sidebar.button("Déconnexion"):
        st.session_state.logged_in = False
        st.session_state.messages = []
        st.session_state.page = "home"; st.rerun()

# ======================================================
# 🔐 ADMIN
# ======================================================
elif st.session_state.page == "admin":
    st.title("🔐 Panneau Admin")
    if st.text_input("Mot de passe", type="password") == "babar":
        tab1, tab2 = st.tabs(["👤 Comptes", "💬 Conversations"])
        with tab1:
            for f in os.listdir("accounts"):
                with open(f"accounts/{f}", "r") as file:
                    st.write(f"👤 `{f.replace('.txt', '')}` | MDP: `{file.read()}`")
        with tab2:
            if st.button("🗑️ Vider l'historique complet"):
                if os.path.exists("data"):
                    shutil.rmtree("data")
                    os.makedirs("data")
                    st.rerun()
            st.divider()
            dates = sorted([d for d in os.listdir("data") if os.path.isdir(f"data/{d}")], reverse=True)
            for d in dates:
                with st.expander(f"📅 Date : {d}"):
                    chemin_date = f"data/{d}"
                    users = [u for u in os.listdir(chemin_date) if os.path.isdir(f"{chemin_date}/{u}")]
                    for u in users:
                        st.markdown(f"**📂 Dossier Utilisateur : {u.upper()}**")
                        chemin_conv = f"{chemin_date}/{u}/conversation.txt"
                        if os.path.exists(chemin_conv):
                            with open(chemin_conv, "r", encoding="utf-8") as f:
                                st.text(f.read())
                        st.divider()
    if st.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()
