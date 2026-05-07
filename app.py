import streamlit as st
import requests
import firebase_admin
from firebase_admin import credentials, firestore

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Hartur IA", page_icon="🤖")

# Connexion Firebase
if not firebase_admin._apps:
    # Vérifie que ce nom est identique à ton fichier sur GitHub
    cred = credentials.Certificate("arthure-ia-firebase-adminsdk-fbsvc-8c2d7737ee.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

# --- 2. PERSONNALITÉ (Ton équilibré) ---
instruction = "Tu es Hartur, un assistant poli, moderne et efficace. Réponds de façon amicale mais reste professionnel."

# --- 3. BARRE LATÉRALE (ADMIN) ---
st.sidebar.title("🔐 Administration")
mot_de_passe_saisi = st.sidebar.text_input("Code secret", type="password")
MOT_DE_PASSE_CORRECT = "1234" # <--- METS TON CODE ICI

# --- 4. INTERFACE PRINCIPALE ---
st.title("🤖 Hartur IA")

# Case pour le nom (comme au tout début)
nom_utilisateur = st.text_input("Comment t'appelles-tu ?", placeholder="Ton prénom ici...")

if not nom_utilisateur:
    st.info("👋 Bonjour ! Entre ton nom ci-dessus pour commencer à discuter.")
else:
    st.success(f"Ravi de t'aider, *{nom_utilisateur}* !")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Affichage des messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Entrée du message
    if prompt := st.chat_input("Ta question pour Hartur..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Appel à l'IA Mistral
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
            
            if res.status_code == 200:
                reponse_ia = res.json()['choices'][0]['message']['content']
                
                # Sauvegarde Firebase avec le NOM
                db.collection("messages").add({
                    "nom": nom_utilisateur,
                    "question": prompt,
                    "reponse": reponse_ia,
                    "date": firestore.SERVER_TIMESTAMP
                })
                
                with st.chat_message("assistant"):
                    st.markdown(reponse_ia)
                    st.session_state.messages.append({"role": "assistant", "content": reponse_ia})
            else:
                st.error("L'IA ne répond pas. Vérifie ta clé MISTRAL_KEY dans les Secrets.")
        except Exception as e:
            st.error(f"Erreur de connexion : {e}")

# --- 5. AFFICHAGE ADMIN (Correction : s'affiche dès que le MDP est bon) ---
if mot_de_passe_saisi == MOT_DE_PASSE_CORRECT:
    st.divider()
    st.subheader("📊 Historique Admin")
    try:
        docs = db.collection("messages").order_by("date", direction=firestore.Query.DESCENDING).limit(15).stream()
        for doc in docs:
            d = doc.to_dict()
            st.write(f"👤 *{d.get('nom')}* : {d.get('question')}")
            st.write(f"🤖 Hartur : {d.get('reponse')}")
            st.write("---")
    except Exception as e:
        st.write("L'historique s'affichera ici après les premiers messages.")
