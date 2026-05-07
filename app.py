import streamlit as st
import requests
import firebase_admin
from firebase_admin import credentials, firestore

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Hartur IA", page_icon="🤖")

# Connexion Firebase (Vérifie bien que le nom du .json est le même sur GitHub)
if not firebase_admin._apps:
    cred = credentials.Certificate("arthure-ia-firebase-adminsdk-fbsvc-8c2d7737ee.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

# --- 2. TON DE L'IA (Équilibré) ---
instruction = "Tu es Hartur, un assistant IA poli, moderne et amical. Réponds clairement mais sans langage trop familier."

# --- 3. BARRE LATÉRALE (ADMIN) ---
st.sidebar.title("🔐 Administration")
mot_de_passe_saisi = st.sidebar.text_input("Code secret", type="password")
MOT_DE_PASSE_CORRECT = "1234" # <--- MODIFIE TON CODE ICI

# --- 4. INTERFACE PRINCIPALE (AU MILIEU) ---
st.title("🤖 Hartur IA")

# Case pour le nom (Indispensable pour commencer)
nom_utilisateur = st.text_input("Comment t'appelles-tu ?", placeholder="Ton prénom ici...")

if not nom_utilisateur:
    st.info("👋 Bonjour ! Entre ton nom ci-dessus pour commencer à discuter avec Hartur.")
else:
    st.success(f"Ravi de t'aider, *{nom_utilisateur}* !")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Affichage du chat historique
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
            headers = {"Authorization": f"Bearer {api_key}"}
            data = {
                "model": "mistral-tiny",
                "messages": [
                    {"role": "system", "content": instruction},
                    {"role": "user", "content": prompt}
                ]
            }
            res = requests.post("https://api.mistral.ai/v1/chat/completions", json=data, headers=headers)
            reponse_ia = res.json()['choices'][0]['message']['content']
            
            # Sauvegarde dans Firebase avec le NOM du visiteur
            db.collection("messages").add({
                "nom": nom_utilisateur,
                "question": prompt,
                "reponse": reponse_ia,
                "date": firestore.SERVER_TIMESTAMP
            })
            
            with st.chat_message("assistant"):
                st.markdown(reponse_ia)
                st.session_state.messages.append({"role": "assistant", "content": reponse_ia})
        except:
            st.error("Petit souci avec l'IA. Vérifie ta clé Mistral dans les secrets.")

# --- 5. AFFICHAGE DE L'HISTORIQUE (Si Admin déverrouillé) ---
if mot_de_passe_saisi == MOT_DE_PASSE_CORRECT:
    st.divider()
    st.subheader("📊 Historique des conversations (Admin)")
    try:
        # On récupère les derniers messages pour l'admin
        docs = db.collection("messages").order_by("date", direction=firestore.Query.DESCENDING).limit(15).stream()
        for doc in docs:
            d = doc.to_dict()
            st.write(f"👤 *{d.get('nom')}* : {d.get('question')}")
            st.write(f"🤖 Hartur : {d.get('reponse')}")
            st.write("---")
    except:
        st.write("L'historique sera visible ici dès que quelqu'un parlera à Hartur.")
