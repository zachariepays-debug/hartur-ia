import streamlit as st
import requests
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="Hartur IA", page_icon="🤖")

# Initialisation des variables pour éviter les erreurs d'affichage
if "messages" not in st.session_state:
    st.session_state.messages = []
if "admin_auth" not in st.session_state:
    st.session_state.admin_auth = False

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
        return "Petit bug technique avec l'IA."

# --- NAVIGATION ---
menu = st.sidebar.selectbox("Menu", ["💬 Discussion", "🔐 Admin"])

# ======================================================
# 💬 DISCUSSION (Sauvegarde automatique)
# ======================================================
if menu == "💬 Discussion":
    st.title("🤖 Hartur IA")

    if "nom" not in st.session_state:
        nom_saisi = st.text_input("Ton prénom pour commencer :")
        if st.button("Lancer"):
            if nom_saisi.strip():
                st.session_state.nom = nom_saisi
                st.rerun()
    else:
        for m in st.session_state.messages:
            with st.chat_message(m["role"]):
                st.markdown(m["content"])

        prompt = st.chat_input("Écris ici...")
        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            reponse = appeler_mistral(prompt)
            with st.chat_message("assistant"):
                st.markdown(reponse)
            st.session_state.messages.append({"role": "assistant", "content": reponse})

            # SAUVEGARDE DANS FIREBASE (Dossier 'discussions')
            try:
                db.collection("discussions").add({
                    "nom": st.session_state.nom,
                    "texte": prompt,
                    "reponse": reponse,
                    "date": datetime.utcnow()
                })
            except:
                pass

# ======================================================
# 🔐 ADMIN (Dossiers par utilisateur)
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
        st.subheader("📂 Dossiers de conversations")
        
        try:
            # Récupération de tous les messages
            docs = list(db.collection("discussions").stream())
            
            if not docs:
                st.info("Aucun message trouvé dans la base.")
            else:
                # Regroupement automatique par nom
                convs = {}
                for d in docs:
                    data = d.to_dict()
                    u = data.get("nom", "Anonyme")
                    if u not in convs: convs[u] = []
                    convs[u].append(data)

                # Affichage d'un dossier (expander) par utilisateur
                for user, messages in convs.items():
                    with st.expander(f"👤 Conversation de {user}"):
                        for m in reversed(messages):
                            # On lit 'texte' ou 'ecris' pour être sûr de rien rater
                            msg_user = m.get('texte') or m.get('ecris') or "Vide"
                            st.write(f"💬 **{user}:** {msg_user}")
                            st.write(f"🤖 **Hartur:** {m.get('reponse')}")
                            st.divider()
        except Exception as e:
            st.error(f"Erreur Firebase : {e}")

        if st.button("🔄 Actualiser"):
            st.rerun()
