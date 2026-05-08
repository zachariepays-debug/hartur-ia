import streamlit as st
import os

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
    st.session_state.page = "home"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "admin_mode" not in st.session_state:
    st.session_state.admin_mode = False

if "admin_popup" not in st.session_state:
    st.session_state.admin_popup = False

# 🎭 PERSONNALISATION IA
if "humeur" not in st.session_state:
    st.session_state.humeur = "Cool"

if "style" not in st.session_state:
    st.session_state.style = "Normal"

if "nom_ia" not in st.session_state:
    st.session_state.nom_ia = "Hartur"

# ======================================================
# 📁 USERS
# ======================================================
os.makedirs("accounts", exist_ok=True)

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
# 🔐 BOUTON ADMIN (EN HAUT DROITE)
# ======================================================
col1, col2 = st.columns([9, 1])

with col2:
    if st.button("🔐 Admin"):
        st.session_state.admin_popup = True

# ======================================================
# 🔐 POPUP ADMIN
# ======================================================
if st.session_state.admin_popup:

    st.warning("Accès Admin")

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
# 🏠 HOME
# ======================================================
if st.session_state.page == "home":

    st.title("🤖 Hartur IA")

    st.info("""
✔ IA intelligente personnalisable  
✔ Comptes utilisateurs  
✔ Chat avec mémoire  
✔ Mode admin  
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

    st.subheader("Créer un compte")

    u = st.text_input("Identifiant")
    p = st.text_input("Mot de passe", type="password")

    if st.button("Créer"):

        if create_account(u, p):
            st.success("Compte créé")
            st.session_state.page = "login"
            st.rerun()
        else:
            st.error("Identifiant déjà utilisé")

    if st.button("Retour"):
        st.session_state.page = "home"
        st.rerun()

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
            st.error("Erreur login")

    if st.button("Retour"):
        st.session_state.page = "home"
        st.rerun()

    st.stop()

# ======================================================
# 💬 CHAT PAGE
# ======================================================
if st.session_state.page == "chat" and st.session_state.logged_in:

    st.title(f"🤖 {st.session_state.nom_ia}")

    st.sidebar.success(f"👤 {st.session_state.username}")

    if st.sidebar.button("Déconnexion"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.page = "home"
        st.rerun()

    # ==================================================
    # ⚙️ PERSONNALISATION IA (VISIBLE UTILISATEUR)
    # ==================================================
    st.sidebar.subheader("⚙️ Personnalisation IA")

    st.session_state.humeur = st.sidebar.selectbox(
        "Humeur",
        ["Cool", "Drôle", "Gentil", "Sarcastique"]
    )

    st.session_state.style = st.sidebar.selectbox(
        "Style",
        ["Normal", "Familier", "Poli"]
    )

    st.session_state.nom_ia = st.sidebar.text_input(
        "Nom IA",
        st.session_state.nom_ia
    )

    # ==================================================
    # 🔐 ADMIN PANEL
    # ==================================================
    if st.session_state.admin_mode:
        st.subheader("🔐 ADMIN MODE")
        st.write("✔ Comptes")
        st.write("✔ Conversations")
        st.write("✔ Stats")

    # ==================================================
    # 💬 CHAT
    # ==================================================
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    prompt = st.chat_input("Écris ici...")

    if prompt:

        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })

        # 🤖 réponse simple (à connecter IA après)
        reponse = f"({st.session_state.nom_ia}) répond en mode {st.session_state.humeur}"

        st.session_state.messages.append({
            "role": "assistant",
            "content": reponse
        })

        st.rerun()
