import streamlit as st
import requests
import firebase_admin
from firebase_admin import credentials, firestore

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Hartur IA", page_icon="🤖")

# Connexion Firebase (Vérifie bien le nom du fichier .json sur ton GitHub)
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate("arthure-ia-firebase-adminsdk-fbsvc-8c2d7737ee.json")
        firebase_admin.initialize_app(cred)
    except:
        st.error("Erreur de fichier Firebase. Vérifie le nom du .json")

db = firestore.client()

# --- 2. TON DE L'IA (Neutre et Poli) ---
instruction = "Tu es Hartur, un assistant IA poli et moderne. Tu réponds de façon amicale mais professionnelle."

# --- 3. BARRE LATÉRALE (ADMIN) ---
st.sidebar.title("🔐 Administration")
mot_de_passe_saisi = st.sidebar.text_input("Code secret", type="password")
MOT_DE_PASSE_CORRECT = "1234" # <--- TON CODE ICI

# --- 4. INTERFACE PRINCIPALE ---
st.title("🤖 Hartur IA")

# Système de validation du prénom (Bouton pour téléphone)
if "nom" not in st.session_state:
    st.session_state.nom = ""

if st.session_state.nom == "":
    nom_input = st.text_input("Ton prénom pour commencer :")
    if st.button("Valider le prénom"):
        if nom_input:
            st.session_state.nom = nom_input
            st.rerun()
else:
    st.write(f"Bonjour **{st.session_state.nom}**, je t'écoute !")
    if st.button("Changer de nom"):
        st.session_state.nom = ""
        st.rerun()

    # Chat
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Pose ta question ici..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Appel à Mistral
        try:
            api_key = st.secrets["MISTRAL_KEY"]
            res = requests.post(
                "https://api.mistral.ai/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
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
                    "nom": st.session_state.nom,
                    "question": prompt,
                    "reponse": reponse,
                    "date": firestore.SERVER_TIMESTAMP
                })
                
                with st.chat_message("assistant"):
                    st.markdown(reponse)
                    st.session_state.messages.append({"role": "assistant", "content": reponse})
            else:
                st.error("L'IA ne répond pas (Clé API peut-être invalide).")
        except Exception as e:
            st.error(f"Erreur technique : {e}")

# --- 5. ESPACE ADMIN (S'affiche en bas dès que le MDP est bon) ---
if mot_de_passe_saisi == MOT_DE_PASSE_CORRECT:
    st.divider()
    st.header("📊 Historique Admin")
    docs = db.collection("messages").order_by("date", direction=firestore.Query.DESCENDING).limit(10).stream()
    for doc in docs:
        d = doc.to_dict()
        st.info(f"👤 {d.get('nom')} : {d.get('question')}")
