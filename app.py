import streamlit as st
import requests
import firebase_admin
from firebase_admin import credentials, firestore

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Hartur IA", page_icon="🤖")

# --- CONNEXION FIREBASE ---
if not firebase_admin._apps:
    # Assurez-vous que ce nom correspond exactement au fichier sur votre GitHub
    cred = credentials.Certificate("arthure-ia-firebase-adminsdk-fbsvc-8c2d7737ee.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

# --- PERSONNALITÉ DE L'IA (Niveau de cool ajusté) ---
# Le ton est ici poli et moderne, mais sans excès de langage familier.
instruction = """
Tu es Hartur, un assistant IA intelligent, poli et efficace. 
Ton ton est amical et moderne, mais reste toujours professionnel et respectueux. 
Évite d'être 'trop cool' ou d'utiliser trop de jargon de rue, mais ne sois pas non plus trop rigide. 
Aide l'utilisateur de manière claire et directe.
"""

# --- BARRE LATÉRALE : ESPACE ADMIN ---
st.sidebar.title("🔐 Administration")
mot_de_passe_saisi = st.sidebar.text_input("Code d'accès", type="password")

# --- MOT DE PASSE À MODIFIER ICI ---
MOT_DE_PASSE_CORRECT = "1234" 

# --- INTERFACE DE CHAT PRINCIPALE ---
st.title("🤖 Hartur IA")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Affichage des messages de la session
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Zone d'écriture
if prompt := st.chat_input("Posez votre question à Hartur..."):
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
        reponse_ia = res.json()['choices'][0]['message']['content']
        
        # Sauvegarde dans Firestore
        db.collection("messages").add({
            "utilisateur": prompt, 
            "assistant": reponse_ia,
            "date": firestore.SERVER_TIMESTAMP
        })
        
        with st.chat_message("assistant"):
            st.markdown(reponse_ia)
            st.session_state.messages.append({"role": "assistant", "content": reponse_ia})
    except Exception as e:
        st.error("L'IA est indisponible pour le moment. Vérifiez vos clés.")

# --- AFFICHAGE DU PANNEAU ADMIN ---
# Si le mot de passe est bon, on affiche le contenu caché
if mot_de_passe_saisi == MOT_DE_PASSE_CORRECT:
    st.sidebar.success("Accès Admin déverrouillé")
    st.divider()
    st.header("📊 Historique des conversations (Admin)")
    
    # Récupération des 20 derniers messages sur Firebase
    docs = db.collection("messages").order_by("date", direction=firestore.Query.DESCENDING).limit(20).stream()
    
    for doc in docs:
        d = doc.to_dict()
        st.info(f"*U :* {d.get('utilisateur')}\n\n*H :* {d.get('assistant')}")
        st.write("---")
        
elif mot_de_passe_saisi != "":
    st.sidebar.error("Code incorrect")
