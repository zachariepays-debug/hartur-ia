import streamlit as st
import requests
import firebase_admin
from firebase_admin import credentials, firestore

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Hartur IA", page_icon="🤖")

# Connexion Firebase
if not firebase_admin._apps:
    try:
        # Vérifie que ce nom de fichier est exactement celui sur ton GitHub
        cred = credentials.Certificate("arthure-ia-firebase-adminsdk-fbsvc-8c2d7737ee.json")
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"Erreur de certificat Firebase : {e}")

db = firestore.client()

# --- 2. PERSONNALITÉ DE L'IA (Rectifiée : Neutre et Poli) ---
instruction = "Tu es Hartur, un assistant IA moderne, clair et respectueux. Ton ton est professionnel et amical."

# --- 3. BARRE LATÉRALE (ADMINISTRATION) ---
st.sidebar.title("🔐 Administration")
code_admin = st.sidebar.text_input("Code secret", type="password")
CODE_VALIDE = "1234" # <--- MODIFIE TON CODE ICI

# --- 4. INTERFACE PRINCIPALE ---
st.title("🤖 Hartur IA")

# Case pour le nom
nom_utilisateur = st.text_input("Comment t'appelles-tu ?", placeholder="Ton prénom...")

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

        # Appel à l'IA Mistral
        try:
            if "MISTRAL_KEY" not in st.secrets:
                st.error("Clé MISTRAL_KEY manquante dans les Secrets Streamlit.")
            else:
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
                    },
                    timeout=15
                )
                
                if res.status_code == 200:
                    reponse = res.json()['choices'][0]['message']['content']
                    
                    # Sauvegarde Firebase (avec sécurité si les règles bloquent)
                    try:
                        db.collection("messages").add({
                            "nom": nom_utilisateur,
                            "question": prompt,
                            "reponse": reponse,
                            "date": firestore.SERVER_TIMESTAMP
                        })
                    except:
                        pass # Continue même si la sauvegarde échoue
                    
                    with st.chat_message("assistant"):
                        st.markdown(reponse)
                        st.session_state.messages.append({"role": "assistant", "content": reponse})
                else:
                    st.error(f"L'IA ne répond pas (Erreur {res.status_code}).")
        except Exception as e:
            st.error(f"Erreur technique : {e}")

# --- 5. LOGIQUE ADMIN (Affichage de l'historique complet) ---
if code_admin == CODE_VALIDE:
    st.divider()
    st.header("📊 Historique des conversations")
    
    try:
        # Récupère les derniers messages enregistrés
        docs = db.collection("messages").order_by("date", direction=firestore.Query.DESCENDING).limit(20).stream()
        
        for doc in docs:
            d = doc.to_dict()
            st.info(f"👤 **{d.get('nom')}** : {d.get('question')}")
            st.write(f"🤖 *Hartur* : {d.get('reponse')}")
            st.write("---")
    except Exception as e:
        st.write("L'historique s'affichera ici dès que des messages seront enregistrés.")
