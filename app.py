import streamlit as st
import os
import random

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
# 🔐 ADMIN BOUTON
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
✔ IA intelligente  
✔ Comptes utilisateurs  
✔ Chat sauvegardé  
✔ Admin dashboard  
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
            st.error("Déjà utilisé")

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

    st.stop()

# ======================================================
# 🧠 IA RESPONSE
# ======================================================
def generer_reponse(prompt):

    prompt = prompt.strip()

    if not prompt:
        return "🤖 Dis-moi quelque chose 🙂"

    p = prompt.lower()

    if "bonjour" in p:
        return f"🤖 {st.session_state.nom_ia} : Salut 🙂"

    if "ça va" in p:
        return f"🤖 {st.session_state.nom_ia} : Oui ça va 🙂 et toi ?"

    if "qui es tu" in p:
        return f"🤖 {st.session_state.nom_ia} : Je suis ton assistant IA 🙂"

    base = [
        "J’ai bien compris 👍",
        "Ok je vois 🙂",
        "D’accord 👌",
        "Je comprends 👍"
    ]

    return f"🤖 {st.session_state.nom_ia} : {random.choice(base)}"

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

        reponse = generer_reponse(prompt)

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
# 🔐 ADMIN
# ======================================================
if st.session_state.page == "admin":

    st.title("🔐 ADMIN PANEL")

    mdp = st.text_input("Mot de passe admin", type="password")

    if mdp != "babar":
        st.warning("Accès refusé")
        st.stop()

    st.success("Mode admin activé 🔓")

    menu = st.radio(
        "Navigation Admin",
        ["📁 Sauvegardes", "👤 Comptes", "💬 Conversations"]
    )

    if menu == "📁 Sauvegardes":

        for f in os.listdir("accounts"):
            with st.expander(f):
                with open(f"accounts/{f}", "r") as file:
                    st.text(file.read())

    elif menu == "👤 Comptes":

        for f in os.listdir("accounts"):
            st.write("✔", f.replace(".txt", ""))

    elif menu == "💬 Conversations":

        st.subheader("💬 Conversations")

        # 🔥 FIX COMPLET + SAFE
        data_path = "data"

        if os.path.exists(data_path):

            for d in os.listdir(data_path):

                chemin_d = os.path.join(data_path, d)

                # ✔ on ignore si ce n'est pas un dossier
                if not os.path.isdir(chemin_d):
                    continue

                st.write("📅", d)

                for f in os.listdir(chemin_d):

                    user = f.replace(".txt", "")

                    if st.button(f"👤 {user}", key=f"btn_{d}_{f}"):

                        st.session_state.selected_user = f

                    if st.session_state.selected_user == f:

                        st.markdown("### 📜 Conversation")

                        with open(os.path.join(chemin_d, f), "r") as file:
                            st.text(file.read())

    if st.button("⬅ Retour app"):
        st.session_state.page = "home"
        st.rerun()
