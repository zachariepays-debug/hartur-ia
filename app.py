import streamlit as st
import requests
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="Hartur IA", page_icon="🤖")

# --- FIREBASE ---
# Pour Streamlit Cloud, on utilise les secrets pour Firebase aussi
if not firebase_admin._apps:
    try:
        # Si tu es en local, il cherche le fichier JSON
        # Si tu es en ligne, il utilise les secrets Streamlit
        if "firebase" in st.secrets:
            f_cred = credentials.Certificate(dict(st.secrets["firebase"]))
            firebase_admin.initialize_app(f_cred)
        else:
            cred = credentials.Certificate('arthure-ia-firebase-adminsdk-fbsvc-8c2d7737ee.json')
            firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"Erreur de connexion base de données : {e}")

db = firestore.client()

# --- MISTRAL ---
# Lecture sécurisée de la clé dans les Secrets
api_key = st.secrets.get("MISTRAL_KEY", "CLE_NON_CONFIGUREE")

def appeler_mistral(prompt):
    if api_key == "CLE_NON_CONFIGUREE":
        return "Erreur : La clé API Mistral n'est pas configurée dans les secrets."

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
            {"role": "system", "content": "Tu es Hartur, un ado cool. Tutoie l'utilisateur."},
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
            return f"Note de Mistral : {res_json.get('detail', 'Problème de clé')}"
    except Exception as e:
        return f"Erreur technique : {e}"

# --- NAVIGATION ---
menu = st.sidebar.selectbox("Navigation", ["💬 Discussion", "🔐 Admin"])

# ======================================================
# 💬 DISCUSSION
# ======================================================
if menu == "💬 Discussion":
    st.title("🤖 Hartur IA")

    if "nom" not in st.session_state:
        nom = st.text_input("Salut ! C'est quoi ton prénom ?")
        if st.button("Lancer la discussion"):
            if nom.strip():
                st.session_state.nom = nom
                st.session_state.messages = []
                st.rerun()
    else:
        st.sidebar.button("Se déconnecter", on_click=lambda: st.session_state.clear())

        for m in st.session_state.messages:
            with st.chat_message(m["role"]):
                st.markdown(m["content"])

        prompt = st.chat_input("Écris ici...")

        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            reponse = appeler_mistral(prompt)
            with st.chat_message("assistant"):
                st.markdown(reponse)
            st.session_state.messages.append({"role": "assistant", "content": reponse})

            # Sauvegarde Firebase (Collection : discussions)
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

    if "admin_ok" not in st.session_state:
        st.session_state.admin_ok = False

    if not st.session_state.admin_ok:
        pwd = st.text_input("Mot de passe :", type="password")
        if st.button("Connexion"):
            if pwd == "babar":
                st.session_state.admin_ok = True
                st.rerun()
            else:
                st.error("Faux !")
    else:
        if st.sidebar.button("Sortir de l'Admin"):
            st.session_state.admin_ok = False
            st.rerun()

        try:
            # Récupération de ta collection "discussions"
            docs = list(db.collection("discussions").stream())
            if not docs:
                st.info("Aucune discussion dans la base.")
            else:
                convs = {}
                for d in docs:
                    data = d.to_dict()
                    u = data.get("nom", "Anonyme")
                    if u not in convs: convs[u] = []
                    convs[u].append(data)

                for user, msgs in convs.items():
                    with st.expander(f"👤 {user}"):
                        for m in reversed(msgs):
                            st.write(f"**Lui:** {m.get('texte')}")
                            st.write(f"**Hartur:** {m.get('reponse')}")
                            st.divider()
        except Exception as e:
            st.error(f"Erreur Firebase : {e}")
