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
# 🤖 MISTRAL
# ======================================================
try:
    api_key = st.secrets["MISTRAL_KEY"]
except Exception:
    api_key = None

# ======================================================
# 🎭 HUMEUR IA
# ======================================================
mood = st.sidebar.selectbox(
    "😎 Humeur de Hartur",
    ["Cool", "Drôle", "Gentil", "Sarcastique"]
)

# ======================================================
# 🤖 IA
# ======================================================
def appeler_mistral(prompt):

    # 🔥 COMMANDES RAPIDES
    if prompt.lower() == "/clear":
        st.session_state.messages = []
        return "Conversation réinitialisée 😄"

    if "ça va" in prompt.lower():
        return "Ouiii 😄 et toi ?"

    if "tu m'aimes" in prompt.lower():
        return "Évidemment 🤖❤️"

    if "qui t'a créé" in prompt.lower():
        return "J'ai été créé par Zacharie Pays 🤖"

    # 🧠 MÉMOIRE
    if "mon âge est" in prompt.lower():
        age = prompt.split("est")[-1].strip()
        st.session_state.memory["age"] = age
        return f"Okay 😄 je retiens que tu as {age} ans."

    if "quel âge j'ai" in prompt.lower():
        if "age" in st.session_state.memory:
            return f"Tu as {st.session_state.memory['age']} ans 😄"
        else:
            return "Tu ne me l'as pas encore dit 👀"

    # 🎮 MINI JEU
    if prompt.lower() == "/dice":
        return f"🎲 Tu as obtenu : {random.randint(1,6)}"

    if not api_key:
        return "Erreur : clé API manquante."

    # 🎭 humeur
    humeur_prompt = {
        "Cool": "Tu es Hartur, un ado cool et sympa.",
        "Drôle": "Tu es Hartur, très drôle et amusant.",
        "Gentil": "Tu es Hartur, très gentil et bienveillant.",
        "Sarcastique": "Tu es Hartur, sarcastique mais drôle."
    }

    system_prompt = humeur_prompt[mood]

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
        return "Petit bug avec l'IA 😅"


# ======================================================
# 💾 SAVE
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
# 📋 MENU
# ======================================================
menu = st.sidebar.selectbox(
    "Menu",
    ["💬 Discussion", "🔐 Admin"]
)

# ======================================================
# 💬 DISCUSSION
# ======================================================
if menu == "💬 Discussion":

    st.title("🤖 Hartur IA")

    st.sidebar.write(
        datetime.now().strftime("🕒 %H:%M")
    )

    # 👤 connexion
    if st.session_state.nom is None:

        nom = st.text_input("Ton prénom ou pseudo :")

        if st.button("Lancer"):

            if nom.strip():

                st.session_state.nom = nom.strip()

                # 🔥 recharge ancien historique
                st.session_state.messages = load_old_messages(
                    st.session_state.nom
                )

                st.session_state.session_id = str(uuid.uuid4())

                st.rerun()

    else:

        st.success(f"Salut {st.session_state.nom} 😄")

        st.sidebar.write(f"👤 {st.session_state.nom}")

        # 📸 image
        image = st.file_uploader(
            "📸 Envoie une image",
            type=["png", "jpg", "jpeg"]
        )

        if image:
            st.image(image)

        # 💬 historique
        for m in st.session_state.messages:

            with st.chat_message(m["role"]):
                st.markdown(m["content"])

        prompt = st.chat_input("Écris ici...")

        if prompt:

            # USER
            st.session_state.messages.append({
                "role": "user",
                "content": prompt
            })

            with st.chat_message("user"):
                st.markdown(prompt)

            # IA
            reponse = appeler_mistral(prompt)

            st.session_state.messages.append({
                "role": "assistant",
                "content": reponse
            })

            with st.chat_message("assistant"):
                st.markdown(reponse)

            # 💾 SAVE
            save_message(
                st.session_state.nom,
                st.session_state.session_id,
                prompt,
                reponse
            )

# ======================================================
# 🔐 ADMIN
# ======================================================
elif menu == "🔐 Admin":

    st.title("🔐 Admin")

    if not st.session_state.admin_auth:

        pwd = st.text_input(
            "Mot de passe :",
            type="password"
        )

        if st.button("Connexion"):

            if pwd == "babar":

                st.session_state.admin_auth = True
                st.rerun()

            else:
                st.error("Mot de passe incorrect")

    else:

        st.success("Connecté 🔓")

        st.subheader("📂 Conversations")

        os.makedirs("data", exist_ok=True)

        dates = sorted(os.listdir("data"), reverse=True)

        total_users = 0

        if not dates:

            st.info("Aucune conversation.")

        else:

            for date in dates:

                date_path = f"data/{date}"

                if os.path.isdir(date_path):

                    with st.expander(f"📅 {date}"):

                        files = os.listdir(date_path)

                        total_users += len(files)

                        if not files:

                            st.write("Aucune conversation.")

                        else:

                            for file in files:

                                if file.endswith(".txt"):

                                    name = file.replace(
                                        ".txt",
                                        ""
                                    ).replace(
                                        "_",
                                        " "
                                    ).title()

                                    st.markdown(f"👤 **{name}**")

                                    with open(
                                        f"{date_path}/{file}",
                                        "r",
                                        encoding="utf-8"
                                    ) as f:

                                        st.text(f.read())

                                    st.divider()

        st.sidebar.write(f"👥 Utilisateurs : {total_users}")

        if st.button("Déconnexion"):

            st.session_state.admin_auth = False
            st.rerun()
