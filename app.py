import streamlit as st
import requests
import firebase_admin
from firebase_admin import credentials, firestore

# --- CONFIGURATION ---
st.set_page_config(page_title="Hartur IA", page_icon="🤖")

# Connexion Firebase
if not firebase_admin._apps:
    # Vérifie que ce nom de fichier est le bon sur ton GitHub
    cred = credentials.Certificate("arthure-ia-firebase-adminsdk-fbsvc-8c2d7737ee.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

# --- TON DE L'IA (Un peu moins cool, plus équilibré) ---
instruction = "Tu es Hartur, un assistant poli et moderne. Ton ton est amical mais reste professionnel."

# --- BARRE LATÉRALE (ADMIN) ---
st.sidebar.title("🔐 Administration")
mot_de_passe_saisi = st.sidebar.text_input("Code secret", type="password")
MOT_DE_PASSE_CORRECT = "1234" # MODIFIE TON CODE ICI

# --- INTERFACE PRINCIPALE (AU MILIEU) ---
st.title("🤖 Hartur IA")

# Case pour le nom
nom_utilisateur = st.text_input("Comment t'appelles-tu ?", placeholder="Ton prénom ici...")

if not nom_utilisateur:
    st.info("👋 Bonjour ! Entre ton nom ci-dessus pour commencer à discuter avec Hartur.")
else:
    st.success(f"Ravi de t'aider, *{nom_utilisateur}* !")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Affichage du chat
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Entrée du message
    if prompt := st.chat_input("Ta question..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        try:
            api_key = st.secrets["MISTRAL_KEY"]
            headers = {"Authorization": f"Bearer {api_key}"}
            data = {
                "model": "mistral-tiny",
                "messages": [
                    {"role": "system", "content": instruction},
                    {"role": "user", "content": prompt}
                ]
            }
            res = requests.post("https://api.mistral.ai/v1/chat/completions", json=data, headers=headers)
            reponse = res.json()['choices'][0]['message']['content']
            
            # Sauvegarde dans Firebase avec le NOM
            db.collection("messages").add({
                "nom": nom_utilisateur,
                "question": prompt,
                "reponse": reponse,
                "date": firestore.SERVER_TIMESTAMP
            })
            
            with st.chat_message("assistant"):
                st.markdown(reponse)
                st.session_state.messages.append({"role": "assistant", "content": reponse})
        except:
            st.error("Petit souci technique avec l'IA. Vérifie ta clé Mistral.")

# --- AFFICHAGE HISTORIQUE (Si Admin connecté) ---
if mot_de_passe_saisi == MOT_DE_PASSE_CORRECT:
    st.divider()
    st.subheader("📊 Historique des conversations (Admin)")
    docs = db.collection("messages").order_by("date", direction=firestore.Query.DESCENDING).limit(15).stream()
    for doc in docs:
        d = doc.to_dict()
        st.write(f"👤 *{d.get('nom')}* : {d.get('question')}")
        st.write(f"🤖 Hartur : {d.get('reponse')}")
        st.write("---")
