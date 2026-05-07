import streamlit as st
import requests
import firebase_admin
from firebase_admin import credentials, firestore

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Hartur IA", page_icon="🤖")

# Connexion Firebase (Vérifie bien le nom du fichier .json)
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate("arthure-ia-firebase-adminsdk-fbsvc-8c2d7737ee.json")
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"Erreur Firebase : {e}")

db = firestore.client()

# --- 2. TON IA ---
instruction = "Tu es Hartur, un assistant poli et moderne. Réponds de façon amicale mais professionnelle."

# --- 3. ADMIN ---
st.sidebar.title("🔐 Administration")
mot_de_passe_saisi = st.sidebar.text_input("Code secret", type="password")
MOT_DE_PASSE_CORRECT = "1234" 

# --- 4. INTERFACE ---
st.title("🤖 Hartur IA")
nom_utilisateur = st.text_input("Comment t'appelles-tu ?")

if not nom_utilisateur:
    st.info("👋 Bonjour ! Entre ton nom pour commencer.")
else:
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Ta question..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # --- LE TEST CRITIQUE ICI ---
        try:
            # On vérifie si la clé existe avant d'appeler
            if "MISTRAL_KEY" not in st.secrets:
                st.error("LA CLÉ MISTRAL_KEY EST ABSENTE DES SECRETS STREAMLIT !")
            else:
                api_key = st.secrets["MISTRAL_KEY"]
                headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
                data = {
                    "model": "mistral-tiny",
                    "messages": [{"role": "system", "content": instruction}, {"role": "user", "content": prompt}]
                }
                
                # On lance l'appel
                res = requests.post("https://api.mistral.ai/v1/chat/completions", json=data, headers=headers, timeout=15)
                
                if res.status_code == 200:
                    reponse = res.json()['choices'][0]['message']['content']
                    
                    # Sauvegarde
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
                    # SI CA REPOND PAS, ON DIT POURQUOI
                    st.error(f"Mistral refuse : Code {res.status_code} - {res.text}")
        except Exception as e:
            st.error(f"L'application a crashé ici : {e}")

# --- 5. HISTORIQUE ---
if mot_de_passe_saisi == MOT_DE_PASSE_CORRECT:
    st.divider()
    docs = db.collection("messages").order_by("date", direction=firestore.Query.DESCENDING).limit(10).stream()
    for doc in docs:
        d = doc.to_dict()
        st.info(f"👤 {d.get('nom')} : {d.get('question')}")
