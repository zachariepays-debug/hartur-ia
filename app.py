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
        # Utilisation du fichier JSON de configuration Firebase
        cred = credentials.Certificate('arthure-ia-firebase-adminsdk-fbsvc-8c2d7737ee.json')
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"Erreur Firebase : {e}")

db = firestore.client()

# --- MISTRAL ---
# Le script récupère la clé MISTRAL_KEY que tu as enregistrée dans les Secrets Streamlit
try:
    api_key = st.secrets["MISTRAL_KEY"]
except Exception:
    api_key = None

def appeler_mistral(prompt):
    if not api_key:
        return "Erreur : La clé API Mistral n'est pas configurée."
    
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}"}
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
        return res_json['choices'][0]['message']['content']
    except Exception as e:
        return f"Désolé, petit bug technique ! ({e})"

# --- NAVIGATION ---
menu = st.sidebar.selectbox("Menu", ["💬 Discussion", "🔐 Admin"])

# ======================================================
# 💬 SECTION DISCUSSION
# ======================================================
if menu == "💬 Discussion":
    st.title("🤖 Hartur IA")

    if "nom" not in st.session_state:
        nom_utilisateur = st.text_input("Salut ! C'est quoi ton prénom ?")
        if st.button("Lancer la discussion"):
            if nom_utilisateur.strip():
                st.session_state.nom = nom_utilisateur
                st.session_state.messages = []
                st.rerun()
    else:
        st.sidebar.write(f"Connecté : **{st.session_state.nom}**")
        if st.sidebar.button("Se déconnecter"):
            del st.session_state.nom
            st.rerun()

        # Affichage de l'historique de la session actuelle
        for m in st.session_state.messages:
            with st.chat_message(m["role"]):
                st.markdown(m["content"])

        prompt = st.chat_input("Dis-moi un truc...")

        if prompt:
            # Affichage immédiat du message utilisateur
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Appel de l'IA
            reponse = appeler_mistral(prompt)
            
            with st.chat_message("assistant"):
                st.markdown(reponse)
            st.session_state.messages.append({"role": "assistant", "content": reponse})

            # SAUVEGARDE DANS FIREBASE (Collection: discussions)
            try:
                db.collection("discussions").add({
                    "nom": st.session_state.nom,
                    "texte": prompt,
                    "reponse": reponse,
                    "date": datetime.utcnow()
                })
            except Exception:
                pass

# ======================================================
# 🔐 SECTION ADMIN (CORRIGÉE)
# ======================================================
elif menu == "🔐 Admin":
    st.title("🔐 Espace Admin")

    if "admin_auth" not in st.session_state:
        st.session_state.admin_auth = False

    # Formulaire de connexion
    if not st.session_state.admin_auth:
        mot_de_passe = st.text_input("Mot de passe :", type="password")
        if st.button("Se connecter"):
            if mot_de_passe == "babar":
                st.session_state.admin_auth = True
                st.rerun()
            else:
                st.error("❌ Mot de passe incorrect")
    
    # Affichage des conversations si connecté
    else:
        st.sidebar.button("Quitter l'Admin", on_click=lambda: st.session_state.update({"admin_auth": False}))
        st.subheader("📂 Historique des conversations")
        
        try:
            # Récupération de tous les documents de la collection "discussions"
            docs = list(db.collection("discussions").stream())
            
            if not docs:
                st.info("Aucun message trouvé dans la base de données.")
            else:
                # Regroupement des messages par nom d'utilisateur
                conversations = {}
                for d in docs:
                    data = d.to_dict()
                    u = data.get("nom", "Inconnu")
                    if u not in conversations:
                        conversations[u] = []
                    conversations[u].append(data)

                # Affichage des dossiers expander
                for user_name, msgs in conversations.items():
                    with st.expander(f"👤 {user_name} ({len(msgs)} messages)"):
                        # Tri des messages du plus récent au plus ancien
                        for m in reversed(msgs):
                            # On lit 'texte' ou 'ecris' pour récupérer les anciens messages
                            contenu = m.get('texte') or m.get('ecris') or "Message vide"
                            rep = m.get('reponse') or "Pas de réponse"
                            
                            st.write(f"❓ **Lui :** {contenu}")
                            st.write(f"🤖 **Hartur :** {rep}")
                            st.divider()
        except Exception as e:
            st.error(f"Erreur lors de la lecture des données : {e}")

        if st.button("🔄 Actualiser les messages"):
            st.rerun()
