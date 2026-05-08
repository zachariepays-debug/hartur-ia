import streamlit as st
import os
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

# 👉 SUPPRESSION des humeurs problématiques (IA stable)
st.session_state.humeur = "Stable"

if "selected_user" not in st.session_state:
    st.session_state.selected_user = None

# ======================================================
# 📁 USERS + DATA
# ======================================================
os.makedirs("accounts", exist_ok=True)
os.makedirs("data", exist_ok=True)


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
# 💾 SAUVEGARDE CONVERSATION
# ======================================================

def save_message(username, role, content):
    date = datetime.now().strftime("%Y-%m-%d")
    folder = f"data/{date}"
    os.makedirs(folder, exist_ok=True)

    file = f"{folder}/{username}.txt"

    with open(file, "a", encoding="utf-8") as f:
        f.write(f"{role.upper()} : {content}\n")


# ======================================================
# 🧠 IA RESPONSE (FIX API READY)
# ======================================================

def generer_reponse(prompt):

    # 🔥 MODE SIMPLE STABLE (sans bug humeur)
    
    # 👉 SI TU VEUX UNE API PLUS TARD : décommente
    # return appel_api_openai(prompt)

    return f"🤖 {st.session_state.nom_ia} : {prompt}"


# ======================================================
# 🔐 NAVIGATION TOP
# ======================================================
col1, col2 = st.columns([9, 1])

with col2:
    if st.button("🔐 Admin"):
        st.session_state.page = "admin"
        st.rerun()


# ======================================================
# 🏠 HOME
# ======================================================
if st.session_state.page == "home":

    st.title("🤖 Hartur IA")

    st.info("""
✔ IA stable (corrigée)
✔ Comptes utilisateurs
✔ Chat sauvegardé
✔ Admin panel
""")

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
            st.session_state.page = "chat"
            st.rerun()

        else:
            st.error("Identifiants incorrects")

    st.stop()


# ======================================================
# 💬 CHAT
# ======================================================
if st.session_state.page == "chat" and st.session_state.logged_in:

    st.title(f"🤖 {st.session_state.nom_ia}")

    st.sidebar.success(f"👤 {st.session_state.username}")

    # 💬 affichage messages
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    prompt = st.chat_input("Écris ici...")

    if prompt:

        st.session_state.messages.append({"role": "user", "content": prompt})
        save_message(st.session_state.username, "user", prompt)

        reponse = generer_reponse(prompt)

        st.session_state.messages.append({"role": "assistant", "content": reponse})
        save_message(st.session_state.username, "assistant", reponse)

        st.rerun()

    if st.sidebar.button("Déconnexion"):
        st.session_state.logged_in = False
        st.session_state.username = None
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

    st.success("Admin actif")

    menu = st.radio("Menu", ["Comptes", "Conversations"])

    if menu == "Comptes":
        for f in os.listdir("accounts"):
            st.write(f.replace(".txt", ""))

    elif menu == "Conversations":

        for d in os.listdir("data"):
            st.write("📅", d)

            for f in os.listdir(f"data/{d}"):
                if st.button(f):
                    with open(f"data/{d}/{f}", "r", encoding="utf-8") as file:
                        st.text(file.read())

    if st.button("⬅ Retour"):
        st.session_state.page = "home"
        st.rerun()
