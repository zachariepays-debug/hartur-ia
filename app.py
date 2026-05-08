import streamlit as st
import requests
from datetime import datetime
import uuid
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
# 🎨 STYLE SIMPLE
# ======================================================
st.markdown("""
<style>
.stApp {
    background-color: #0f1117;
    color: white;
}
.big-title {
    text-align: center;
    font-size: 45px;
    font-weight: bold;
    color: #60a5fa;
}
</style>
""", unsafe_allow_html=True)

# ======================================================
# 💾 SESSION
# ======================================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "show_popup" not in st.session_state:
    st.session_state.show_popup = True

# ======================================================
# 📁 DOSSIERS
# ======================================================
os.makedirs("accounts", exist_ok=True)
os.makedirs("data", exist_ok=True)

# ======================================================
# 🤖 IA API
# ======================================================
try:
    api_key = st.secrets["MISTRAL_KEY"]
except:
    api_key = None

def appeler_mistral(prompt):

    if not api_key:
        return "Clé API manquante."

    url = "https://api.mistral.ai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    data = {
        "model": "open-mistral-7b",
        "messages": [
            {"role": "system", "content": "Tu es Hartur, un assistant IA cool."},
            {"role": "user", "content": prompt}
        ]
    }

    try:
        r = requests.post(url, headers=headers, json=data, timeout=20)
        return r.json()['choices'][0]['message']['content']
    except:
        return "Erreur IA."

# ======================================================
# 👤 COMPTES
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
# 💾 CHAT SAVE
# ======================================================
def save_message(user, session_id, user_msg, ia_msg):

    date_folder = datetime.utcnow().strftime("%Y-%m-%d")
    os.makedirs(f"data/{date_folder}", exist_ok=True)

    file = f"data/{date_folder}/{user.lower()}.txt"

    time = datetime.utcnow().strftime("%H:%M:%S")

    with open(file, "a") as f:
        f.write(f"\n[{time}] SESSION:{session_id}\n")
        f.write(f"USER: {user_msg}\n")
        f.write(f"IA: {ia_msg}\n")
        f.write("-"*40)

# ======================================================
# 📥 LOAD CHAT
# ======================================================
def load_messages(user):

    msgs = []

    if not os.path.exists("data"):
        return msgs

    for d in os.listdir("data"):

        path = f"data/{d}/{user.lower()}.txt"

        if os.path.exists(path):

            with open(path, "r") as f:

                for line in f:

                    if line.startswith("USER:"):
                        msgs.append({"role": "user", "content": line[6:].strip()})

                    if line.startswith("IA:"):
                        msgs.append({"role": "assistant", "content": line[3:].strip()})

    return msgs

# ======================================================
# 🔐 POPUP
# ======================================================
if st.session_state.show_popup:

    st.info("""
🤖 Hartur IA

✔ Chat IA personnalisé  
✔ Comptes utilisateurs  
✔ Historique sauvegardé  
✔ Personnalisation IA  
""")

    if st.button("❌ Fermer"):
        st.session_state.show_popup = False
        st.rerun()

# ======================================================
# 🔐 LOGIN / REGISTER
# ======================================================
if not st.session_state.logged_in:

    st.markdown("<div class='big-title'>Connexion</div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("🔑 Connexion")

        u = st.text_input("Identifiant", key="login_u")
        p = st.text_input("Mot de passe", type="password", key="login_p")

        if st.button("Se connecter"):

            if login_account(u, p):

                st.session_state.logged_in = True
                st.session_state.username = u
                st.session_state.messages = load_messages(u)

                st.rerun()

            else:
                st.error("Erreur login")

    with col2:

        st.subheader("🆕 Créer compte")

        nu = st.text_input("Identifiant", key="new_u")
        np = st.text_input("Mot de passe", type="password", key="new_p")

        if st.button("Créer"):

            if create_account(nu, np):
                st.success("Compte créé")
            else:
                st.error("Déjà existant")

    st.stop()

# ======================================================
# 👤 USER CONNECTÉ
# ======================================================
st.sidebar.success(f"👤 {st.session_state.username}")

if st.sidebar.button("Déconnexion"):
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.messages = []
    st.rerun()

# ======================================================
# 💬 CHAT
# ======================================================
st.markdown("<div class='big-title'>🤖 Hartur IA</div>", unsafe_allow_html=True)

for m in st.session_state.messages:

    with st.chat_message(m["role"]):
        st.markdown(m["content"])

prompt = st.chat_input("Écris ici...")

if prompt:

    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    reponse = appeler_mistral(prompt)

    st.session_state.messages.append({
        "role": "assistant",
        "content": reponse
    })

    save_message(
        st.session_state.username,
        st.session_state.session_id,
        prompt,
        reponse
    )

    st.rerun()

# ======================================================
# 🔐 ADMIN
# ======================================================
st.sidebar.markdown("## 🔐 Admin")

if st.sidebar.text_input("Mot de passe admin", type="password") == "babar":

    st.sidebar.success("Admin OK")

    st.subheader("👤 Comptes")

    for f in os.listdir("accounts"):
        st.write(f)

    st.subheader("💬 Conversations")

    for d in os.listdir("data"):

        st.write("📅", d)

        for f in os.listdir(f"data/{d}"):

            st.write("👤", f)
