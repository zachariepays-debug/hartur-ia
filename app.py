import streamlit as st
import requests
import firebase_admin
from firebase_admin import credentials, firestore

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Hartur IA", page_icon="🤖")

# Connexion Firebase
if not firebase_admin._apps:
    try:
        # Vérifie bien que ce nom de fichier est celui présent sur ton GitHub
        cred = credentials.Certificate("arthure-ia-firebase-adminsdk-fbsvc-8c2d7737ee.json")
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"Erreur de certificat Firebase : {e}")

db = firestore.client()

# --- 2. TON DE L'IA (Equilibré) ---
instruction = "Tu es Hartur, un assistant poli et moderne. Réponds de façon claire et professionnelle."

# --- 3. ADMIN ---
st.sidebar.title("🔐 Admin")
code_admin = st.sidebar.text_input("Code secret", type="password")
CODE_VALIDE = "1234" 

# --- 4. INTERFACE ---
st.title("🤖 Hartur IA")
nom = st.text_input("Ton prénom :")

if nom:
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    if prompt := st.chat_input("Ta question..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        try:
            # Appel Mistral
            key = st.secrets["MISTRAL_KEY"]
            res = requests.post(
                "https://api.mistral.ai/v1/chat/completions",
                headers={"Authorization": f"Bearer {key}"},
                json={
                    "model": "mistral-tiny",
                    "messages": [
                        {"role": "system", "content": instruction},
                        {"role": "user", "content": prompt}
                    ]
                },
                timeout=10
            )
            
            if res.status_code == 200:
                reponse = res.json()['choices'][0]['message']['content']
                
                # SAUVEGARDE (C'est ici que les règles Firebase comptent)
                try:
                    db.collection("messages").add({
                        "nom": nom,
                        "question": prompt,
                        "reponse": reponse,
                        "date": firestore.SERVER_TIMESTAMP
                    })
                except Exception as fire_err:
                    st.warning("Message non sauvegardé (Vérifie tes règles Firebase).")
                
                with st.chat_message("assistant"):
                    st.markdown(reponse)
                    st.session_state.messages.append({"role": "assistant", "content": reponse})
            else:
                st.error(f"Erreur IA : {res.status_code}")
        except Exception as e:
            st.error(f"Erreur technique : {e}")

# --- 5. HISTORIQUE ADMIN ---
if code_admin == CODE_VALIDE:
    st.divider()
    st.subheader("📊 Historique")
    docs = db.collection("messages").order_by("date", direction=firestore.Query.DESCENDING).limit(10).stream()
    for doc in docs:
        d = doc.to_dict()
        st.info(f"👤 {d.get('nom')} : {d.get('question')}")
