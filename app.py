import streamlit as st
import requests
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import uuid

# --- CONFIGURATION ---
st.set_page_config(page_title="Hartur IA", page_icon="🤖")

# --- SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "admin_auth" not in st.session_state:
    st.session_state.admin_auth = False
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "nom" not in st.session_state:
    st.session_state.nom = None

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
except Exception:
    api_key = None


def appeler_mistral(prompt):
    if not api_key:
        return "Erreur : Clé API non configurée."

    # Créateur
    if any(x in prompt.lower() for x in ["qui t'a créé", "ton créateur", "t'a fait"]):
        return "J'ai été créé par Zacharie Pays 🤖 C'est lui le boss !"

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
        response = requests.post(url, headers=headers, json=data, timeout=15)
        return response.json()['choices'][0]['message']['content']
    except Exception:
        return "Petit bug technique avec l'IA."


# --- MENU ---
menu = st.sidebar.selectbox("Menu", ["💬 Discussion", "🔐 Admin"])

# ======================================================
# 💬 DISCUSSION
# ======================================================
if menu == "💬 Discussion":
    st.title("🤖 Hartur IA")

    if st.session_state.nom is None:
        nom_saisi = st.text_input("Ton prénom pour commencer :")
        if st.button("Lancer"):
            if nom_saisi.strip():
                st.session_state.nom = nom_saisi.strip()
                st.rerun()
    else:
        st.sidebar.write(f"Session de : **{st.session_state.nom}**")

        # Chat affichage
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

            # 🔥 FIREBASE (SIMPLIFIÉ)
            try:
                db.collection("discutions").add({
                    "session_id": st.session_state.session_id,
                    "nom": st.session_state.nom,
                    "user": prompt,
                    "ia": reponse,
                    "timestamp": datetime.utcnow()
                })
            except Exception as e:
                st.error(f"Erreur de sauvegarde : {e}")


# ======================================================
# 🔐 ADMIN
# ======================================================
elif menu == "🔐 Admin":
    st.title("🔐 Espace Admin")

    if not st.session_state.admin_auth:
        pwd = st.text_input("Mot de passe :", type="password")
        if st.button("Se connecter"):
            if pwd == "babar":
                st.session_state.admin_auth = True
                st.rerun()
            else:
                st.error("Mot de passe incorrect")
    else:
        st.sidebar.button(
            "Déconnexion",
            on_click=lambda: st.session_state.update({"admin_auth": False})
        )

        st.subheader("📂 Conversations")

        try:
            msgs = db.collection("discutions").order_by(
                "timestamp",
                direction=firestore.Query.DESCENDING
            ).stream()

            current_session = None

            for m in msgs:
                data = m.to_dict()

                if current_session != data["session_id"]:
                    current_session = data["session_id"]
                    st.markdown("---")
                    st.write(f"👤 **{data['nom']}** | Session: {current_session[:6]}")

                st.write(f"💬 User: {data['user']}")
                st.write(f"🤖 IA: {data['ia']}")
                st.caption(data["timestamp"])
                st.divider()

        except Exception as e:
            st.error(f"Erreur Firebase : {e}")

        if st.button("🔄 Actualiser"):
            st.rerun()
