import streamlit as st
import os
import time

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

if "current_chat" not in st.session_state:
    st.session_state.current_chat = None

if "nom_ia" not in st.session_state:
    st.session_state.nom_ia = "Hartur"

if "humeur" not in st.session_state:
    st.session_state.humeur = "Cool"

# ======================================================
# 📁 FILE SYSTEM
# ======================================================
os.makedirs("accounts", exist_ok=True)
os.makedirs("data", exist_ok=True)

def user_folder(user):
    path = f"data/{user}"
    os.makedirs(path, exist_ok=True)
    return path

def chat_file(user, chat_id):
    return f"{user_folder(user)}/{chat_id}.txt"

def list_chats(user):
    folder = user_folder(user)
    return [f.replace(".txt", "") for f in os.listdir(folder) if f.endswith(".txt")]

# ======================================================
# 💾 CHAT SAVE / LOAD
# ======================================================
def save_message(user, chat_id, role, content):
    file = chat_file(user, chat_id)
    with open(file, "a", encoding="utf-8") as f:
        f.write(f"{role}:{content}\n")

def load_messages(user, chat_id):
    file = chat_file(user, chat_id)
    if not os.path.exists(file):
        return []

    msgs = []
    with open(file, "r", encoding="utf-8") as f:
        for line in f:
            if ":" in line:
                r, c = line.split(":", 1)
                msgs.append({"role": r, "content": c.strip()})
    return msgs

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
# 🧠 IA RESPONSE
# ======================================================
def generer_reponse(prompt):
    if st.session_state.humeur == "Raisonnement complexe":
        return f"Analyse structurée de : {prompt}\n\nJe réfléchis étape par étape..."
    elif st.session_state.humeur == "Drôle":
        return f"😄 Haha : {prompt}"
    elif st.session_state.humeur == "Sérieux":
        return f"Réponse : {prompt}"
    else:
        return f"{st.session_state.nom_ia} : {prompt}"

# ======================================================
# ✨ STREAMING EFFECT
# ======================================================
def stream_text(text):
    placeholder = st.empty()
    output = ""
    for char in text:
        output += char
        time.sleep(0.01)
        placeholder.markdown(output)
    return output

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

    u = st.text_input("User")
    p = st.text_input("Pass", type="password")

    if st.button("Créer"):
        if create_account(u, p):
            st.success("OK")
            st.session_state.page = "login"
            st.rerun()

    st.stop()

# ======================================================
# 🔑 LOGIN
# ======================================================
if st.session_state.page == "login":

    u = st.text_input("User")
    p = st.text_input("Pass", type="password")

    if st.button("Connexion"):

        if login_account(u, p):

            st.session_state.logged_in = True
            st.session_state.username = u
            st.session_state.page = "chat"

            # 💬 créer chat si aucun
            chats = list_chats(u)
            if not chats:
                st.session_state.current_chat = "chat_1"
            else:
                st.session_state.current_chat = chats[-1]

            st.session_state.messages = load_messages(u, st.session_state.current_chat)

            st.rerun()

    st.stop()

# ======================================================
# 💬 CHAT
# ======================================================
if st.session_state.page == "chat" and st.session_state.logged_in:

    user = st.session_state.username
    chat = st.session_state.current_chat

    # ==================================================
    # 📌 SIDEBAR (HISTORIQUE)
    # ==================================================
    st.sidebar.title("💬 Chats")

    if st.sidebar.button("➕ Nouveau chat"):
        chat_id = f"chat_{int(time.time())}"
        st.session_state.current_chat = chat_id
        st.session_state.messages = []
        st.rerun()

    for c in list_chats(user):
        col1, col2 = st.sidebar.columns([8, 2])

        with col1:
            if st.button(f"🧠 {c}"):
                st.session_state.current_chat = c
                st.session_state.messages = load_messages(user, c)
                st.rerun()

        with col2:
            if st.button("🗑", key=f"del_{c}"):
                os.remove(chat_file(user, c))
                st.rerun()

    # ==================================================
    # 💬 CHAT UI
    # ==================================================
    st.title(f"🤖 {st.session_state.nom_ia}")

    st.session_state.humeur = st.selectbox(
        "Humeur IA",
        ["Cool", "Drôle", "Sérieux", "Raisonnement complexe"]
    )

    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    prompt = st.chat_input("Écris ici...")

    if prompt:

        # user
        st.session_state.messages.append({"role": "user", "content": prompt})
        save_message(user, chat, "user", prompt)

        # IA
        rep = generer_reponse(prompt)

        with st.chat_message("assistant"):
            final_text = stream_text(rep)

        st.session_state.messages.append({"role": "assistant", "content": final_text})
        save_message(user, chat, "assistant", final_text)

        st.rerun()
