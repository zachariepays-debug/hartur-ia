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

# --- CLEAN NOM ---
def clean_name(name):
    return name.strip().lower().replace(" ", "_")

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

    if any(x in prompt.lower() for x in ["qui t'a créé", "ton créateur", "t'a fait"]):
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
        response = requests.post(url, headers=headers, json=data, timeout=15)
        return response.json()['choices'][0]['message']['content']
    except Exception:
        return "Petit bug technique."


# --- MENU ---
menu = st.sidebar.selectbox("Menu", ["💬 Discussion", "🔐 Admin"])

# ======================================================
# 💬 DISCUSSION
# ======================================================
if menu == "💬 Discussion":
    st.title("🤖 Hartur IA")

    # 👤 NOM + RESET CHAT
    if st.session_state.nom is None:
        nom_saisi = st.text_input("Ton prénom pour commencer :")

        if st.button("Lancer"):
            if nom_saisi.strip():
                st.session_state.nom = nom_saisi.strip()

                # 🔥 IMPORTANT : nouvelle session à chaque connexion
                st.session_state.session_id = str(uuid.uuid4())
                st.session_state.messages = []

                st.rerun()

    else:
        st.sidebar.write(f"👤 {st.session_state.nom}")

        # 💬 affichage chat local
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

            # 🔥 FIREBASE
            try:
                user_id = clean_name(st.session_state.nom)

                db.collection("conversations") \
                  .document(user_id) \
                  .collection("sessions") \
                  .document(st.session_state.session_id) \
                  .collection("messages") \
                  .add({
                      "user": prompt,
                      "ia": reponse,
                      "timestamp": datetime.utcnow()
                  })

                db.collection("conversations").document(user_id).set({
                    "nom": st.session_state.nom,
                    "derniere_session": st.session_state.session_id
                }, merge=True)

            except Exception as e:
                st.error(f"Erreur Firebase : {e}")


# ======================================================
# 🔐 ADMIN
# ======================================================
elif menu == "🔐 Admin":
    st.title("🔐 Admin")

    if not st.session_state.admin_auth:
        pwd = st.text_input("Mot de passe :", type="password")
        if st.button("Se connecter"):
            if pwd == "babar":
                st.session_state.admin_auth = True
                st.rerun()
            else:
                st.error("Incorrect")

    else:
        st.sidebar.button(
            "Déconnexion",
            on_click=lambda: st.session_state.update({"admin_auth": False})
        )

        st.subheader("📂 Conversations")

        try:
            users = db.collection("conversations").stream()

            for u in users:
                st.markdown("---")
                st.write(f"👤 **{u.id}**")

                sessions = db.collection("conversations").document(u.id).collection("sessions").stream()

                for s in sessions:
                    st.write(f"📁 Session : {s.id}")

                    msgs = db.collection("conversations") \
                        .document(u.id) \
                        .collection("sessions") \
                        .document(s.id) \
                        .collection("messages") \
                        .stream()

                    for m in msgs:
                        d = m.to_dict()
                        st.write(f"💬 {d['user']}")
                        st.write(f"🤖 {d['ia']}")
                        st.divider()

        except Exception as e:
            st.error(f"Erreur Firebase : {e}")

        if st.button("🔄 Actualiser"):
            st.rerun()
