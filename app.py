import streamlit as st
import requests
import firebase_admin
from firebase_admin import credentials, firestore

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Hartur IA", page_icon="🤖")

# Connexion Firebase (Vérifie bien que le nom du fichier .json est le même sur ton GitHub)
if not firebase_admin._apps:
    cred = credentials.Certificate("arthure-ia-firebase-adminsdk-fbsvc-8c2d7737ee.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

# --- 2. TON DE L'IA (Rectifié : Neutre et Poli) ---
# J'ai retiré le côté "cool cool" pour quelque chose de plus équilibré.
instruction = "Tu es Hartur, un assistant IA poli et moderne. Tu réponds de façon amicale mais professionnelle."

# --- 3. BARRE LATÉRALE (ADMIN) ---
st.sidebar.title("🔐 Administration")
mot_de_passe_saisi = st.sidebar.text_input("Code secret", type="password")
MOT_DE_PASSE_CORRECT = "1234" # <--- TON CODE ICI

# --- 4. INTERFACE PRINCIPALE ---
st.title("🤖 Hartur IA")

# On remet exactement la case prénom comme au début
nom_utilisateur = st.text_input("Comment t'appelles-tu ?")

if not nom_utilisateur:
    st.info("👋 Bonjour ! Entre ton nom pour commencer à discuter.")
else:
    st.write(f"Ravi de t'aider, **{nom_utilisateur}** !")
    
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
                
                # Sauvegarde Firebase avec le NOM
                db.collection("messages").add({
                    "nom": nom_utilisateur,
                    "question": prompt,
                    "reponse": reponse,
                    "date": firestore.SERVER_TIMESTAMP
                })
                
                with st.chat_message("assistant"):
                    st.markdown(reponse)
                    st.session_state.messages.append({"role": "assistant", "content": reponse})
            else:
                st.error("L'IA ne répond pas. Vérifie ta clé Mistral dans les Secrets.")
        except Exception as e:
            st.error(f"Erreur technique : {e}")

# --- 5. ESPACE ADMIN (Rectifié : s'affiche quand le mot de passe est bon) ---
if mot_de_passe_saisi == MOT_DE_PASSE_CORRECT:
    st.divider()
    st.header("📊 Historique Admin")
    # On récupère les messages directement
    docs = db.collection("messages").order_by("date", direction=firestore.Query.DESCENDING).limit(10).stream()
    for doc in docs:
        d = doc.to_dict()
        st.info(f"👤 {d.get('nom')} : {d.get('question')}")
