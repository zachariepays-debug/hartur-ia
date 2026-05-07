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
        cred = credentials.Certificate('arthure-ia-firebase-adminsdk-fbsvc-8c2d7737ee.json')
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"Erreur Firebase : {e}")

db = firestore.client()

# --- MISTRAL ---
api_key = st.secrets.get("MISTRAL_KEY", "TA_CLE_ICI")

def appeler_mistral(prompt):
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}"}
    data = {
        "model": "open-mistral-7b",
        "messages": [{"role": "user", "content": prompt}]
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        return response.json()['choices'][0]['message']['content']
    except:
        return "Erreur de connexion à l'IA."

# --- NAVIGATION ---
menu = st.sidebar.selectbox("Menu", ["💬 Discussion", "🔐 Admin"])

# ======================================================
# 💬 DISCUSSION
# ======================================================
if menu == "💬 Discussion":
    st.title("🤖 Hartur IA")
    if "nom" not in st.session_state:
        nom = st.text_input("Ton prénom ?")
        if st.button("Lancer"):
            st.session_state.nom = nom
            st.rerun()
    else:
        prompt = st.chat_input("Dis moi un truc...")
        if prompt:
            reponse = appeler_mistral(prompt)
            st.write(f"**Toi:** {prompt}")
            st.write(f"**Hartur:** {reponse}")
            # Sauvegarde
            db.collection("discussions").add({
                "nom": st.session_state.nom,
                "texte": prompt,
                "reponse": reponse,
                "date": datetime.utcnow()
            })

# ======================================================
# 🔐 ADMIN (CORRIGÉ POUR AFFICHER LES MESSAGES)
# ======================================================
elif menu == "🔐 Admin":
    st.title("🔐 Espace Admin")

    # Initialisation de l'état de connexion si besoin
    if "auth_admin" not in st.session_state:
        st.session_state.auth_admin = False

    # Étape 1 : Formulaire de connexion (si pas connecté)
    if not st.session_state.auth_admin:
        pwd = st.text_input("Mot de passe :", type="password")
        if st.button("Se connecter"):
            if pwd == "babar":
                st.session_state.auth_admin = True
                st.rerun() # Relance pour effacer le champ password
            else:
                st.error("Mot de passe incorrect")

    # Étape 2 : Affichage des données (si connecté)
    else:
        st.sidebar.button("Déconnexion Admin", on_click=lambda: st.session_state.update({"auth_admin": False}))
        
        st.subheader("📁 Dossiers de conversations")
        
        try:
            # Récupération de la collection "discussions"
            docs = list(db.collection("discussions").stream())
            
            if not docs:
                st.info("Aucun message trouvé dans la base 'discussions'.")
            else:
                convs = {}
                for d in docs:
                    data = d.to_dict()
                    u = data.get("nom", "Anonyme")
                    if u not in convs: convs[u] = []
                    convs[u].append(data)

                # Création d'un menu déroulant par utilisateur
                for user, messages in convs.items():
                    with st.expander(f"👤 {user} ({len(messages)} messages)"):
                        for m in reversed(messages):
                            st.write(f"💬 **Message :** {m.get('texte')}")
                            st.write(f"🤖 **Réponse :** {m.get('reponse')}")
                            st.divider()
        except Exception as e:
            st.error(f"Erreur de lecture Firebase : {e}")

        if st.button("🔄 Rafraîchir les données"):
            st.rerun()
