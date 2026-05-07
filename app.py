import streamlit as st
import requests
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="Hartur IA", page_icon="🤖")

# Initialisation des variables de session pour éviter l'erreur AttributeError
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
# Utilisation de la clé enregistrée dans tes Secrets Streamlit
try:
    api_key = st.secrets["MISTRAL_KEY"]
except Exception:
    api_key = None

def appeler_mistral(prompt):
    if not api_key:
        return "Erreur : Clé API non configurée dans les Secrets."
    
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}"}
    data = {
        "model": "open-mistral-7b",
        "messages": [
            {"role": "system", "content": "Tu es Hartur, un ado cool. Tutoie l'utilisateur."},
            {"role": "user", "content": prompt}
        ]
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"Petit bug technique : {e}"

# --- NAVIGATION ---
menu = st.sidebar.selectbox("Menu", ["💬 Discussion", "🔐 Admin"])

# ======================================================
# 💬 SECTION DISCUSSION
# ======================================================
if menu == "💬 Discussion":
    st.title("🤖 Hartur IA")

    if "nom" not in st.session_state:
        nom_saisi = st.text_input("Salut ! C'est quoi ton prénom ?")
        if st.button("Lancer"):
            if nom_saisi.strip():
                st.session_state.nom = nom_saisi
                st.rerun()
    else:
        st.sidebar.write(f"Utilisateur : **{st.session_state.nom}**")
        
        # Affichage sécurisé de l'historique
        for m in st.session_state.messages:
            with st.chat_message(m["role"]):
                st.markdown(m["content"])

        prompt = st.chat_input("Écris ton message...")

        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            reponse = appeler_mistral(prompt)
            
            with st.chat_message("assistant"):
                st.markdown(reponse)
            st.session_state.messages.append({"role": "assistant", "content": reponse})

            # Sauvegarde Firebase (Collection : discussions)
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
# 🔐 SECTION ADMIN
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
                st.error("Incorrect")
    
    else:
        st.sidebar.button("Déconnexion", on_click=lambda: st.session_state.update({"admin_auth": False}))
        
        try:
            docs = list(db.collection("discussions").stream())
            if not docs:
                st.info("Aucun message dans 'discussions'.")
            else:
                convs = {}
                for d in docs:
                    data = d.to_dict()
                    u = data.get("nom", "Inconnu")
                    if u not in convs: convs[u] = []
                    convs[u].append(data)

                for user, msgs in convs.items():
                    with st.expander(f"👤 {user} ({len(msgs)} messages)"):
                        for m in reversed(msgs):
                            # On gère 'texte' ou 'ecris' pour les anciens messages
                            txt = m.get('texte') or m.get('ecris') or "Vide"
                            st.write(f"**Lui:** {txt}")
                            st.write(f"**IA:** {m.get('reponse')}")
                            st.divider()
        except Exception as e:
            st.error(f"Erreur lecture : {e}")
