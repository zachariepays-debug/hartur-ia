import streamlit as st
import os
import json
from datetime import datetime

# ======================================================
# ⚙️ CONFIG
# ======================================================
st.set_page_config(
    page_title="Hartur IA",
    page_icon="🤖",
    layout="wide"
)

# ======================================================
# 💾 SESSION STATE
# ======================================================
if "page" not in st.session_state:
    st.session_state.page = "home"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "nom_ia" not in st.session_state:
    st.session_state.nom_ia = "Hartur"

if "humeur" not in st.session_state:
    st.session_state.humeur = "Cool"

if "selected_user" not in st.session_state:
    st.session_state.selected_user = None

# ======================================================
# 📁 DATA FOLDERS
# ======================================================
os.makedirs("accounts", exist_ok=True)
os.makedirs("data", exist_ok=True)

def save_chat(user):
    """Sauvegarde chat utilisateur"""
    if not user:
        return

    today = datetime.now().strftime("%Y-%m-%d")
    folder = f"data/{today}"
    os.makedirs(folder, exist_ok=True)

    file_path = f"{folder}/{user}.json"

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(st.session_state.messages, f, ensure_ascii=False, indent=2)

def load_chat(user):
    today = datetime.now().strftime("%Y-%m-%d")
    file_path = f"data/{today}/{user}.json"

    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# ======================================================
# 🔐 USERS
# ======================================================
def create_account(user, pwd):
    file = f"accounts/{user.lower()}.txt"
    if os.path.exists(file):
        return False
    with open(file, "w") as f:
        f.write(pwd)
    return True

def login_account(user, pwd):
    file = f"accounts/{user.lower()}.txt"
    if not os.path.exists(file):
        return False
    with open(file, "r") as f:
        return f.read() == pwd

# ======================================================
# 🧠 IA
# ======================================================
def generer_reponse(prompt):

    mode = st.session_state.humeur

    if mode == "Raisonnement complexe":
        return f"""🧠 Analyse avancée :

Question : {prompt}

1. Compréhension
2. Décomposition logique
3. Analyse
4. Conclusion

👉 Réponse :
Je traite cela de façon structurée et approfondie.
"""

    if mode == "Drôle":
        return f"😄 Haha ! {prompt} (ça m’a fait sourire)"

    if mode == "Sérieux":
        return f"Réponse structurée : {prompt}"

    if mode == "Sarcastique":
        return f"🤨 Oh vraiment ? {prompt}... intéressant."

    return f"{st.session_state.nom_ia} : {prompt}"

# ======================================================
# 🏠 HOME
# ======================================================
if st.session_state.page == "home":

    st.title("🤖 Hartur IA")

    c1, c2 = st.columns(2)

    with c1:
        if st.button("🔑 Connexion"):
            st.session_state.page = "login"
            st.rerun()

    with c2:
        if st.button("🆕 Créer compte"):
            st.session_state.page = "signup"
            st.rerun()

    st.stop()

# ======================================================
# 🆕 SIGNUP
# ======================================================
if st.session_state.page == "signup":

    st.subheader("Créer compte")

    u = st.text_input("Identifiant")
    p = st.text_input("Mot de passe", type="password")

    if st.button("Créer"):
        if create_account(u, p):
            st.success("Compte créé")
            st.session_state.page = "login"
            st.rerun()
        else:
            st.error("Compte déjà existant")

    st.stop()

# ======================================================
# 🔑 LOGIN
# ======================================================
if st.session_state.page == "login":

    st.subheader("Connexion")

    u = st.text_input("Identifiant")
    p = st.text_input("Mot de passe", type="password")

    if st.button("Connexion"):

        if login_account(u, p):

            st.session_state.logged_in = True
            st.session_state.username = u
            st.session_state.messages = load_chat(u)
            st.session_state.page = "chat"
            st.rerun()

        else:
            st.error("Erreur login")

    st.stop()

# ======================================================
# 💬 CHAT
# ======================================================
if st.session_state.page == "chat" and st.session_state.logged_in:

    st.title(f"🤖 {st.session_state.nom_ia}")

    st.sidebar.success(f"👤 {st.session_state.username}")

    st.session_state.humeur = st.sidebar.selectbox(
        "Humeur IA",
        ["Cool", "Drôle", "Sérieux", "Sarcastique", "Raisonnement complexe"]
    )

    # AFFICHAGE CHAT
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    prompt = st.chat_input("Écris ici...")

    if prompt:

        # USER MESSAGE
        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })

        # IA RESPONSE
        reponse = generer_reponse(prompt)

        st.session_state.messages.append({
            "role": "assistant",
            "content": reponse
        })

        # SAVE CHAT
        save_chat(st.session_state.username)

        st.rerun()

    if st.sidebar.button("Déconnexion"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.messages = []
        st.session_state.page = "home"
        st.rerun()

# ======================================================
# 🔐 ADMIN
# ======================================================
if st.session_state.page == "admin":

    st.title("🔐 ADMIN PANEL")

    mdp = st.text_input("Mot de passe admin", type="password")

    if mdp != "babar":
        st.warning("Accès refusé")
        st.stop()

    st.success("Admin activé")

    if st.button("⬅ Retour"):
        st.session_state.page = "home"
        st.rerun()
