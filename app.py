import streamlit as st
import os
import requests
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# ======================================================
# ⚙️ CONFIGURATION
# ======================================================
st.set_page_config(page_title="Hartur IA", page_icon="🤖", layout="wide")

if not firebase_admin._apps:
    try:
        cred = credentials.Certificate('arthure-ia-firebase-adminsdk-fbsvc-8c2d7737ee.json')
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"Erreur Firebase : {e}")

db = firestore.client()
api_key = st.secrets.get("MISTRAL_KEY")

# ======================================================
# 💾 SESSION STATE
# ======================================================
if "page" not in st.session_state: st.session_state.page = "home"
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "username" not in st.session_state: st.session_state.username = None
if "messages" not in st.session_state: st.session_state.messages = []
if "humeur" not in st.session_state: st.session_state.humeur = "Cool"

# ======================================================
# 🧠 IA LOGIQUE (FLUIDITÉ AMÉLIORÉE)
# ======================================================
def generer_reponse(prompt):
    if not api_key:
        return "Clé API manquante."

    # On définit des instructions qui privilégient la discussion directe
    instructions = {
        "Cool": "Tu es Hartur, un ado cool. Parle normalement, sans faire de listes, sois bref et amical. Tutoie.",
        "Drôle": "Réponds avec humour et des emojis, comme si on était sur WhatsApp.",
        "Sérieux": "Réponds de manière concise et directe, sans analyse inutile.",
        "Sarcastique": "Sois ironique et un peu moqueur, mais reste fluide.",
        "Raisonnement complexe": "Explique simplement mais avec intelligence, sans structure rigide."
    }
    
    system_content = instructions.get(st.session_state.humeur, "Tu es Hartur, réponds de façon fluide.")

    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}"}
    data = {
        "model": "open-mistral-7b",
        "messages": [
            {"role": "system", "content": system_content},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7  # Ajoute un peu de créativité pour plus de naturel
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        # On renvoie uniquement le texte de la réponse, sans fioritures
        return response.json()['choices'][0]['message']['content']
    except:
        return "Désolé, j'ai eu un bug réseau. On reprend ?"

# ======================================================
# 🏠 NAVIGATION
# ======================================================
if st.session_state.page == "home":
    st.title("🤖 Hartur IA")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🔑 Connexion"): st.session_state.page = "login"; st.rerun()
    with c2:
        if st.button("🔐 Admin"): st.session_state.page = "admin"; st.rerun()

elif st.session_state.page == "login":
    u = st.text_input("Pseudo")
    if st.button("Lancer le chat"):
        if u:
            st.session_state.logged_in = True
            st.session_state.username = u
            st.session_state.page = "chat"
            st.rerun()

# ======================================================
# 💬 CHAT (FLUIDE)
# ======================================================
elif st.session_state.page == "chat":
    st.title(f"🤖 Hartur")
    
    st.sidebar.selectbox("Ton mood :", ["Cool", "Drôle", "Sérieux", "Sarcastique"], key="humeur")

    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    user_input = st.chat_input("Dis-moi...")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"): st.markdown(user_input)

        # Ici, l'IA génère la réponse directe sans passer par l'ancien système de questions
        reponse = generer_reponse(user_input)
        
        st.session_state.messages.append({"role": "assistant", "content": reponse})
        with st.chat_message("assistant"): st.markdown(reponse)

        # Sauvegarde silencieuse Firebase
        try:
            db.collection("discussions").add({
                "nom": st.session_state.username,
                "texte": user_input,
                "reponse": reponse,
                "date": datetime.utcnow()
            })
        except: pass

# ======================================================
# 🔐 ADMIN
# ======================================================
elif st.session_state.page == "admin":
    st.title("🔐 Admin")
    if st.text_input("Pass", type="password") == "babar":
        docs = db.collection("discussions").order_by("date", direction=firestore.Query.DESCENDING).limit(20).stream()
        for d in docs:
            msg = d.to_dict()
            st.write(f"**{msg.get('nom')}**: {msg.get('texte')}")
            st.write(f"🤖: {msg.get('reponse')}")
            st.divider()
    if st.button("Retour"): st.session_state.page = "home"; st.rerun()
