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
        # Assure-tu que ce fichier .json est bien dans le même dossier que app.py
        cred = credentials.Certificate('arthure-ia-firebase-adminsdk-fbsvc-8c2d7737ee.json')
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"Erreur Firebase : {e}")

db = firestore.client()

# --- MISTRAL ---
# Priorité aux secrets Streamlit (pour la mise en ligne), sinon clé locale
api_key = st.secrets.get("MISTRAL_KEY", "TA_CLE_POUR_TEST_LOCAL")

def appeler_mistral(prompt):
    p = prompt.lower()

    # Ta petite touche perso (Zacharie le boss !)
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
        # Petit bouton pour changer de pseudo si besoin
        st.sidebar.write(f"Utilisateur : **{st.session_state.nom}**")
        if st.sidebar.button("Déconnexion"):
            del st.session_state.nom
            st.rerun()

        # Affichage des messages
        for m in st.session_state.messages:
            with st.chat_message(m["role"]):
                st.markdown(m["content"])

        prompt = st.chat_input("Écris ton message...")

        if prompt:
            # Affichage immédiat de l'utilisateur
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Appel de l'IA
            reponse = appeler_mistral(prompt)

            # Affichage réponse
            with st.chat_message("assistant"):
                st.markdown(reponse)
            st.session_state.messages.append({"role": "assistant", "content": reponse})

            # --- SAVE FIREBASE ---
            try:
                db.collection("discussions").add({
                    "nom": st.session_state.nom,
                    "texte": prompt,
                    "reponse": reponse,
                    "date": datetime.utcnow()
                })
            except Exception as e:
                st.error(f"Erreur sauvegarde : {e}")


# ======================================================
# 🔐 ADMIN
# ======================================================
elif menu == "🔐 Admin":
    st.title("🔐 Espace Admin")

    pwd = st.text_input("Mot de passe :", type="password")

    if pwd == "babar":
        st.success("✅ Accès autorisé")
        
        # 🔄 Récupération Firebase triée par date
        docs = db.collection("discussions").order_by("date", direction=firestore.Query.DESCENDING).stream()

        conversations = {}
        for d in docs:
            data = d.to_dict()
            nom = data.get("nom", "Inconnu")
            if nom not in conversations:
                conversations[nom] = []
            conversations[nom].append(data)

        st.subheader("📁 Historique des conversations")

        if not conversations:
            st.info("Aucune conversation enregistrée pour le moment.")

        for nom, msgs in conversations.items():
            # On affiche le nom et le nombre de messages
            with st.expander(f"👤 {nom} ({len(msgs)} échanges)"):
                for m in msgs:
                    # Affichage de l'heure
                    date_str = m['date'].strftime("%d/%m %H:%M") if 'date' in m else "Date inconnue"
                    
                    st.write(f"🕒 *Le {date_str}*")
                    st.markdown(f"❓ **{nom} :** {m['texte']}")
                    st.markdown(f"🤖 **Hartur :** {m['reponse']}")
                    st.divider()

        if st.button("🔄 Rafraîchir les données"):
            st.rerun()

    elif pwd:
        st.error("❌ Mot de passe incorrect")
