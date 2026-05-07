import streamlit as st
import requests
import firebase_admin
from firebase_admin import credentials, firestore

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Hartur IA", page_icon="🤖")

# Connexion Firebase
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate("arthure-ia-firebase-adminsdk-fbsvc-8c2d7737ee.json")
        firebase_admin.initialize_app(cred)
    except:
        pass 

db = firestore.client()

# --- 2. PERSONNALITÉ (Le ton cool qui marche) ---
instruction = "Tu es Hartur, un assistant IA super cool, relax et branché. Parle de façon décontractée."

# --- 3. BARRE LATÉRALE ---
st.sidebar.title("🔐 Administration")
code_saisi = st.sidebar.text_input("Code secret", type="password")
MON_CODE = "1234" 

# --- 4. INTERFACE ---
st.title("🤖 Hartur IA")
nom = st.text_input("Comment t'appelles-tu ?")

if not nom:
    st.info("👋 Salut ! Entre ton nom pour commencer.")
else:
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Dis-moi tout..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Appel IA
        try:
            api_key = st.secrets["MISTRAL_KEY"]
            res = requests.post(
                "https://api.mistral.ai/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": "mistral-tiny",
                    "messages": [{"role": "system", "content": instruction}, {"role": "user", "content": prompt}]
                }
            )
            
            if res.status_code == 200:
                reponse = res.json()['choices'][0]['message']['content']
                
                # Sauvegarde Firebase
                db.collection("messages").add({
                    "nom": nom,
                    "question": prompt,
                    "reponse": reponse,
                    "date": firestore.SERVER_TIMESTAMP
                })
                
                with st.chat_message("assistant"):
                    st.markdown(reponse)
                    st.session_state.messages.append({"role": "assistant", "content": reponse})
        except:
            st.error("Petit bug, réessaie !")

# --- 5. LISTE ADMIN (Tout en bas) ---
if code_saisi == MON_CODE:
    st.divider()
    st.header("📊 Liste des messages")
    docs = db.collection("messages").order_by("date", direction=firestore.Query.DESCENDING).limit(20).stream()
    for doc in docs:
        d = doc.to_dict()
        st.info(f"👤 {d.get('nom')} : {d.get('question')}")
