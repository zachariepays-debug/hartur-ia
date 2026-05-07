import streamlit as st
import requests
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# --- CONFIGURATION INITIALE ---
st.set_page_config(page_title="Hartur IA", page_icon="🤖")

# Connexion Firebase
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate('arthure-ia-firebase-adminsdk-fbsvc-8c2d7737ee.json')
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"Erreur Firebase : {e}")

db = firestore.client()

# --- CONFIGURATION MISTRAL ---
try:
    api_key = st.secrets["MISTRAL_KEY"]
except:
    api_key = "TA_CLE_POUR_TEST_LOCAL"

def appeler_mistral(prompt):
    p = prompt.lower()
    # Réponse personnalisée sur le créateur
    if any(word in p for word in ["créateur", "createur", "qui t'a fait", "qui t'a créé"]):
        return "J'ai été conçu par Zacharie Pays."
    
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
    
    # CHANGEMENT DU TON : Plus neutre et professionnel
    instructions = "Tu es Hartur, un assistant virtuel poli, clair et respectueux. Évite le langage trop familier."
    
    data = {
        "model": "open-mistral-7b",
        "messages": [
            {"role": "system", "content": instructions},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        return response.json()['choices'][0]['message']['content']
    except:
        return "Désolé, je rencontre une petite difficulté technique pour répondre."

# --- INTERFACE ---
st.title("🤖 Hartur IA")

# --- ESPACE ADMIN DANS LA BARRE LATÉRALE ---
st.sidebar.title("🔐 Administration")
pwd = st.sidebar.text_input("Code Admin", type="password")

if pwd == "babar": # Ton mot de passe
    st.sidebar.success("Accès autorisé")
    st.divider()
    st.subheader("📊 Historique des discussions")
    
    try:
        msgs = db.collection('discussions').order_by('date', direction='DESCENDING').limit(20).stream()
        groupes = {}
        for doc in msgs:
            d = doc.to_dict()
            n = d.get('nom', 'Inconnu')
            if n not in groupes: groupes[n] = []
            groupes[n].append(d)
        
        for n, hist in groupes.items():
            with st.expander(f"👤 {n}"):
                for c in hist:
                    st.write(f"❓ **Lui:** {c['texte']}")
                    st.write(f"🤖 **Hartur:** {c['reponse']}")
                    st.divider()
    except:
        st.write("Aucune donnée disponible.")

# --- ZONE DE CHAT PRINCIPALE ---
if "nom" not in st.session_state:
    st.subheader("Bienvenue !")
    nom_saisi = st.text_input("Entrez votre prénom pour commencer :")
    if st.button("Valider"):
        if nom_saisi:
            st.session_state.nom = nom_saisi
            st.rerun()
else:
    st.write(f"Bonjour **{st.session_state.nom}**, en quoi puis-je vous aider ?")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Affichage des messages
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    # Entrée utilisateur
    if prompt := st.chat_input("Écrivez votre message ici..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        with st.chat_message("assistant"):
            reponse = appeler_mistral(prompt)
            st.markdown(reponse)
            st.session_state.messages.append({"role": "assistant", "content": reponse})
            
            # Sauvegarde Firebase
            try:
                db.collection('discussions').add({
                    'nom': st.session_state.nom,
                    'texte': prompt,
                    'reponse': reponse,
                    'date': datetime.now()
                })
            except:
                pass
