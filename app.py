mport streamlit as st
import requests
import firebase_admin
from firebase_admin import credentials, firestore

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Hartur IA", page_icon="🤖")

# --- 2. CONNEXION FIREBASE ---
if not firebase_admin._apps:
    # VERIFIE BIEN CE NOM DE FICHIER SUR TON GITHUB
    cred = credentials.Certificate("arthure-ia-firebase-adminsdk-fbsvc-8c2d7737ee.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

# --- 3. TON DE L'IA (Equilibré) ---
instruction = "Tu es Hartur, un assistant IA poli et moderne. Ton ton est amical mais reste professionnel."

# --- 4. BARRE LATÉRALE (ADMIN) ---
st.sidebar.title("🔐 Administration")
mot_de_passe_saisi = st.sidebar.text_input("Code secret", type="password")
MOT_DE_PASSE_CORRECT = "1234" # <--- METS TON CODE ICI

# --- 5. INTERFACE PRINCIPALE (AU MILIEU) ---
st.title("🤖 Hartur IA")

# Case pour le nom
nom_utilisateur = st.text_input("Comment t'appelles-tu ?", placeholder="Ton prénom ici...")

if not nom_utilisateur:
    st.info("👋 Bonjour ! Entre ton nom ci-dessus pour commencer à discuter.")
else:
    st.success(f"Ravi de t'aider, *{nom_utilisateur}* !")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Affichage du chat historique de la session
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Entrée du message
    if prompt := st.chat_input("Ta question pour Hartur..."):
        # 1. Afficher le message de l'utilisateur
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 2. Appeler l'IA Mistral
        try:
            api_key = st.secrets["MISTRAL_KEY"]
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": "mistral-tiny",
                "messages": [
                    {"role": "system", "content": instruction},
                    {"role": "user", "content": prompt}
                ]
            }
            
            response = requests.post("https://api.mistral.ai/v1/chat/completions", json=data, headers=headers)
            
            if response.status_code == 200:
                reponse_ia = response.json()['choices'][0]['message']['content']
                
                # 3. Sauvegarder dans Firebase
                db.collection("messages").add({
                    "nom": nom_utilisateur,
                    "question": prompt,
                    "reponse": reponse_ia,
                    "date": firestore.SERVER_TIMESTAMP
                })
                
                # 4. Afficher la réponse de Hartur
                with st.chat_message("assistant"):
                    st.markdown(reponse_ia)
                    st.session_state.messages.append({"role": "assistant", "content": reponse_ia})
            else:
                st.error(f"Erreur Mistral : {response.status_code}")
        except Exception as e:
            st.error(f"Erreur technique : {e}")

# --- 6. AFFICHAGE HISTORIQUE (Pour l'Admin) ---
if mot_de_passe_saisi == MOT_DE_PASSE_CORRECT:
    st.divider()
    st.subheader("📊 Historique Admin")
    try:
        docs = db.collection("messages").order_by("date", direction=firestore.Query.DESCENDING).limit(10).stream()
        for doc in docs:
            d = doc.to_dict()
            st.write(f"👤 *{d.get('nom')}* : {d.get('question')}")
            st.write(f"🤖 Hartur : {d.get('reponse')}")
            st.write("---")
    except:
        st.write("Aucun historique trouvé pour le moment.")
