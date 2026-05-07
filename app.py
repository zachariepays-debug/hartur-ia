import streamlit as st
import requests
import firebase_admin
from firebase_admin import credentials, firestore

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Hartur IA", page_icon="🤖")

# Connexion Firebase (Vérification de sécurité)
if not firebase_admin._apps:
    try:
        # Vérifie que ce nom de fichier est exactement celui sur ton GitHub
        cred = credentials.Certificate("arthure-ia-firebase-adminsdk-fbsvc-8c2d7737ee.json")
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"Erreur de certificat : {e}")

db = firestore.client()

# --- 2. PERSONNALITÉ DE L'IA ---
# Ton équilibré : amical et moderne, mais professionnel.
instruction = "Tu es Hartur, un assistant IA poli et efficace. Ton ton est moderne mais reste toujours professionnel et clair."

# --- 3. BARRE LATÉRALE (ADMINISTRATION) ---
st.sidebar.title("🔐 Administration")
code_admin = st.sidebar.text_input("Code d'accès", type="password")
MOT_DE_PASSE_CORRECT = "1234" # <--- MODIFIE TON CODE ICI

# --- 4. INTERFACE PRINCIPALE ---
st.title("🤖 Hartur IA")

# Gestion de la session pour éviter les rechargements inutiles
if "chat_nom" not in st.session_state:
    st.session_state.chat_nom = ""

# Étape 1 : Demander le prénom
if st.session_state.chat_nom == "":
    nom_saisi = st.text_input("Bonjour ! Quel est ton prénom ?", placeholder="Écris ici...")
    if st.button("Lancer la discussion"):
        if nom_saisi:
            st.session_state.chat_nom = nom_saisi
            st.rerun()
        else:
            st.warning("Merci d'entrer un prénom.")
else:
    # Étape 2 : Le Chat une fois le prénom validé
    st.write(f"Content de te voir, **{st.session_state.chat_nom}** !")
    
    if st.button("Quitter la session"):
        st.session_state.chat_nom = ""
        st.session_state.messages = []
        st.rerun()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Affichage de l'historique de la discussion
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Zone d'écriture
    if prompt := st.chat_input("Pose ta question à Hartur..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Appel à Mistral AI
        try:
            api_key = st.secrets["MISTRAL_KEY"]
            headers = {"Authorization": f"Bearer {api_key}"}
            payload = {
                "model": "mistral-tiny",
                "messages": [
                    {"role": "system", "content": instruction},
                    {"role": "user", "content": prompt}
                ]
            }
            
            res = requests.post("https://api.mistral.ai/v1/chat/completions", json=payload, headers=headers)
            
            if res.status_code == 200:
                reponse_ia = res.json()['choices'][0]['message']['content']
                
                # Sauvegarde dans Firestore
                db.collection("messages").add({
                    "nom": st.session_state.chat_nom,
                    "question": prompt,
                    "reponse": reponse_ia,
                    "date": firestore.SERVER_TIMESTAMP
                })
                
                with st.chat_message("assistant"):
                    st.markdown(reponse_ia)
                    st.session_state.messages.append({"role": "assistant", "content": reponse_ia})
            else:
                st.error("L'IA est indisponible. Vérifie ta clé Mistral dans les Secrets.")
        except Exception as e:
            st.error(f"Erreur technique : {e}")

# --- 5. LOGIQUE ADMIN (Correction Affichage) ---
if code_admin == MOT_DE_PASSE_CORRECT:
    st.divider()
    st.header("📊 Historique des conversations")
    
    try:
        # Récupère les 15 derniers messages
        docs = db.collection("messages").order_by("date", direction=firestore.Query.DESCENDING).limit(15).stream()
        for doc in docs:
            d = doc.to_dict()
            st.info(f"👤 **{d.get('nom')}** : {d.get('question')}")
            st.write(f"🤖 *Hartur* : {d.get('reponse')}")
            st.write("---")
    except Exception as e:
        st.write("Aucun message trouvé ou erreur de base de données.")
