import streamlit as st
import os
import uuid

# ======================================================
# ⚙️ CONFIG
# ======================================================
st.set_page_config(
    page_title="Hartur IA",
    page_icon="🤖",
    layout="wide"
)

# ======================================================
# 💾 SESSION
# ======================================================
if "page" not in st.session_state:
    st.session_state.page = "home"  # home / login / signup / chat

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = None

if "admin_mode" not in st.session_state:
    st.session_state.admin_mode = False

if "admin_popup" not in st.session_state:
    st.session_state.admin_popup = False

if "messages" not in st.session_state:
    st.session_state.messages = []

# ======================================================
# 📁 USERS FILES
# ======================================================
os.makedirs("accounts", exist_ok=True)

# ======================================================
# 👤 CREATE ACCOUNT
# ======================================================
def create_account(user, pwd):

    file = f"accounts/{user.lower()}.txt"

    if os.path.exists(file):
        return False

    with open(file, "w") as f:
        f.write(pwd)

    return True

# ======================================================
# 🔑 LOGIN
# ======================================================
def login_account(user, pwd):

    file = f"accounts/{user.lower()}.txt"

    if not os.path.exists(file):
        return False

    with open(file, "r") as f:
        return f.read() == pwd

# ======================================================
# 🔐 BOUTON ADMIN
# ======================================================
col1, col2 = st.columns([9, 1])

with col2:
    if st.button("🔐"):
        st.session_state.admin_popup = True

# ======================================================
# 🔐 POPUP ADMIN
# ======================================================
if st.session_state.admin_popup:

    st.warning("Mode Admin")

    mdp = st.text_input("Mot de passe", type="password")

    c1, c2 = st.columns(2)

    with c1:
        if st.button("Valider"):

            if mdp == "babar":
                st.session_state.admin_mode = True
                st.session_state.admin_popup = False
                st.rerun()

    with c2:
        if st.button("Annuler"):
            st.session_state.admin_popup = False
            st.rerun()

    st.stop()

# ======================================================
# 🏠 PAGE D'ACCUEIL (DESCRIPTION IA)
# ======================================================
if st.session_state.page == "home":

    st.title("🤖 Hartur IA")

    st.info("""
Bienvenue sur Hartur IA 👋

✔ Une IA intelligente  
✔ Chat personnalisé  
✔ Comptes utilisateurs  
✔ Mémoire des conversations  

👉 Choisis une option ci-dessous
""")

    c1, c2 = st.columns(2)

    with c1:
        if st.button("🔑 Se connecter"):
            st.session_state.page = "login"
            st.rerun()

    with c2:
        if st.button("🆕 Créer un compte"):
            st.session_state.page = "signup"
            st.rerun()

    st.stop()

# ======================================================
# 🆕 CREER COMPTE
# ======================================================
if st.session_state.page == "signup":

    st.subheader("🆕 Créer un compte")

    user = st.text_input("Identifiant")
    pwd = st.text_input("Mot de passe", type="password")

    c1, c2 = st.columns(2)

    with c1:
        if st.button("Créer"):

            if create_account(user, pwd):

                st.success("Compte créé 😄")
                st.session_state.page = "login"
                st.rerun()

            else:
                st.error("Identifiant déjà utilisé")

    with c2:
        if st.button("Retour"):
            st.session_state.page = "home"
            st.rerun()

    st.stop()

# ======================================================
# 🔑 LOGIN PAGE
# ======================================================
if st.session_state.page == "login":

    st.subheader("🔑 Connexion")

    user = st.text_input("Identifiant")
    pwd = st.text_input("Mot de passe", type="password")

    c1, c2 = st.columns(2)

    with c1:
        if st.button("Connexion"):

            if login_account(user, pwd):

                st.session_state.logged_in = True
                st.session_state.username = user
                st.session_state.page = "chat"
                st.rerun()

            else:
                st.error("Identifiants incorrects")

    with c2:
        if st.button("Retour"):
            st.session_state.page = "home"
            st.rerun()

    st.stop()

# ======================================================
# 💬 CHAT PAGE
# ======================================================
if st.session_state.page == "chat" and st.session_state.logged_in:

    st.title("🤖 Hartur IA")

    st.sidebar.success(f"👤 {st.session_state.username}")

    if st.sidebar.button("Déconnexion"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.page = "home"
        st.rerun()

    # ADMIN MODE
    if st.session_state.admin_mode:
        st.subheader("🔐 ADMIN PANEL")
        st.write("Comptes + stats ici")

    # CHAT
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    prompt = st.chat_input("Écris ici...")

    if prompt:

        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })

        reponse = "IA réponse (à connecter)"

        st.session_state.messages.append({
            "role": "assistant",
            "content": reponse
        })

        st.rerun()
