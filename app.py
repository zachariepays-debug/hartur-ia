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
# Le code cherche la clé dans tes secrets Streamlit
try:
    api_key = st.secrets["MISTRAL_KEY"]
except:
    api_key = "TA_CLE_DE_SECOURS_ICI"

def appeler_mistral(prompt):
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}"}
    data = {
        "model": "open-mistral-7b",
        "messages": [{"role": "system", "content": "Tu es Hartur, un ado cool."},
                     {"role": "user", "content": prompt}]
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        return response.json()['choices'][0]['message']['content']
    except:
        return "Petit bug avec l'IA."

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
        prompt = st.chat_input("Dis-moi un truc...")
        if prompt:
            reponse = appeler_mistral(prompt)
            st.write(f"**Toi:** {prompt}")
            st.write(f"**Hartur:** {reponse}")
            # Sauvegarde dans Firebase
            db.collection("discussions").add({
                "nom": st.session_state.nom,
                "texte": prompt,
                "reponse": reponse,
                "date": datetime.utcnow()
            })

# ======================================================
# 🔐 ADMIN (AFFICHAGE AUTOMATIQUE)
# ======================================================
elif menu == "🔐 Admin":
    st.title("🔐 Espace Admin")

    if "admin_log" not in st.session_state:
        st.session_state.admin_log = False

    # Formulaire si non connecté
    if not st.session_state.admin_log:
        pwd = st.text_input("Mot de passe :", type="password")
        if st.button("Se connecter"):
            if pwd == "babar":
                st.session_state.admin_log = True
                st.rerun()
            else:
                st.error("Mot de passe incorrect")
    
    # Affichage des dossiers si connecté
    else:
        st.sidebar.button("Quitter l'Admin", on_click=lambda: st.session_state.update({"admin_log": False}))
        
        st.subheader("📂 Dossiers de conversations")
        
        try:
            # Récupération de TOUS les messages
            docs = list(db.collection("discussions").stream())
            
            if not docs:
                st.info("Aucun message trouvé. Envoie un message dans 'Discussion' pour tester.")
            else:
                convs = {}
                for d in docs:
                    data = d.to_dict()
                    u = data.get("nom", "Inconnu")
                    if u not in convs: convs[u] = []
                    convs[u].append(data)

                # Affichage par utilisateur
                for user, messages in convs.items():
                    with st.expander(f"👤 {user} ({len(messages)} messages)"):
                        for m in reversed(messages):
                            st.write(f"💬 **Lui:** {m.get('texte')}")
                            st.write(f"🤖 **Hartur:** {m.get('reponse')}")
                            st.divider()
        except Exception as e:
            st.error(f"Erreur Firebase : {e}")

        if st.button("🔄 Actualiser"):
            st.rerun()
