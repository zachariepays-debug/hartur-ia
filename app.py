import streamlit as st
import os
import requests
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
# 📁 GESTION DES FICHIERS (Comptes et Logs)
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

def sauvegarder_message_local(user, texte, reponse):
    # 1. Dossier Date (ex: data/08-05-2026)
    date_jour = datetime.now().strftime("%d-%m-%Y")
    chemin_date = f"data/{date_jour}"
    
    # 2. Dossier Utilisateur dans la date (ex: data/08-05-2026/pseudo)
    chemin_user = f"{chemin_date}/{user.lower()}"
    os.makedirs(chemin_user, exist_ok=True)
    
    # 3. Fichier de conversation
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
        "Cool": "Tu es Hartur, un ado cool. Réponds directement et tutoie.",
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
    except: return "Erreur de connexion..."

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
            st.session_state.page = "chat"; st.rerun()

elif st.session_state.page == "chat":
    st.title(f"🤖 Chat")
    st.session_state.humeur = st.sidebar.selectbox("Mood", ["Cool", "Drôle", "Sérieux", "Sarcastique", "Raisonnement complexe"])
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])
    prompt = st.chat_input("Écris ici...")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        reponse = generer_reponse(prompt)
        st.session_state.messages.append({"role": "assistant", "content": reponse})
        with st.chat_message("assistant"): st.markdown(reponse)
        sauvegarder_message_local(st.session_state.username, prompt, reponse)

# ======================================================
# 🔐 ADMIN (Dossier Date -> Dossier User -> Fichier)
# ======================================================
elif st.session_state.page == "admin":
    st.title("🔐 Admin Panel")
    if st.text_input("Mot de passe", type="password") == "babar":
        
        tab1, tab2 = st.tabs(["👤 Comptes", "💬 Conversations"])
        
        with tab1:
            for f in os.listdir("accounts"):
                with open(f"accounts/{f}", "r") as file:
                    st.write(f"👤 `{f.replace('.txt', '')}` | MDP: `{file.read()}`")

        with tab2:
            st.subheader("Archives des conversations")
            # 1. Lister les dossiers de dates
            dates = sorted([d for d in os.listdir("data") if os.path.isdir(f"data/{d}")], reverse=True)
            
            for d in dates:
                with st.expander(f"📅 Dossier Date : {d}"):
                    # 2. Lister les dossiers utilisateurs dans cette date
                    chemin_date = f"data/{d}"
                    users_today = [u for u in os.listdir(chemin_date) if os.path.isdir(f"{chemin_date}/{u}")]
                    
                    if not users_today:
                        st.write("Aucun utilisateur ce jour-là.")
                    
                    for u in users_today:
                        # 3. Bouton ou sous-expander pour voir l'utilisateur
                        st.markdown(f"---")
                        st.write(f"📂 **Dossier Utilisateur : {u.upper()}**")
                        chemin_conv = f"{chemin_date}/{u}/conversation.txt"
                        
                        if os.path.exists(chemin_conv):
                            with open(chemin_conv, "r", encoding="utf-8") as f:
                                st.text(f.read())
                        else:
                            st.warning("Fichier de conversation introuvable.")

    if st.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()
