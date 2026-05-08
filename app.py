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

if "selected_user" not in st.session_state:
    st.session_state.selected_user = None

# ======================================================
# 📁 DATA
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
# 🔐 ADMIN BUTTON
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

    u = st.text_input("Identifiant")
    p = st.text_input("Mot de passe", type="password")

    if st.button("Créer"):
        if create_account(u, p):
            st.success("Compte créé")
            st.session_state.page = "login"
            st.rerun()
        else:
            st.error("Déjà utilisé")

    st.stop()

# ======================================================
# 🔑 LOGIN
# ======================================================
if st.session_state.page == "login":

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

    st.stop()

# ======================================================
# 💬 CHAT
# ======================================================
if st.session_state.page == "chat" and st.session_state.logged_in:

    st.title(f"🤖 {st.session_state.nom_ia}")

    st.sidebar.success(f"👤 {st.session_state.username}")

    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    prompt = st.chat_input("Écris ici...")

    if prompt:

        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })

        reponse = f"{st.session_state.nom_ia} répond 🤖"

        st.session_state.messages.append({
            "role": "assistant",
            "content": reponse
        })

        st.rerun()

    if st.sidebar.button("Déconnexion"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.page = "home"
        st.rerun()

# ======================================================
# 🔐 ADMIN PANEL (AVEC BULLES MODERNES)
# ======================================================
if st.session_state.page == "admin":

    st.title("🔐 ADMIN PANEL")

    mdp = st.text_input("Mot de passe admin", type="password")

    if mdp != "babar":
        st.warning("Accès refusé")
        st.stop()

    st.success("Mode admin activé 🔓")

    menu = st.radio(
        "Navigation",
        ["📁 Sauvegardes", "👤 Comptes", "💬 Conversations"]
    )

    # ==================================================
    # 📁 COMPTES
    # ==================================================
    if menu == "📁 Sauvegardes":

        st.subheader("📁 Comptes")

        for f in os.listdir("accounts"):
            with st.expander(f):
                with open(f"accounts/{f}", "r") as file:
                    st.text(file.read())

    # ==================================================
    # 👤 USERS
    # ==================================================
    elif menu == "👤 Comptes":

        st.subheader("👤 Utilisateurs")

        for f in os.listdir("accounts"):
            st.write("✔", f.replace(".txt", ""))

    # ==================================================
    # 💬 CONVERSATIONS (VERSION BULLES MODERNES)
    # ==================================================
    elif menu == "💬 Conversations":

        st.subheader("💬 Conversations utilisateurs")

        for d in os.listdir("data"):

            st.write("📅", d)

            for f in os.listdir(f"data/{d}"):

                user = f.replace(".txt", "")

                if st.button(f"👤 {user}"):

                    st.session_state.selected_user = f

                # ==================================================
                # 💬 AFFICHAGE CHAT STYLE BULLES
                # ==================================================
                if st.session_state.selected_user == f:

                    st.markdown("### 📜 Conversation")

                    file_path = f"data/{d}/{f}"

                    try:
                        with open(file_path, "r", encoding="utf-8") as file:
                            lines = file.readlines()

                        for line in lines:

                            line = line.strip()

                            if not line:
                                continue

                            # 👤 USER
                            if line.startswith("USER:"):

                                msg = line.replace("USER:", "").strip()

                                st.markdown(
                                    f"""
                                    <div style="
                                        background:#2b2b2b;
                                        color:white;
                                        padding:10px;
                                        border-radius:15px;
                                        margin:6px 0;
                                        width:70%;
                                        margin-left:auto;
                                        text-align:right;
                                    ">
                                    👤 {msg}
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )

                            # 🤖 IA
                            elif line.startswith("IA:"):

                                msg = line.replace("IA:", "").strip()

                                st.markdown(
                                    f"""
                                    <div style="
                                        background:#1f6fff;
                                        color:white;
                                        padding:10px;
                                        border-radius:15px;
                                        margin:6px 0;
                                        width:70%;
                                        margin-right:auto;
                                        text-align:left;
                                    ">
                                    🤖 {msg}
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )

                    except Exception as e:
                        st.error(f"Erreur : {e}")
