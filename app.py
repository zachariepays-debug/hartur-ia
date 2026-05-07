import streamlit as st
import requests
import firebase_admin
from firebase_admin import credentials, firestore

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Hartur IA", page_icon="🤖")

# Connexion Firebase avec détection d'erreur
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate("arthure-ia-firebase-adminsdk-fbsvc-8c2d7737ee.json")
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"❌ Erreur de connexion Firebase : {e}")

db = firestore.client()

# --- 2. TON DE L'IA ---
instruction = "Tu es Hartur, un assistant IA poli et professionnel."

# --- 3. ADMINISTRATION ---
st.sidebar.title("🔐 Administration")
mot_de_passe = st.sidebar.text_input("Code secret", type="password")
CODE_OK = "1234" # À modifier

# --- 4. INTERFACE PRINCIPALE ---
st.title("🤖 Hartur IA")
nom_utilisateur = st.text_input("Comment t'appelles-tu ?")

if not nom_utilisateur:
    st.info("👋 Bonjour ! Entre ton nom pour commencer.")
else:
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Ta question..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # --- L'APPEL À L'IA ---
        try:
            # Vérification de la clé dans les secrets
            if "MISTRAL_KEY" not in st.secrets:
                st.error("⚠️ LA CLÉ 'MISTRAL_KEY' N'EST PAS TROUVÉE DANS LES SECRETS STREAMLIT.")
            else:
                api_key = st.secrets["MISTRAL_KEY"]
                
                # Envoi de la requête
                response = requests.post(
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

                if response.status_code == 200:
                    reponse_texte = response.json()['choices'][0]['message']['content']
                    
                    # Sauvegarde Firebase
                    try:
                        db.collection("messages").add({
                            "nom": nom_utilisateur,
                            "question": prompt,
                            "reponse": reponse_texte,
                            "date": firestore.SERVER_TIMESTAMP
                        })
                    except:
                        st.warning("⚠️ Impossible de sauvegarder dans Firebase (vérifie tes règles).")

                    with st.chat_message("assistant"):
                        st.markdown(reponse_texte)
                        st.session_state.messages.append({"role": "assistant", "content": reponse_texte})
                else:
                    st.error(f"❌ Erreur Mistral {response.status_code} : {response.text}")
        
        except Exception as e:
            st.error(f"❌ Erreur technique : {e}")

# --- 5. ESPACE ADMIN ---
if mot_de_passe == CODE_OK:
    st.divider()
    st.subheader("📊 Historique")
    docs = db.collection("messages").order_by("date", direction=firestore.Query.DESCENDING).limit(10).stream()
    for doc in docs:
        d = doc.to_dict()
        st.info(f"👤 {d.get('nom')} : {d.get('question')}")
