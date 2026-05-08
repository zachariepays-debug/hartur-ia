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
# 🧠 IA RESPONSE LOGIC (✔ CORRIGÉ ICI)
# ======================================================
def generer_reponse(prompt):

    # 🧠 Raisonnement complexe
    if st.session_state.humeur == "Raisonnement complexe":

        return f"""
🧠 Analyse :

Question : {prompt}

1️⃣ Compréhension :
Je comprends que tu demandes → {prompt}

2️⃣ Analyse :
Je structure la réponse étape par étape.

3️⃣ Conclusion :

👉 Réponse :
Je vais t’aider de manière claire et détaillée.
"""

    # 😄 Drôle
    if st.session_state.humeur == "Drôle":
        return f"😄 Haha ! Tu viens de dire : '{prompt}' 😂"

    # 🎯 Sérieux
    if st.session_state.humeur == "Sérieux":
        return f"📌 Je comprends ta demande → {prompt}. Voici une réponse claire."

    # 😏 Sarcastique
    if st.session_state.humeur == "Sarcastique":
        return f"🙃 Wow… '{prompt}'… quelle question fascinante."

    # 🌿 Cool
    return f"🤖 {st.session_state.nom_ia} : J’ai bien compris → {prompt}"

# ======================================================
# ✨ STREAM TEXT
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
# 💬 CHAT
# ======================================================
if st.session_state.page == "chat" and st.session_state.logged_in:

    user = st.session_state.username
    chat = st.session_state.current_chat

    col1, col2, col3 = st.columns([7, 2, 1])

    with col1:
        st.title(f"🤖 {st.session_state.nom_ia}")

    with col2:
        if st.button("➕ Nouveau chat"):
            chat_id = f"chat_{int(time.time())}"
            st.session_state.current_chat = chat_id
            st.session_state.messages = []
            st.rerun()

    with col3:
        if st.button("🔐"):
            st.session_state.page = "admin"
            st.rerun()

    st.session_state.humeur = st.selectbox(
        "Humeur IA",
        ["Cool", "Drôle", "Sérieux", "Sarcastique", "Raisonnement complexe"]
    )

    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    prompt = st.chat_input("Écris ici...")

    if prompt:

        st.session_state.messages.append({"role": "user", "content": prompt})
        save_message(user, chat, "user", prompt)

        reponse = generer_reponse(prompt)

        with st.chat_message("assistant"):
            final = stream_text(reponse)

        st.session_state.messages.append({"role": "assistant", "content": final})
        save_message(user, chat, "assistant", final)

        st.rerun()
