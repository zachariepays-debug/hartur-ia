import streamlit as st
import google.generativeai as genai
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="Hartur IA", page_icon="🤖")

# --- FIREBASE INIT ---
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate("arthure-ia-firebase-adminsdk-fbsvc-8c2d7737ee.json")
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"Erreur Firebase : {e}")

db = firestore.client()

# --- GEMINI CONFIG ---
genai.configure(
    api_key="1ZfLHQLAFzfUZkhilAQyYtxyqirdNhhx"
)

model = genai.GenerativeModel("gemini-pro")
chat = model.start_chat(history=[])

# --- NAVIGATION ---
menu = st.sidebar.selectbox("Navigation", ["Discussion avec Hartur", "Espace Admin"])

# =====================================================
# 🔵 PAGE CHAT
# =====================================================
if menu == "Discussion avec Hartur":
    st.title("🤖 Parle avec Hartur")

    # --- NOM UTILISATEUR ---
    if "nom" not in st.session_state:
        nom = st.text_input("Comment t'appelles-tu ?", placeholder="Ex: Marc")

        if st.button("Commencer la discussion"):
            if nom.strip():
                st.session_state.nom = nom.strip()
                st.session_state.messages = []
                st.rerun()
            else:
                st.warning("Entre un nom valide.")

    else:
        st.write(f"Connecté en tant que : **{st.session_state.nom}**")

        # --- CHARGEMENT HISTORIQUE ---
        if "messages" not in st.session_state:
            st.session_state.messages = []

            with st.spinner("Hartur récupère vos souvenirs... 🧠"):
                docs = (
                    db.collection("discussions")
                    .where("nom", "==", st.session_state.nom)
                    .order_by("date")
                    .stream()
                )

                for doc in docs:
                    data = doc.to_dict()
                    st.session_state.messages.append({"role": "user", "content": data["texte"]})
                    st.session_state.messages.append({"role": "assistant", "content": data["reponse"]})

        # --- AFFICHAGE CHAT ---
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # --- INPUT UTILISATEUR ---
        if prompt := st.chat_input("Dis quelque chose à Hartur..."):
            st.session_state.messages.append({"role": "user", "content": prompt})

            with st.chat_message("user"):
                st.markdown(prompt)

            # --- IA RESPONSE ---
            with st.chat_message("assistant"):
                try:
                    response = chat.send_message(prompt)
                    reponse_ia = response.text
                except Exception as e:
                    reponse_ia = "Erreur IA 😕"
                    st.error(str(e))

                st.markdown(reponse_ia)
                st.session_state.messages.append({"role": "assistant", "content": reponse_ia})

            # --- SAVE FIREBASE ---
            try:
                db.collection("discussions").add({
                    "nom": st.session_state.nom,
                    "texte": prompt,
                    "reponse": reponse_ia,
                    "date": datetime.utcnow()
                })
            except Exception as e:
                st.error(f"Erreur sauvegarde Firebase : {e}")

# =====================================================
# 🔐 PAGE ADMIN
# =====================================================
elif menu == "Espace Admin":
    st.title("🔐 Espace Administrateur")

    pwd = st.text_input("Mot de passe admin :", type="password")

    if pwd == "babar":
        st.success("Accès autorisé ✅")

        docs = (
            db.collection("discussions")
            .order_by("date", direction=firestore.Query.DESCENDING)
            .stream()
        )

        for doc in docs:
            d = doc.to_dict()
            date_str = d["date"].strftime("%d/%m/%Y %H:%M")

            with st.expander(f"👤 {d['nom']} - {date_str}"):
                st.write(f"**Question :** {d['texte']}")
                st.write(f"**Hartur :** {d['reponse']}")

    elif pwd != "":
        st.error("Mot de passe incorrect ❌")
