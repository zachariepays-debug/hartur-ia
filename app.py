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
        st.error(f"Erreur de connexion Firebase : {e}")

db = firestore.client()

# --- CONFIGURATION MISTRAL ---
api_key = st.secrets.get("MISTRAL_KEY", "TA_CLE_POUR_TEST_LOCAL")

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
            if nom_saisi:
                st.session_state.nom = nom_saisi
                st.rerun()
            else:
                st.warning("Écris un petit nom avant d'y aller !")
    else:
        if "messages" not in st.session_state:
            st.session_state.messages = []

        for m in st.session_state.messages:
            with st.chat_message(m["role"]): 
                st.markdown(m["content"])

        if prompt := st.chat_input("Dis un truc..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): 
                st.markdown(prompt)
            
            with st.chat_message("assistant"):
                reponse = appeler_mistral(prompt)
                st.markdown(reponse)
                st.session_state.messages.append({"role": "assistant", "content": reponse})
                
                # Sauvegarde Firebase
                db.collection('discussions').add({
                    'nom': st.session_state.nom, 
                    'texte': prompt, 
                    'reponse': reponse, 
                    'date': datetime.now()
                })

elif menu == "Espace Admin":
    st.title("🔐 Admin")

    # Utilisation du session_state pour rester connecté
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        pwd = st.text_input("Mot de passe :", type="password")
        if st.button("Se connecter"):
            if pwd == "babar":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Mot de passe incorrect")
    else:
        if st.button("Se déconnecter"):
            st.session_state.authenticated = False
            st.rerun()

        st.subheader("Historique des conversations")
        
        # Récupération des messages (sans order_by si l'index n'est pas encore créé)
        try:
            msgs = db.collection('discussions').order_by('date', direction='DESCENDING').stream()
            
            groupes = {}
            for doc in msgs:
                d = doc.to_dict()
                n = d.get('nom', 'Inconnu')
                if n not in groupes: 
                    groupes[n] = []
                groupes[n].append(d)

            if not groupes:
                st.info("Aucune discussion enregistrée pour le moment.")

            for n, hist in groupes.items():
                with st.expander(f"👤 {n} ({len(hist)} messages)"):
                    for c in hist:
                        # Formatage de la date si présente
                        date_str = c['date'].strftime("%d/%m %H:%M") if 'date' in c else ""
                        st.markdown(f"**[{date_str}]**")
                        st.write(f"❓ *Lui:* {c['texte']}")
                        st.write(f"🤖 *Hartur:* {c['reponse']}")
                        st.divider()
        except Exception as e:
            st.error(f"Erreur de lecture : {e}")
            st.info("Si l'erreur mentionne un 'index', clique sur le lien fourni par Firebase dans la console pour l'activer.")
