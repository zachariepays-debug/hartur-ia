import streamlit as st
import requests
from datetime import datetime
import uuid
import os

# --- CONFIGURATION ---
st.set_page_config(page_title="Hartur IA", page_icon="🤖")

# --- SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "nom" not in st.session_state:
    st.session_state.nom = None
if "admin_auth" not in st.session_state:
    st.session_state.admin_auth = False


# --- MISTRAL ---
try:
    api_key = st.secrets["MISTRAL_KEY"]
except Exception:
    api_key = None


def appeler_mistral(prompt):
    if not api_key:
        return "Erreur : clé API manquante."

    if any(x in prompt.lower() for x in ["qui t'a créé", "ton créateur"]):
        return "J'ai été créé par Zacharie Pays 🤖"

    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}"}
    data = {
        "model": "open-mistral-7b",
        "messages": [
            {"role": "system", "content": "Tu es Hartur, un ado cool."},
            {"role": "user", "content": prompt}
        ]
    }

    try:
        r = requests.post(url, headers=headers, json=data, timeout=15)
        return r.json()['choices'][0]['message']['content']
    except Exception:
        return "Erreur IA."


# 💾 SAUVEGARDE PAR PERSONNE
def save_message(nom, session_id, user, ia):
    os.makedirs("data", exist_ok=True)

    filename = f"data/{nom.lower().replace(' ', '_')}.txt"

    with open(filename, "a", encoding="utf-8") as f:
        f.write(f"\nSESSION: {session_id}\n")
        f.write(f"[USER] {user}\n")
        f.write(f"[IA] {ia}\n")
        f.write("-" * 40 + "\n")


# --- MENU ---
menu = st.sidebar.selectbox("Menu", ["💬 Discussion", "🔐 Admin"])


# ======================================================
# 💬 DISCUSSION
# ======================================================
if menu == "💬 Discussion":
    st.title("🤖 Hartur IA")

    if st.session_state.nom is None:
        nom = st.text_input("Ton prénom :")

        if st.button("Lancer"):
            if nom.strip():
                st.session_state.nom = nom.strip()
                st.session_state.session_id = str(uuid.uuid4())
                st.session_state.messages = []
                st.rerun()

    else:
        st.sidebar.write(f"👤 {st.session_state.nom}")

        for m in st.session_state.messages:
            with st.chat_message(m["role"]):
                st.markdown(m["content"])

        prompt = st.chat_input("Écris ici...")

        if prompt:
            # user
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # IA
            reponse = appeler_mistral(prompt)
            st.session_state.messages.append({"role": "assistant", "content": reponse})

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
        pwd = st.text_input("Mot de passe :", type="password")

        if st.button("Connexion"):
            if pwd == "babar":
                st.session_state.admin_auth = True
                st.rerun()
            else:
                st.error("Mot de passe incorrect")

    else:
        st.success("Connecté 🔓")

        st.subheader("📂 Fiches utilisateurs")

        os.makedirs("data", exist_ok=True)
        files = os.listdir("data")

        if not files:
            st.info("Aucune conversation enregistrée.")
        else:
            for file in files:
                if file.endswith(".txt"):
                    name = file.replace(".txt", "").replace("_", " ").title()

                    with st.expander(f"👤 {name}"):
                        with open(f"data/{file}", "r", encoding="utf-8") as f:
                            st.text(f.read())

        if st.button("Déconnexion"):
            st.session_state.admin_auth = False
            st.rerun()
