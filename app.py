import streamlit as st
import google.generativeai as genai
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# --- CONFIGURATION INITIALE ---
st.set_page_config(page_title="Hartur IA", page_icon="🤖")

# Connexion à Firebase arthure-ia-firebase-adminsdk-fbsvc-8c2d7737ee
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate('arthure-ia-firebase-adminsdk-fbsvc-8c2d7737ee.json')
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"Erreur de connexion Firebase : {e}")

db = firestore.client()

# Connexion à Gemini 1ZfLHQLAFzfUZkhilAQyYtxyqirdNhhx
genai.configure(api_key="1ZfLHQLAFzfUZkhilAQyYtxyqirdNhhx", transport='rest', default_metadata=[('x-goog-api-client', 'gl-python/3.14.0')])
# Configuration de Hartur avec ses instructions
model = genai.GenerativeModel('gemini-pro')
chat = model.start_chat(history=[])
# --- STRUCTURE DE NAVIGATION ---
menu = st.sidebar.selectbox("Navigation", ["Discussion avec Hartur", "Espace Admin"])

# --- PAGE DE CHAT ---
if menu == "Discussion avec Hartur":
    st.title("🤖 Parle avec Hartur !")

    # 1. Demander le nom pour la sauvegarde
    if "nom" not in st.session_state:
        nom_saisi = st.text_input("Comment t'appelles-tu ?", placeholder="Ex: Marc")
        if st.button("Commencer la discussion"):
            if nom_saisi:
                st.session_state.nom = nom_saisi.strip()
                st.rerun()
    else:
        st.write(f"Connecté en tant que : *{st.session_state.nom}*")
        
        # 2. Charger l'historique depuis Firebase si c'est une reconnexion
        if "messages" not in st.session_state:
            st.session_state.messages = []
            with st.spinner("Hartur recherche vos souvenirs... 🧠"):
                docs = db.collection('discussions').where('nom', '==', st.session_state.nom).order_by('date').stream()
                for doc in docs:
                    data = doc.to_dict()
                    st.session_state.messages.append({"role": "user", "content": data['texte']})
                    st.session_state.messages.append({"role": "assistant", "content": data['reponse']})

        # 3. Affichage des messages
        for m in st.session_state.messages:
            with st.chat_message(m["role"]):
                st.markdown(m["content"])

        # 4. Zone de saisie
        if prompt := st.chat_input("Dis quelque chose à Hartur..."):
            # Afficher le message utilisateur
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Obtenir la réponse de Hartur
            with st.chat_message("assistant"):
                response = chat.send_message(prompt)
                reponse_ia = response.text
                st.markdown(reponse_ia)
                st.session_state.messages.append({"role": "assistant", "content": reponse_ia})

            # 5. SAUVEGARDE DANS FIREBASE
            db.collection('discussions').add({
                'nom': st.session_state.nom,
                'texte': prompt,
                'reponse': reponse_ia,
                'date': datetime.now()
            })

# --- PAGE ADMIN ---
elif menu == "Espace Admin":
    st.title("🔐 Panneau Administrateur")
    pwd = st.text_input("Entrez le mot de passe admin :", type="password")
    
    if pwd == "babar":
        st.success("Accès autorisé. Voici toutes les discussions enregistrées :")
        
        # Récupérer tout l'historique de tout le monde
        tous_les_messages = db.collection('discussions').order_by('date', direction='DESCENDING').stream()
        
        for doc in tous_les_messages:
            d = doc.to_dict()
            date_str = d['date'].strftime("%d/%m %H:%M")
            with st.expander(f"👤 {d['nom']} - {date_str}"):
                st.write(f"*Question :* {d['texte']}")
                st.write(f"*Hartur :* {d['reponse']}")
    elif pwd != "":
        st.error("Mot de passe incorrect ❌")
