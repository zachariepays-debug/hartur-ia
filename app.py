import streamlit as st
import os
import random
import requests

# ======================================================
# ⚙️ CONFIG
# ======================================================
st.set_page_config(
    page_title="Hartur IA",
    page_icon="🤖",
    layout="wide"
)

# ======================================================
# 🔑 API KEY (FIX STREAMLIT SECRETS)
# ======================================================
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

# ======================================================
# 💾 SESSION STATE SAFE INIT
# ======================================================
defaults = {
    "page": "home",
    "logged_in": False,
    "username": None,
    "messages": [],
    "nom_ia": "Hartur",
    "selected_user": None
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ======================================================
# 📁 FOLDERS SAFE
# ======================================================
os.makedirs("accounts", exist_ok=True)
os.makedirs("data", exist_ok=True)

# ======================================================
# 👤 USERS SYSTEM
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
# 🧠 IA (API CORRIGÉE)
# ======================================================
def generer_reponse(prompt):

    prompt = prompt.strip()

    if not prompt:
        return "Dis-moi quelque chose 🙂"

    url = "https://api.openai.com/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {st.secrets['OPENAI_API_KEY']}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content": "Tu es Hartur, une IA naturelle, utile et simple. Tu réponds sans répétitions inutiles."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.7
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=20)

        if response.status_code != 200:
            return f"❌ API Error {response.status_code} : {response.text}"

        return response.json()["choices"][0]["message"]["content"]

    except Exception as e:
        return f"❌ Connexion error : {str(e)}"

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

    st.info("✔ IA ✔ Chat ✔ Comptes ✔ Admin")

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
            st.error("Déjà existant")

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

        response = generer_reponse(prompt)

        st.session_state.messages.append({
            "role": "assistant",
            "content": response
        })

        st.rerun()

    if st.sidebar.button("Déconnexion"):
        st.session_state = {}
        st.rerun()

# ======================================================
# 🔐 ADMIN PANEL SAFE
# ======================================================
if st.session_state.page == "admin":

    st.title("🔐 ADMIN PANEL")

    mdp = st.text_input("Mot de passe", type="password")

    if mdp != "babar":
        st.stop()

    menu = st.radio("Menu", ["Comptes", "Conversations"])

    if menu == "Comptes":

        for f in os.listdir("accounts"):
            st.write("✔", f.replace(".txt", ""))

    if menu == "Conversations":

        if os.path.exists("data"):

            for d in os.listdir("data"):

                path = os.path.join("data", d)

                if not os.path.isdir(path):
                    continue

                st.write("📅", d)

                for f in os.listdir(path):

                    if st.button(f"👤 {f}", key=f"btn_{d}_{f}"):

                        st.session_state.selected_user = f

                    if st.session_state.selected_user == f:

                        with open(os.path.join(path, f), "r") as file:
                            st.text(file.read())

    if st.button("⬅ Retour"):
        st.session_state.page = "home"
        st.rerun()
