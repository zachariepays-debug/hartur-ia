import streamlit as st
import requests
import firebase_admin
from firebase_admin import credentials, firestore

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Hartur IA", page_icon="🤖")

# Connexion Firebase (Vérifie bien le nom de ton fichier .json sur GitHub)
if not firebase_admin._apps:
    cred = credentials.Certificate("arthure-ia-firebase-adminsdk-fbsvc-8c2d7737ee.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

# --- 2. TON DE L'IA (Rectifié : Neutre et Pro) ---
instruction = "Tu es Hartur, un assistant virtuel poli et efficace. Tu réponds de façon claire et tu évites de te répéter inutilement."

# --- 3. BARRE LATÉRALE (ADMIN) ---
st.sidebar.title("🔐 Administration")
mot_de_passe_saisi = st.sidebar.text_input("Code secret", type="password")
MOT_DE_PASSE_CORRECT = "1234" # <--- METS TON CODE ICI

# --- 4. INTERFACE PRINCIPALE ---
st.title("🤖 Hartur IA")

# Case pour le nom (comme au début)
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
    if prompt := st.chat_input("Ta question pour Hartur..."):
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
                    "nom": nom_utilisateur,
                    "question": prompt,
                    "reponse": reponse,
                    "date": firestore.SERVER_TIMESTAMP
                })
                
                with st.chat_message("assistant"):
                    st.markdown(reponse)
                    st.session_state.messages.append({"role": "assistant", "content": reponse})
            else:
                st.error("L'IA ne répond pas. Vérifie ta clé Mistral.")
        except Exception as e:
            st.error(f"Erreur technique : {e}")

# --- 5. AFFICHAGE ADMIN (La liste complète de retour) ---
if mot_de_passe_saisi == MOT_DE_PASSE_CORRECT:
    st.divider()
    st.header("📊 Liste complète des messages")
    
    # On récupère tous les messages triés par date
    docs = db.collection("messages").order_by("date", direction=firestore.Query.DESCENDING).limit(20).stream()
    
    for doc in docs:
        d = doc.to_dict()
        st.info(f"👤 **{d.get('nom')}** : {d.get('question')}")
        st.write(f"🤖 **Hartur** : {d.get('reponse')}")
        st.write("---")
