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
# 🎨 STYLE MODERNE
# ======================================================
st.markdown("""
<style>

/* Fond principal */
.stApp {
    background-color: #0f1117;
    color: white;
}

/* Bulles chat */
.stChatMessage {
    border-radius: 18px;
    padding: 12px;
    margin-bottom: 10px;
    border: none;
}

/* Messages utilisateur */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    background: linear-gradient(135deg, #2563eb, #1d4ed8);
    border-radius: 20px;
    padding: 15px;
    margin-left: 80px;
    box-shadow: 0 4px 15px rgba(37,99,235,0.4);
}

/* Messages IA */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
    background: linear-gradient(135deg, #1f2937, #111827);
    border-radius: 20px;
    padding: 15px;
    margin-right: 80px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.4);
}

/* Input chat */
.stChatInputContainer {
    background-color: #111827;
    border-radius: 20px;
    padding: 10px;
}

/* Boutons */
.stButton>button {
    border-radius: 15px;
    background: linear-gradient(135deg, #2563eb, #7c3aed);
    color: white;
    border: none;
    font-weight: bold;
    transition: 0.3s;
}

.stButton>button:hover {
    transform: scale(1.03);
}

/* Inputs */
.stTextInput input {
    border-radius: 15px;
}

/* Onglets */
.stTabs [data-baseweb="tab"] {
    font-size: 18px;
    border-radius: 12px;
    padding: 10px 20px;
}

/* Titre */
.big-title {
    font-size: 55px;
    font-weight: bold;
    text-align: center;
    background: linear-gradient(90deg, #60a5fa, #a78bfa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 20px;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #111827;
}

/* Scrollbar */
::-webkit-scrollbar {
    width: 10px;
}

::-webkit-scrollbar-thumb {
    background: #374151;
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)

# ======================================================
# 💾 SESSION
# ======================================================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "nom" not in st.session_state:
    st.session_state.nom = None

if "admin_auth" not in st.session_state:
    st.session_state.admin_auth = False

if "memory" not in st.session_state:
    st.session_state.memory = {}

# ======================================================
# 🤖 API
# ======================================================
try:
    api_key = st.secrets["MISTRAL_KEY"]
except Exception:
    api_key = None

# ======================================================
# 📂 SAVE
# ======================================================
def save_message(nom, session_id, user, ia):

    date_folder = datetime.utcnow().strftime("%Y-%m-%d")

    os.makedirs(f"data/{date_folder}", exist_ok=True)

    filename = f"data/{date_folder}/{nom.lower().replace(' ', '_')}.txt"

    date_now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    with open(filename, "a", encoding="utf-8") as f:

        f.write(f"\n📅 {date_now} | SESSION: {session_id}\n")
        f.write(f"[USER] {user}\n")
        f.write(f"[IA] {ia}\n")
        f.write("-" * 40 + "\n")

# ======================================================
# 📂 LOAD
# ======================================================
def load_old_messages(nom):

    messages = []

    if not os.path.exists("data"):
        return messages

    nom_fichier = nom.lower().replace(" ", "_") + ".txt"

    for date_folder in sorted(os.listdir("data")):

        folder_path = f"data/{date_folder}"

        if os.path.isdir(folder_path):

            file_path = f"{folder_path}/{nom_fichier}"

            if os.path.exists(file_path):

                with open(file_path, "r", encoding="utf-8") as f:

                    lines = f.readlines()

                    for line in lines:

                        line = line.strip()

                        if line.startswith("[USER]"):

                            messages.append({
                                "role": "user",
                                "content": line.replace("[USER] ", "")
                            })

                        elif line.startswith("[IA]"):

                            messages.append({
                                "role": "assistant",
                                "content": line.replace("[IA] ", "")
                            })

    return messages

# ======================================================
# 🎭 ONGLET
# ======================================================
tab1, tab2, tab3 = st.tabs([
    "💬 Chat",
    "⚙️ Personnalisation",
    "🔐 Admin"
])

# ======================================================
# ⚙️ PERSONNALISATION
# ======================================================
with tab2:

    st.title("⚙️ Personnalisation IA")

    humeur = st.selectbox(
        "🎭 Humeur",
        ["Cool", "Drôle", "Gentil", "Sarcastique"]
    )

    style = st.selectbox(
        "🗣️ Style",
        ["Normal", "Familier", "Poli"]
    )

    humour = st.slider(
        "😂 Humour",
        0,
        10,
        5
    )

    gentillesse = st.slider(
        "❤️ Gentillesse",
        0,
        10,
        8
    )

    nom_ia = st.text_input(
        "🤖 Nom de l'IA",
        "Hartur"
    )

    mode_chaos = st.toggle("💀 Mode chaos")

    mode_memoire = st.toggle(
        "🧠 Retenir les discussions",
        value=True
    )

    mode_dark = st.toggle("🌙 Mode nuit")

# ======================================================
# 🤖 IA
# ======================================================
def appeler_mistral(prompt):

    if prompt.lower() == "/clear":
        st.session_state.messages = []
        return "Conversation supprimée 😄"

    if prompt.lower() == "/dice":
        return f"🎲 Résultat : {random.randint(1,6)}"

    if "tu m'aimes" in prompt.lower():
        return "Évidemment 🤖❤️"

    if "qui t'a créé" in prompt.lower():
        return "J'ai été créé par Zacharie Pays 🤖"

    if "mon âge est" in prompt.lower():

        age = prompt.split("est")[-1].strip()

        st.session_state.memory["age"] = age

        return f"Je retiens que tu as {age} ans 😄"

    if "quel âge j'ai" in prompt.lower():

        if "age" in st.session_state.memory:
            return f"Tu as {st.session_state.memory['age']} ans 😄"

        return "Tu ne me l'as jamais dit 👀"

    if not api_key:
        return "Erreur API."

    system_prompt = f"""
Tu es {nom_ia}.

Humeur : {humeur}
Style : {style}
Humour : {humour}/10
Gentillesse : {gentillesse}/10

Tu dois répondre naturellement.
"""

    if mode_chaos:
        system_prompt += """
Tu es imprévisible et chaotique.
"""

    url = "https://api.mistral.ai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    data = {
        "model": "open-mistral-7b",
        "messages": [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    try:

        r = requests.post(
            url,
            headers=headers,
            json=data,
            timeout=20
        )

        return r.json()['choices'][0]['message']['content']

    except Exception:
        return "Petit bug IA 😅"

# ======================================================
# 💬 CHAT
# ======================================================
with tab1:

    st.markdown(
        "<div class='big-title'>🤖 Hartur IA</div>",
        unsafe_allow_html=True
    )

    if st.session_state.nom is None:

        nom = st.text_input("👤 Ton prénom ou pseudo")

        if st.button("🚀 Entrer"):

            if nom.strip():

                st.session_state.nom = nom.strip()

                if mode_memoire:
                    st.session_state.messages = load_old_messages(
                        st.session_state.nom
                    )

                st.session_state.session_id = str(uuid.uuid4())

                st.rerun()

    else:

        st.success(f"Salut {st.session_state.nom} 😄")

        image = st.file_uploader(
            "📸 Envoyer une image",
            type=["png", "jpg", "jpeg"]
        )

        if image:
            st.image(image)

        for m in st.session_state.messages:

            with st.chat_message(m["role"]):
                st.markdown(m["content"])

        prompt = st.chat_input("💬 Écris ici...")

        if prompt:

            st.session_state.messages.append({
                "role": "user",
                "content": prompt
            })

            with st.chat_message("user"):
                st.markdown(prompt)

            reponse = appeler_mistral(prompt)

            st.session_state.messages.append({
                "role": "assistant",
                "content": reponse
            })

            with st.chat_message("assistant"):
                st.markdown(reponse)

            save_message(
                st.session_state.nom,
                st.session_state.session_id,
                prompt,
                reponse
            )

# ======================================================
# 🔐 ADMIN
# ======================================================
with tab3:

    st.title("🔐 Admin")

    if not st.session_state.admin_auth:

        pwd = st.text_input(
            "Mot de passe",
            type="password"
        )

        if st.button("Connexion Admin"):

            if pwd == "babar":

                st.session_state.admin_auth = True
                st.rerun()

            else:
                st.error("Mot de passe incorrect")

    else:

        st.success("Connecté 🔓")

        os.makedirs("data", exist_ok=True)

        dates = sorted(os.listdir("data"), reverse=True)

        total_users = 0

        for date in dates:

            date_path = f"data/{date}"

            if os.path.isdir(date_path):

                with st.expander(f"📅 {date}"):

                    files = os.listdir(date_path)

                    total_users += len(files)

                    for file in files:

                        if file.endswith(".txt"):

                            name = file.replace(
                                ".txt",
                                ""
                            ).replace(
                                "_",
                                " "
                            ).title()

                            st.markdown(f"### 👤 {name}")

                            with open(
                                f"{date_path}/{file}",
                                "r",
                                encoding="utf-8"
                            ) as f:

                                st.text(f.read())

        st.info(f"👥 Utilisateurs : {total_users}")

        if st.button("Déconnexion"):

            st.session_state.admin_auth = False
            st.rerun()
