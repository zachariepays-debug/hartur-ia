import streamlit as st
import requests
import firebase_admin
from firebase_admin import credentials, firestore

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Hartur IA", page_icon="🤖")

# Connexion Firebase
if not firebase_admin._apps:
    # Vérifie que ce nom est identique à ton fichier .json sur GitHub
    cred = credentials.Certificate("arthure-ia-firebase-adminsdk-fbsvc-8c2d7737ee.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

# --- 2. PERSONNALITÉ (Équilibrée) ---
instruction = "Tu es Hartur, un assistant IA poli, moderne et amical. Réponds clairement sans être trop familier."

# --- 3. BARRE LATÉRALE (ADMIN) ---
st.sidebar.title("🔐 Administration")
mot_de_passe_saisi = st.sidebar.text_input("Code secret", type="password")
MOT_DE_PASSE_CORRECT = "1234" # <--- MODIFIE TON CODE ICI

# --- 4. INTERFACE PRINCIPALE ---
st.title("🤖 Hartur IA")

# Initialisation du nom dans la session pour que ça reste en mémoire
if "nom_valide" not in st.session_state:
    st.session_state.nom_valide = ""

# Formulaire d'entrée du nom (Case avec bouton pour mobile)
if st.session_state.nom_valide == "":
    nom_saisi = st.text_input("Comment t'appelles-tu ?", placeholder="Ton prénom ici...")
    if st.button("Commencer la discussion"):
        if nom_saisi:
            st.session_state.nom_valide = nom_saisi
            st.rerun()
        else:
            st.warning("Choisis un prénom d'abord.")
else:
    st.write(f"Ravi de t'aider, *{st.session_state.nom_valide}* !")
    if st.button("Changer de nom"):
        st.session_state.nom_valide = ""
        st.rerun()

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
                
                # Sauvegarde Firebase
                db.collection("messages").add({
                    "nom": st.session_state.nom_valide,
                    "question": prompt,
                    "reponse": reponse_ia,
                    "date": firestore.SERVER_TIMESTAMP
                })
                
                with st.chat_message("assistant"):
                    st.markdown(reponse_ia)
                    st.session_state.messages.append({"role": "assistant", "content": reponse_ia})
            else:
                st.error("L'IA ne répond pas. Vérifie la clé MISTRAL_KEY dans les Secrets Streamlit.")
        except Exception as e:
            st.error(f"Erreur : {e}")

# --- 5. AFFICHAGE ADMIN ---
if mot_de_passe_saisi == MOT_DE_PASSE_CORRECT:
    st.divider()
    st.subheader("📊 Historique Admin")
    docs = db.collection("messages").order_by("date", direction=firestore.Query.DESCENDING).limit(10).stream()
    for doc in docs:
        d = doc.to_dict()
        st.write(f"👤 *{d.get('nom')}* : {d.get('question')}")
        st.write(f"🤖 Hartur : {d.get('reponse')}")
        st.write("---")
