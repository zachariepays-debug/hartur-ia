import streamlit as st
import requests
import firebase_admin
from firebase_admin import credentials, firestore

# --- CONFIGURATION ---
st.set_page_config(page_title="Hartur IA", page_icon="🤖")

if not firebase_admin._apps:
    # Vérifie que ce nom de fichier est exactement le même sur ton GitHub
    cred = credentials.Certificate("arthure-ia-firebase-adminsdk-fbsvc-8c2d7737ee.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

# --- TON DE L'IA (Niveau cool moyen) ---
instruction = "Tu es Hartur, un assistant IA poli, moderne et amical. Réponds de façon claire mais pas trop formelle."

# --- LOGIQUE ADMIN ET STATUT ---
st.sidebar.title("🔐 Administration")
mot_de_passe_saisi = st.sidebar.text_input("Code secret Admin", type="password")
MOT_DE_PASSE_CORRECT = "1234" # <--- METS TON CODE ICI

# Récupération de l'état (Ouvert/Fermé) dans Firebase
status_ref = db.collection("config").document("app_status")
status_doc = status_ref.get()
is_open = status_doc.to_dict().get("is_open", True) if status_doc.exists else True

# Affichage des contrôles si le MDP est bon
if mot_de_passe_saisi == MOT_DE_PASSE_CORRECT:
    st.sidebar.success("Mode Admin activé")
    nouveau_statut = st.sidebar.radio("Statut de l'IA :", ["Ouvert", "Fermé"], index=0 if is_open else 1)
    if st.sidebar.button("Enregistrer le statut"):
        status_ref.set({"is_open": (nouveau_statut == "Ouvert")})
        st.rerun()
    st.sidebar.divider()

# --- INTERFACE PRINCIPALE ---
st.title("🤖 Hartur IA")

if is_open:
    # ON RÉCUPÈRE LE NOM ICI
    col1, col2 = st.columns([1, 2])
    with col1:
        nom_utilisateur = st.text_input("Ton prénom :", placeholder="Ex: Zacharie")

    if not nom_utilisateur:
        st.info("👋 Bonjour ! Entre ton nom ci-dessus pour commencer à discuter.")
    else:
        st.write(f"Ravi de te voir, *{nom_utilisateur}* !")

        if "messages" not in st.session_state:
            st.session_state.messages = []

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("Pose ta question..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            try:
                api_key = st.secrets["MISTRAL_KEY"]
                headers = {"Authorization": f"Bearer {api_key}"}
                data = {
                    "model": "mistral-tiny",
                    "messages": [{"role": "system", "content": instruction}, {"role": "user", "content": prompt}]
                }
                res = requests.post("https://api.mistral.ai/v1/chat/completions", json=data, headers=headers)
                reponse_ia = res.json()['choices'][0]['message']['content']
                
                # ON ENREGISTRE LE NOM DANS FIREBASE
                db.collection("messages").add({
                    "nom": nom_utilisateur,
                    "question": prompt,
                    "reponse": reponse_ia,
                    "date": firestore.SERVER_TIMESTAMP
                })
                
                with st.chat_message("assistant"):
                    st.markdown(reponse_ia)
                    st.session_state.messages.append({"role": "assistant", "content": reponse_ia})
            except:
                st.error("Erreur de connexion API.")

    # AFFICHAGE DE L'HISTORIQUE POUR L'ADMIN
    if mot_de_passe_saisi == MOT_DE_PASSE_CORRECT:
        st.divider()
        st.subheader("📊 Historique (Admin)")
        docs = db.collection("messages").order_by("date", direction=firestore.Query.DESCENDING).limit(10).stream()
        for doc in docs:
            d = doc.to_dict()
            st.text(f"👤 {d.get('nom')} : {d.get('question')}")
            st.write("---")

else:
    st.warning("⚠️ Hartur est actuellement hors ligne. Revenez plus tard !")
