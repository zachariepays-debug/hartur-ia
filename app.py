import streamlit as st
import requests
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import uuid

# --- CONFIGURATION ---
st.set_page_config(page_title="Hartur IA", page_icon="🤖")

# --- SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "admin_auth" not in st.session_state:
    st.session_state.admin_auth = False
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "nom" not in st.session_state:
    st.session_state.nom = None

# --- FIREBASE ---
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate('arthure-ia-firebase-adminsdk-fbsvc-8c2d7737ee.json')
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"Erreur Firebase : {e}")

db = firestore.client()

# --- MISTRAL ---
try:
    api_key = st.secrets["MISTRAL_KEY"]
except Exception:
    api_key = None

def appeler_mistral(prompt):
    if not api_key:
        return "Erreur : Clé API non configurée."

    # Réponse spéciale créateur
    if any(x in prompt.lower() for x in ["qui t'a créé", "ton créateur", "t'a fait"]):
        return "J'ai été créé par Zacharie Pays 🤖 C'est lui le boss !"

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
        response = requests.post(url, headers=headers, json=data, timeout=15)
        return response.json()['choices'][0]['message']['content']
    except Exception:
        return "Petit bug technique avec l'IA."

# --- MENU ---
menu = st.sidebar.selectbox("Menu", ["💬 Discussion", "🔐 Admin"])

# ======================================================
# 💬 DISCUSSION
# ======================================================
if menu == "💬 Discussion":
    st.title("🤖 Hartur IA")

    if st.session_state.nom is None:
        nom_saisi = st.text_input("Ton prénom pour commencer :")
        if st.button("Lancer"):
            if nom_saisi.strip():
                st.session_state.nom = nom_saisi.strip()
                st.rerun()
    else:
        st.sidebar.write(f"Session de : **{st.session_state.nom}**")
        
        # Affichage du chat
        for m in st.session_state.messages:
            with st.chat_message(m["role"]):
                st.markdown(m["content"])

        prompt = st.chat_input("Écris ici...")

        if prompt:
            # Affichage User
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # IA
            reponse = appeler_mistral(prompt)
            st.session_state.messages.append({"role": "assistant", "content": reponse})
            with st.chat_message("assistant"):
                st.markdown(reponse)

            # 🔥 SAUVEGARDE FIREBASE (Structure : conversations -> session_id -> messages)
            try:
                # 1. On crée ou met à jour le dossier de la session
                doc_ref = db.collection("conversations").document(st.session_state.session_id)
                doc_ref.set({
                    "nom": st.session_state.nom,
                    "derniere_activite": datetime.utcnow()
                }, merge=True)

                # 2. On ajoute le message dans la sous-collection
                doc_ref.collection("messages").add({
                    "user": prompt,
                    "ia": reponse,
                    "timestamp": datetime.utcnow()
                })
            except Exception as e:
                st.error(f"Erreur de sauvegarde : {e}")

# ======================================================
# 🔐 ADMIN
# ======================================================
elif menu == "🔐 Admin":
    st.title("🔐 Espace Admin")

    if not st.session_state.admin_auth:
        pwd = st.text_input("Mot de passe :", type="password")
        if st.button("Se connecter"):
            if pwd == "babar":
                st.session_state.admin_auth = True
                st.rerun()
            else:
                st.error("Mot de passe incorrect")
    else:
        st.sidebar.button("Déconnexion", on_click=lambda: st.session_state.update({"admin_auth": False}))
        st.subheader("📂 Conversations par utilisateur")

        try:
            # On récupère toutes les sessions de la collection "conversations"
            sessions = db.collection("conversations").order_by("derniere_activite", direction=firestore.Query.DESCENDING).stream()

            for s in sessions:
                s_data = s.to_dict()
                nom_user = s_data.get('nom', 'Anonyme')
                
                # On crée un dossier (expander) pour chaque session
                with st.expander(f"👤 {nom_user} (ID: {s.id[:5]}...)"):
                    # On va chercher les messages à l'intérieur de cette session
                    msgs = db.collection("conversations").document(s.id).collection("messages").order_by("timestamp").stream()
                    
                    found = False
                    for m in msgs:
                        found = True
                        m_data = m.to_dict()
                        st.write(f"💬 **Lui:** {m_data.get('user')}")
                        st.write(f"🤖 **Hartur:** {m_data.get('ia')}")
                        st.divider()
                    
                    if not found:
                        st.write("Aucun message dans cette session.")

        except Exception as e:
            st.error(f"Erreur Firebase : {e}")

        if st.button("🔄 Actualiser"):
            st.rerun()
