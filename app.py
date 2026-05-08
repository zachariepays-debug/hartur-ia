import streamlit as st
import os
import google.generativeai as genai

# ======================================================
# ⚙️ CONFIG
# ======================================================
st.set_page_config(
    page_title="Hartur IA",
    page_icon="🤖",
    layout="wide"
)

# ======================================================
# 🧠 IA (GEMINI CONFIG)
# ======================================================
genai.configure(api_key="TON_API_KEY_ICI")
model = genai.GenerativeModel("gemini-1.5-flash")

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
# 🔐 ADMIN
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

    st.info("✔ IA connectée ✔ Comptes ✔ Chat ✔ Admin")

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
# 🧠 IA RÉELLE (FIX)
# ======================================================
def generer_reponse(prompt):

    if prompt is None or prompt.strip() == "":
        return "⚠️ Message vide"

    try:
        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        return f"⚠️ Erreur IA : {e}"

# ======================================================
# 💬 CHAT
# ======================================================
if st.session_state.page == "chat" and st.session_state.logged_in:

    st.title(f"🤖 {st.session_state.nom_ia}")

    st.sidebar.success(f"👤 {st.session_state.username}")

    st.sidebar.subheader("🎭 IA Settings")

    st.session_state.humeur = st.sidebar.selectbox(
        "Humeur IA",
        ["Cool", "Drôle", "Sérieux", "Sarcastique", "Raisonnement complexe"]
    )

    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    prompt = st.chat_input("Écris ici...")

    if prompt and prompt.strip() != "":

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
# 🔐 ADMIN (inchangé)
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

        for d in os.listdir("data"):

            st.write("📅", d)

            for f in os.listdir(f"data/{d}"):

                if st.button(f"👤 {f.replace('.txt','')}"):
                    st.session_state.selected_user = f

                if st.session_state.selected_user == f:

                    with open(f"data/{d}/{f}", "r") as file:
                        st.text(file.read())

    if st.button("⬅ Retour app"):
        st.session_state.page = "home"
        st.rerun()
