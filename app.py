import streamlit as st
import requests
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="Hartur IA", page_icon="🤖")

# --- FIREBASE ---
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate('arthure-ia-firebase-adminsdk-fbsvc-8c2d7737ee.json')
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"Erreur Firebase : {e}")

db = firestore.client()

# --- MISTRAL ---
try:
    api_key = st.secrets["MISTRAL_KEY"]
except:
    api_key = "TA_CLE_POUR_TEST_LOCAL"


def appeler_mistral(prompt):
    p = prompt.lower()

    if any(word in p for word in ["créateur", "createur", "qui t'a fait", "qui t'a créé"]):
        return "C'est Zacharie Pays qui m'a créé. C'est lui le boss, il gère de fou !"

    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    instructions = "Tu es Hartur. Parle comme un ado cool, naturel et sympa."

    data = {
        "model": "open-mistral-7b",
        "messages": [
            {"role": "system", "content": instructions},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.8
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        return response.json()['choices'][0]['message']['content']
    except:
        return "Désolé, j'ai un bug technique !"


# --- NAVIGATION ---
menu = st.sidebar.selectbox("Navigation", ["💬 Discussion", "🔐 Admin"])


# ======================================================
# 💬 DISCUSSION
# ======================================================
if menu == "💬 Discussion":
    st.title("🤖 Hartur IA")

    if "nom" not in st.session_state:
        nom = st.text_input("Ton prénom ou pseudo")
        if st.button("Entrer"):
            if nom.strip() != "":
                st.session_state.nom = nom
                st.session_state.messages = []
                st.rerun()

    else:
        st.success(f"Connecté en tant que : {st.session_state.nom}")

        if "messages" not in st.session_state:
            st.session_state.messages = []

        for m in st.session_state.messages:
            with st.chat_message(m["role"]):
                st.markdown(m["content"])

        prompt = st.chat_input("Écris ton message...")

        if prompt:
            # USER
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # IA
            reponse = appeler_mistral(prompt)

            with st.chat_message("assistant"):
                st.markdown(reponse)

            st.session_state.messages.append({"role": "assistant", "content": reponse})

            # --- FIREBASE SAVE ---
            db.collection("discussions").add({
                "nom": st.session_state.nom,
                "texte": prompt,
                "reponse": reponse,
                "date": datetime.utcnow()
            })


# ======================================================
# 🔐 ADMIN
# ======================================================
elif menu == "🔐 Admin":
    st.title("🔐 Espace Admin")

    pwd = st.text_input("Mot de passe :", type="password")

    if pwd == "babar":

        st.success("Accès autorisé")

        # récupérer toutes les discussions
        docs = db.collection("discussions").stream()

        conversations = {}

        for d in docs:
            data = d.to_dict()
            nom = data.get("nom", "Inconnu")

            if nom not in conversations:
                conversations[nom] = []

            conversations[nom].append(data)

        st.subheader("📁 Utilisateurs connectés")

        for nom, msgs in conversations.items():

            if st.button(f"👤 {nom}"):
                st.session_state["selected_user"] = nom

        # affichage conversation sélectionnée
        if "selected_user" in st.session_state:
            user = st.session_state["selected_user"]

            st.markdown(f"## 💬 Conversation de {user}")

            for m in conversations[user]:
                st.write(f"❓ **User :** {m['texte']}")
                st.write(f"🤖 **Hartur :** {m['reponse']}")
                st.divider()

    elif pwd:
        st.error("Mauvais mot de passe")
