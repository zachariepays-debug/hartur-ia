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
        # Assure-toi que ce fichier .json est dans le dossier PROJET_HARTUR
        cred = credentials.Certificate('arthure-ia-firebase-adminsdk-fbsvc-8c2d7737ee.json')
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"Erreur d'initialisation Firebase : {e}")

db = firestore.client()

# --- MISTRAL ---
# Utilise ta clé Mistral ici
api_key = "TA_CLE_MISTRAL_ICI" 

def appeler_mistral(prompt):
    p = prompt.lower()

    # Réponse personnalisée sur le créateur
    if any(word in p for word in ["créateur", "createur", "qui t'a fait", "qui t'a créé"]):
        return "C'est Zacharie Pays qui m'a créé. C'est lui le boss, il gère de fou !"

    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    instructions = "Tu es Hartur. Parle comme un ado cool, naturel et sympa. Tutoie l'utilisateur."

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
    except Exception as e:
        return f"Désolé, j'ai un bug technique ! (Erreur: {e})"


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
        st.sidebar.write(f"Connecté en tant que : **{st.session_state.nom}**")
        
        if st.sidebar.button("Se déconnecter"):
            del st.session_state.nom
            st.rerun()

        # Affichage du chat
        for m in st.session_state.messages:
            with st.chat_message(m["role"]):
                st.markdown(m["content"])

        prompt = st.chat_input("Dis quelque chose à Hartur...")

        if prompt:
            # Affichage utilisateur
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Réponse IA
            reponse = appeler_mistral(prompt)

            with st.chat_message("assistant"):
                st.markdown(reponse)
            st.session_state.messages.append({"role": "assistant", "content": reponse})

            # --- SAUVEGARDE FIREBASE ---
            try:
                db.collection("discussions").add({
                    "nom": st.session_state.nom,
                    "texte": prompt,
                    "reponse": reponse,
                    "date": datetime.utcnow()
                })
            except Exception as e:
                st.error(f"Erreur sauvegarde Firebase : {e}")


# ======================================================
# 🔐 ADMIN (AFFICHAGE CORRIGÉ)
# ======================================================
elif menu == "🔐 Admin":
    st.title("🔐 Espace Admin")

    pwd = st.text_input("Mot de passe :", type="password")

    if pwd == "babar":
        st.success("✅ Accès autorisé")
        
        try:
            # Récupération brute des documents
            docs = list(db.collection("discussions").stream())
            
            if not docs:
                st.warning("Aucune conversation trouvée dans la base de données.")
            else:
                # Organisation des messages par utilisateur
                conversations = {}
                for d in docs:
                    data = d.to_dict()
                    user_name = data.get("nom", "Inconnu")
                    if user_name not in conversations:
                        conversations[user_name] = []
                    conversations[user_name].append(data)

                st.subheader(f"📁 {len(conversations)} utilisateur(s) trouvé(s)")

                # Affichage des dossiers par nom
                for user_name, msgs in conversations.items():
                    with st.expander(f"👤 {user_name} — ({len(msgs)} messages)"):
                        # Inversion pour voir le plus récent en premier
                        for m in reversed(msgs):
                            st.write(f"💬 **Message :** {m.get('texte')}")
                            st.write(f"🤖 **Réponse :** {m.get('reponse')}")
                            st.divider()
        
        except Exception as e:
            st.error(f"Erreur de lecture : {e}")

        if st.button("🔄 Actualiser"):
            st.rerun()

    elif pwd:
        st.error("❌ Mot de passe incorrect")
