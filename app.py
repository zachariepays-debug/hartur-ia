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
    with open(file, "w") as f: f.write(pwd)
    return True

def login_account(user, pwd):
    file = f"accounts/{user.lower()}.txt"
    if not os.path.exists(file): return False
    with open(file, "r") as f: return f.read() == pwd

def sauvegarder_message_local(user, texte, reponse):
    # Création du dossier à la date du jour (ex: 08-05-2026)
    date_jour = datetime.now().strftime("%d-%m-%Y")
    chemin_dossier = f"data/{date_jour}"
    os.makedirs(chemin_dossier, exist_ok=True)
    
    # Création ou ajout dans le fichier de l'utilisateur
    chemin_fichier = f"{chemin_dossier}/{user.lower()}.txt"
    horaire = datetime.now().strftime("%H:%M")
    
    with open(chemin_fichier, "a", encoding="utf-8") as f:
        f.write(f"[{horaire}] LUI: {texte}\n")
        f.write(f"[{horaire}] IA: {reponse}\n")
        f.write("-" * 30 + "\n")

# ======================================================
# 🧠 IA LOGIQUE
# ======================================================
def generer_reponse(prompt):
    if not api_key: return "Clé API manquante."
    instructions = {
        "Cool": "Tu es Hartur, un ado cool. Réponds directement et tutoie.",
        "Drôle": "Sois drôle, utilise des emojis.",
        "Sérieux": "Réponds de manière concise et pro.",
        "Sarcastique": "Sois ironique.",
        "Raisonnement complexe": "Réponds avec intelligence mais reste fluide."
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
        response = requests.post(url, headers=headers, json=data, timeout=10)
        return response.json()['choices'][0]['message']['content']
    except: return "Bug réseau..."

# ======================================================
# 🏠 NAVIGATION
# ======================================================
col1, col2 = st.columns([9, 1])
with col2:
    if st.button("🔐 Admin"):
        st.session_state.page = "admin"
        st.rerun()

if st.session_state.page == "home":
    st.title("🤖 Hartur IA")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🔑 Connexion"): st.session_state.page = "login"; st.rerun()
    with c2:
        if st.button("🆕 Créer compte"): st.session_state.page = "signup"; st.rerun()

elif st.session_state.page == "signup":
    u = st.text_input("Identifiant")
    p = st.text_input("Mot de passe", type="password")
    if st.button("Créer"):
        if create_account(u, p): st.session_state.page = "login"; st.rerun()
        else: st.error("Déjà pris.")
    if st.button("Retour"): st.session_state.page = "home"; st.rerun()

elif st.session_state.page == "login":
    u = st.text_input("Identifiant")
    p = st.text_input("Mot de passe", type="password")
    if st.button("Entrer"):
        if login_account(u, p):
            st.session_state.logged_in = True
            st.session_state.username = u
            st.session_state.page = "chat"
            st.rerun()
        else: st.error("Erreur login.")
    if st.button("Retour"): st.session_state.page = "home"; st.rerun()

# ======================================================
# 💬 CHAT (Sauvegarde dans FICHIER TEXTE)
# ======================================================
elif st.session_state.page == "chat":
    st.title(f"🤖 Hartur")
    st.sidebar.selectbox("Humeur", ["Cool", "Drôle", "Sérieux", "Sarcastique"], key="humeur")
    
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    prompt = st.chat_input("Écris ici...")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        reponse = generer_reponse(prompt)
        st.session_state.messages.append({"role": "assistant", "content": reponse})
        with st.chat_message("assistant"): st.markdown(reponse)

        # 💾 SAUVEGARDE LOCALE DANS LE FICHIER TEXTE
        sauvegarder_message_local(st.session_state.username, prompt, reponse)

# ======================================================
# 🔐 ADMIN (Dossiers par DATE et fichiers TEXTE)
# ======================================================
elif st.session_state.page == "admin":
    st.title("🔐 Panneau Admin Local")
    if st.text_input("Mot de passe maître", type="password") == "babar":
        
        tab1, tab2 = st.tabs(["👤 Comptes", "💬 Conversations (Fichiers)"])

        with tab1:
            for f in os.listdir("accounts"):
                with open(f"accounts/{f}", "r") as file:
                    st.write(f"👤 **{f.replace('.txt', '')}** | MDP: `{file.read()}`")

        with tab2:
            st.subheader("Archives par date")
            # Lister les dossiers de dates dans /data
            dates = sorted(os.listdir("data"), reverse=True)
            for d in dates:
                if os.path.isdir(f"data/{d}"):
                    with st.expander(f"📅 Date : {d}"):
                        utilisateurs = os.listdir(f"data/{d}")
                        for user_file in utilisateurs:
                            st.markdown(f"**👤 Utilisateur : {user_file.replace('.txt', '')}**")
                            with open(f"data/{d}/{user_file}", "r", encoding="utf-8") as f:
                                st.text(f.read())
                            st.divider()

    if st.button("⬅ Retour"):
        st.session_state.page = "home"
        st.rerun()
