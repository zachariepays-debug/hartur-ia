import streamlit as st
import requests
import firebase_admin
from firebase_admin import credentials, firestore

# --- CONFIGURATION ---
st.set_page_config(page_title="Hartur IA", page_icon="🤖")

# Connexion Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate("arthure-ia-firebase-adminsdk-fbsvc-8c2d7737ee.json")
    firebase_admin.initialize_app(cred)
db = firestore.client()

# --- TON DE L'IA (Rectifié : Neutre et Poli) ---
instruction = "Tu es Hartur, un assistant IA poli et moderne. Tu aides l'utilisateur avec respect et clarté."

# --- ADMIN ---
st.sidebar.title("🔐 Administration")
code_admin = st.sidebar.text_input("Code secret", type="password")
CODE_VALIDE = "1234" # Modifie ton code ici

# --- INTERFACE PRINCIPALE ---
st.title("🤖 Hartur IA")
nom = st.text_input("Comment t'appelles-tu ?")

if not nom:
    st.info("👋 Bonjour ! Entre ton nom pour commencer.")
else:
    st.write(f"Bonjour **{nom}**, comment puis-je t'aider ?")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Affichage du chat
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Zone de texte
    if prompt := st.chat_input("Ta question..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Appel à Mistral
        try:
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
                }
            )
            
            if res.status_code == 200:
                reponse = res.json()['choices'][0]['message']['content']
                
                # Sauvegarde Firebase
                db.collection("messages").add({
                    "nom": nom,
                    "question": prompt,
                    "reponse": reponse,
                    "date": firestore.SERVER_TIMESTAMP
                })
                
                with st.chat_message("assistant"):
                    st.markdown(reponse)
                    st.session_state.messages.append({"role": "assistant", "content": reponse})
            else:
                st.error(f"L'IA ne répond pas (Code {res.status_code}).")
        except Exception as e:
            st.error(f"Erreur technique : {e}")

# --- AFFICHAGE ADMIN ---
if code_admin == CODE_VALIDE:
    st.divider()
    st.header("📊 Historique Admin")
    docs = db.collection("messages").order_by("date", direction=firestore.Query.DESCENDING).limit(10).stream()
    for doc in docs:
        d = doc.to_dict()
        st.info(f"👤 {d.get('nom')} : {d.get('question')}")
        st.write(f"🤖 {d.get('reponse')}")
