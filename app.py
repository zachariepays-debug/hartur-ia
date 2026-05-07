import streamlit as st
import requests
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="Hartur IA", page_icon="🤖")

# --- FIREBASE ---
if not firebase_admin._apps:
    try:
        # Utilise le fichier JSON que tu as dans ton dossier
        cred = credentials.Certificate('arthure-ia-firebase-adminsdk-fbsvc-8c2d7737ee.json')
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"Erreur de connexion Firebase : {e}")

db = firestore.client()

# --- MISTRAL (Lecture depuis les Secrets Streamlit) ---
try:
    api_key = st.secrets["MISTRAL_KEY"]
except Exception:
    st.error("La clé MISTRAL_KEY est manquante dans les Secrets.")
    api_key = None

def appeler_mistral(prompt):
    if not api_key: return "Erreur de configuration."
    
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}"}
    data = {
        "model": "open-mistral-7b",
        "messages": [
            {"role": "system", "content": "Tu es Hartur, un ado cool."},
            {"role": "user", "content": prompt}
        ]
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        return response.json()['choices'][0]['message']['content']
    except:
        return "Petit bug technique avec Mistral."

# --- NAVIGATION ---
menu = st.sidebar.selectbox("Menu", ["💬 Discussion", "🔐 Admin"])

# ======================================================
# 💬 DISCUSSION
# ======================================================
if menu == "💬 Discussion":
    st.title("🤖 Hartur IA")
    if "nom" not in st.session_state:
        nom = st.text_input("Ton prénom ?")
        if st.button("Go"):
            st.session_state.nom = nom
            st.session_state.messages = []
            st.rerun()
    else:
        for m in st.session_state.messages:
            with st.chat_message(m["role"]): st.markdown(m["content"])

        prompt = st.chat_input("Dis moi un truc...")
        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})
            reponse = appeler_mistral(prompt)
            st.session_state.messages.append({"role": "assistant", "content": reponse})
            
            # SAUVEGARDE DANS LA COLLECTION "discussions"
            db.collection("discussions").add({
                "nom": st.session_state.nom,
                "texte": prompt,
                "reponse": reponse,
                "date": datetime.utcnow()
            })
            st.rerun()

# ======================================================
# 🔐 ADMIN (AFFICHAGE DES CONVERSATIONS)
# ======================================================
elif menu == "🔐 Admin":
    st.title("🔐 Espace Admin")
    pwd = st.text_input("Mot de passe :", type="password")

    if pwd == "babar":
        st.success("Accès autorisé")
        
        # On force la lecture de la collection "discussions"
        try:
            docs = list(db.collection("discussions").stream())
            
            if not docs:
                st.warning("La collection 'discussions' est vide dans Firebase.")
            else:
                conversations = {}
                for d in docs:
                    data = d.to_dict()
                    u = data.get("nom", "Anonyme")
                    if u not in conversations: conversations[u] = []
                    conversations[u].append(data)

                for user, msgs in conversations.items():
                    with st.expander(f"👤 Messages de {user}"):
                        for m in reversed(msgs):
                            st.write(f"**Utilisateur:** {m.get('texte')}")
                            st.write(f"**Hartur:** {m.get('reponse')}")
                            st.divider()
        except Exception as e:
            st.error(f"Erreur de lecture : {e}")
