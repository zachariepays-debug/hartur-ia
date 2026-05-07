import streamlit as st
import requests
import firebase_admin
from firebase_admin import credentials, firestore

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Hartur IA", page_icon="🤖")

# =========================
# FIREBASE INIT SAFE
# =========================
db = None

if not firebase_admin._apps:
    try:
        cred = credentials.Certificate(
            "arthure-ia-firebase-adminsdk-fbsvc-8c2d7737ee.json"
        )
        firebase_admin.initialize_app(cred)
        db = firestore.client()
    except:
        st.error("Erreur Firebase")

if db is None and firebase_admin._apps:
    db = firestore.client()


# =========================
# API KEY
# =========================
api_key = st.secrets.get("MISTRAL_KEY", "")


# =========================
# IA
# =========================
def appeler_mistral(prompt: str):

    p = prompt.lower()

    if "créateur" in p or "createur" in p:
        return "Je suis une création de Zacharie Pays."

    try:
        r = requests.post(
            "https://api.mistral.ai/v1/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            },
            json={
                "model": "open-mistral-7b",
                "messages": [
                    {"role": "system", "content": "IA simple et utile."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7
            }
        )

        return r.json()["choices"][0]["message"]["content"]

    except:
        return "Erreur IA"


# =========================
# MENU
# =========================
menu = st.sidebar.selectbox("Menu", ["Chat", "Admin"])


# =========================
# 💬 CHAT
# =========================
if menu == "Chat":

    st.title("🤖 Hartur IA")

    if "nom" not in st.session_state:
        nom = st.text_input("Ton nom ?")

        if st.button("Go") and nom:
            st.session_state.nom = nom
            st.session_state.messages = []
            st.rerun()

    else:

        st.subheader(st.session_state.nom)

        if "messages" not in st.session_state:
            st.session_state.messages = []

        for m in st.session_state.messages:
            with st.chat_message(m["role"]):
                st.write(m["content"])

        prompt = st.chat_input("Message...")

        if prompt:

            st.session_state.messages.append({"role": "user", "content": prompt})

            rep = appeler_mistral(prompt)

            st.session_state.messages.append({"role": "assistant", "content": rep})

            if db:
                db.collection("discussions").add({
                    "nom": st.session_state.nom,
                    "texte": prompt,
                    "reponse": rep
                })


# =========================
# 🔐 ADMIN
# =========================
else:

    st.title("Admin")

    if "admin" not in st.session_state:
        st.session_state.admin = False

    if not st.session_state.admin:

        pwd = st.text_input("Mot de passe", type="password")

        if st.button("Connexion"):
            if pwd == st.secrets.get("ADMIN_PASS", "babar"):
                st.session_state.admin = True
                st.rerun()
            else:
                st.error("Erreur")

        st.stop()


    # =========================
    # LOAD DATA
    # =========================
    search = st.text_input("Rechercher")

    docs = db.collection("discussions").stream()

    data = {}

    for d in docs:
        x = d.to_dict()
        if not x:
            continue

        nom = x.get("nom", "Inconnu")

        if search and search.lower() not in str(x).lower():
            continue

        data.setdefault(nom, []).append(x)


    # =========================
    # DISPLAY MINIMAL
    # =========================
    if not data:
        st.info("Aucune discussion")
    else:

        for nom, conv in data.items():

            with st.expander(f"{nom} ({len(conv)})"):

                for c in conv:

                    st.write("👤", c.get("texte", ""))
                    st.write("🤖", c.get("reponse", ""))
                    st.divider()
