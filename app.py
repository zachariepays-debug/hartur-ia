import streamlit as st
import requests
import firebase_admin
from firebase_admin import credentials, firestore

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Hartur IA", page_icon="🤖")

# =========================
# FIREBASE SAFE INIT
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
# IA
# =========================
api_key = st.secrets.get("MISTRAL_KEY", "")

def appeler_mistral(prompt):

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
# 🔐 ADMIN PANEL (CARDS + CHAT VIEW)
# =========================
else:

    st.title("🔐 Admin Panel")

    if "admin" not in st.session_state:
        st.session_state.admin = False

    if not st.session_state.admin:

        pwd = st.text_input("Mot de passe", type="password")

        if st.button("Connexion"):
            if pwd == st.secrets.get("ADMIN_PASS", "babar"):
                st.session_state.admin = True
                st.rerun()
            else:
                st.error("Erreur mot de passe")

        st.stop()


    # =========================
    # LOAD DATA
    # =========================
    docs = db.collection("discussions").stream()

    users = {}

    for d in docs:
        x = d.to_dict()
        if not x:
            continue

        nom = x.get("nom", "Inconnu")
        users.setdefault(nom, []).append(x)


    # =========================
    # STATE
    # =========================
    if "selected_user" not in st.session_state:
        st.session_state.selected_user = None


    # =========================
    # VIEW 1 : CARDS
    # =========================
    if st.session_state.selected_user is None:

        st.subheader("👤 Utilisateurs")

        cols = st.columns(3)

        for i, (nom, conv) in enumerate(users.items()):

            with cols[i % 3]:

                if st.button(f"📦 {nom}\n({len(conv)} msgs)"):

                    st.session_state.selected_user = nom
                    st.rerun()


    # =========================
    # VIEW 2 : CONVERSATION
    # =========================
    else:

        nom = st.session_state.selected_user

        st.subheader(f"💬 {nom}")

        if st.button("⬅ Retour"):
            st.session_state.selected_user = None
            st.rerun()

        conv = users.get(nom, [])

        for c in conv:

            st.markdown(f"👤 {c.get('texte','')}")
            st.markdown(f"🤖 {c.get('reponse','')}")
            st.divider()
