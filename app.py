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
        st.error(f"Erreur d'initialisation Firebase : {e}")

db = firestore.client()

# --- MISTRAL ---
# REMPLACE BIEN "TA_CLE_MISTRAL_ICI" PAR TA VRAIE CLÉ
api_key = "TA_CLE_MISTRAL_ICI" 

def appeler_mistral(prompt):
    p = prompt.lower()
    if any(word in p for word in ["créateur", "createur", "qui t'a fait", "qui t'a créé"]):
        return "C'est Zacharie Pays qui m'a créé. C'est lui le boss, il gère de fou !"

    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    data = {
        "model": "open-mistral-7b",
        "messages": [
            {"role": "system", "content": "Tu es Hartur, un ado cool et sympa. Tutoie l'utilisateur."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.8
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        res_json = response.json()
        if "choices" in res_json:
            return res_json['choices'][0]['message']['content']
        else:
            # Affiche l'erreur renvoyée par Mistral s'il y en a une
            return f"Erreur Mistral : {res_json}"
    except Exception as e:
        # Affiche l'erreur technique précise
        return f"Erreur technique précise : {e}"

# --- NAVIGATION ---
menu = st.sidebar.selectbox("Navigation", ["💬 Discussion", "🔐 Admin"])

# ======================================================
# 💬 DISCUSSION
# ======================================================
if menu == "💬 Discussion":
    st.title("🤖 Hartur IA")

    if "nom" not in st.session_state:
        nom = st.text_input("Ton prénom ou pseudo")
        if st.button("Entrer"):
            if nom.strip() != "":
                st.session_state.nom = nom
                st.session_state.messages = []
                st.rerun()
    else:
        st.sidebar.write(f"Connecté : **{st.session_state.nom}**")
        if st.sidebar.button("Se déconnecter"):
            del st.session_state.nom
            st.rerun()

        for m in st.session_state.messages:
            with st.chat_message(m["role"]):
                st.markdown(m["content"])

        prompt = st.chat_input("Dis quelque chose...")

        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            reponse = appeler_mistral(prompt)
            with st.chat_message("assistant"):
                st.markdown(reponse)
            st.session_state.messages.append({"role": "assistant", "content": reponse})

            # Sauvegarde automatique vers Firebase
            try:
                db.collection("discussions").add({
                    "nom": st.session_state.nom,
                    "texte": prompt,
                    "reponse": reponse,
                    "date": datetime.utcnow()
                })
            except:
                pass

# ======================================================
# 🔐 ADMIN
# ======================================================
elif menu == "🔐 Admin":
    st.title("🔐 Espace Admin")

    if "admin_auth" not in st.session_state:
        st.session_state.admin_auth = False

    if not st.session_state.admin_auth:
        pwd = st.text_input("Mot de passe :", type="password")
        if st.button("Se connecter"):
            if pwd == "babar":
                st.session_state.admin_auth = True
                st.rerun()
            else:
                st.error("❌ Mot de passe incorrect")
    else:
        if st.sidebar.button("Quitter l'Admin"):
            st.session_state.admin_auth = False
            st.rerun()

        st.subheader("📁 Historique des conversations")
        
        try:
            docs = list(db.collection("discussions").stream())
            if not docs:
                st.info("Aucun message trouvé.")
            else:
                conversations = {}
                for d in docs:
                    data = d.to_dict()
                    u = data.get("nom", "Inconnu")
                    if u not in conversations:
                        conversations[u] = []
                    conversations[u].append(data)

                for user_name, msgs in conversations.items():
                    with st.expander(f"👤 {user_name} ({len(msgs)} messages)"):
                        for m in reversed(msgs):
                            st.write(f"❓ **{user_name}:** {m.get('texte')}")
                            st.write(f"🤖 **Hartur:** {m.get('reponse')}")
                            st.divider()
        except Exception as e:
            st.error(f"Erreur Firebase : {e}")

        if st.button("🔄 Actualiser"):
            st.rerun()
