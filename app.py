import streamlit as st
import requests
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import json

# --- CONFIGURATION INITIALE ---
st.set_page_config(page_title="Hartur IA", page_icon="🤖")

# Connexion Firebase (plus sécurisée pour GitHub)
if not firebase_admin._apps:
    try:
        # On utilise le fichier JSON que tu as mis sur GitHub
        cred = credentials.Certificate('arthure-ia-firebase-adminsdk-fbsvc-8c2d7737ee.json')
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"Erreur Firebase : {e}")

db = firestore.client()

# --- CONFIGURATION MISTRAL (VIA SECRETS) ---
# On ne met plus la clé ici, on la cache dans Streamlit
try:
    api_key = st.secrets["MISTRAL_KEY"]
except:
    api_key = "TA_CLE_POUR_TEST_LOCAL" # Uniquement pour tes tests sur ton PC

def appeler_mistral(prompt):
    p = prompt.lower()
    if any(word in p for word in ["créateur", "createur", "qui t'a fait", "qui t'a créé"]):
        return "C'est Zacharie Pays qui m'a créé. C'est lui le boss, il gère de fou !"
    
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
    
    instructions = "Tu es Hartur. Parle comme un ado cool et détendu, sois bref et sympa."
    
    data = {
        "model": "open-mistral-7b",
        "messages": [
            {"role": "system", "content": instructions},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.8
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        return response.json()['choices'][0]['message']['content']
    except:
        return "Désolé, j'ai un petit bug technique !"

# --- INTERFACE ---
menu = st.sidebar.selectbox("Navigation", ["Discussion avec Hartur", "Espace Admin"])

if menu == "Discussion avec Hartur":
    st.title("🤖 Parle avec Hartur !")
    if "nom" not in st.session_state:
        nom_saisi = st.text_input("Ton nom ?")
        if st.button("Go"):
            st.session_state.nom = nom_saisi
            st.rerun()
    else:
        if "messages" not in st.session_state:
            st.session_state.messages = []
        for m in st.session_state.messages:
            with st.chat_message(m["role"]): st.markdown(m["content"])

        if prompt := st.chat_input("Dis un truc..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            with st.chat_message("assistant"):
                reponse = appeler_mistral(prompt)
                st.markdown(reponse)
                st.session_state.messages.append({"role": "assistant", "content": reponse})
                db.collection('discussions').add({
                    'nom': st.session_state.nom, 'texte': prompt, 'reponse': reponse, 'date': datetime.now()
                })

elif menu == "Espace Admin":
    st.title("🔐 Admin")
    pwd = st.text_input("Mot de passe :", type="password")
    if pwd == "babar":
        msgs = db.collection('discussions').order_by('date', direction='ASCENDING').stream()
        groupes = {}
        for doc in msgs:
            d = doc.to_dict()
            n = d.get('nom', 'Inconnu')
            if n not in groupes: groupes[n] = []
            groupes[n].append(d)
        for n, hist in groupes.items():
            with st.expander(f"👤 {n}"):
                for c in hist:
                    st.write(f"❓ *Lui:* {c['texte']}\n🤖 *Hartur:* {c['reponse']}")
                    st.divider()