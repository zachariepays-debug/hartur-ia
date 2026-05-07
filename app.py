import streamlit as st
import requests
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# --- CONFIGURATION INITIALE ---
st.set_page_config(page_title="Hartur IA", page_icon="🤖")

# Firebase
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate('arthure-ia-firebase-adminsdk-fbsvc-8c2d7737ee.json')
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"Erreur Firebase : {e}")

db = firestore.client()

# --- MISTRAL ---
try:
    api_key = st.secrets["MISTRAL_KEY"]
except:
    api_key = "TA_CLE_POUR_TEST_LOCAL"


def appeler_mistral(prompt):
    p = prompt.lower()

    # 👑 CREATOR FIX
    if any(k in p for k in [
        "créateur", "createur", "qui t'a créé",
        "qui t'as créé", "qui est ton créateur",
        "ton créateur"
    ]):
        return "Mon créateur est Zacharie Pays."

    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    data = {
        "model": "open-mistral-7b",
        "messages": [
            {"role": "system", "content": "Tu es Hartur, IA cool et concise."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.8
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"Erreur API : {e}"


# =========================
# 📌 MENU (FIX IMPORTANT)
# =========================
menu = st.sidebar.selectbox(
    "Navigation",
    ["Discussion avec Hartur", "Espace Admin"]
)


# =========================
# 💬 CHAT
# =========================
if menu == "Discussion avec Hartur":

    st.title("🤖 Hartur IA")

    if "nom" not in st.session_state:
        nom = st.text_input("Ton nom ?")

        if st.button("Go"):
            st.session_state.nom = nom
            st.session_state.messages = []
            st.rerun()

    else:
        if "messages" not in st.session_state:
            st.session_state.messages = []

        for m in st.session_state.messages:
            with st.chat_message(m["role"]):
                st.markdown(m["content"])

        if prompt := st.chat_input("Écris un message..."):

            st.session_state.messages.append({"role": "user", "content": prompt})

            reponse = appeler_mistral(prompt)

            st.session_state.messages.append({"role": "assistant", "content": reponse})

            db.collection("discussions").add({
                "nom": st.session_state.nom,
                "texte": prompt,
                "reponse": reponse,
                "date": firestore.SERVER_TIMESTAMP
            })


# =========================
# 🔐 ADMIN PANEL (FIXED)
# =========================
elif menu == "Espace Admin":

    st.title("🔐 Admin Panel")

    if "is_admin" not in st.session_state:
        st.session_state.is_admin = False

    # --- LOGIN ---
    if not st.session_state.is_admin:

        pwd = st.text_input("Mot de passe :", type="password")

        if st.button("Connexion"):
            if pwd == "babar":
                st.session_state.is_admin = True
                st.rerun()
            else:
                st.error("Mot de passe incorrect ❌")

        st.stop()


    # =========================
    # 🔎 SEARCH
    # =========================
    search = st.text_input("🔎 Rechercher utilisateur / message")

    docs = db.collection("discussions").order_by("date").stream()

    groupes = {}

    for doc in docs:
        d = doc.to_dict()
        if not d:
            continue

        nom = d.get("nom", "Inconnu")

        if search:
            if search.lower() not in nom.lower() \
            and search.lower() not in d.get("texte", "").lower() \
            and search.lower() not in d.get("reponse", "").lower():
                continue

        if nom not in groupes:
            groupes[nom] = []

        groupes[nom].append(d)


    # =========================
    # 📊 AFFICHAGE GROUPÉ
    # =========================
    if not groupes:
        st.info("Aucune conversation")
    else:

        for nom, convs in sorted(groupes.items(), key=lambda x: len(x[1]), reverse=True):

            with st.expander(f"👤 {nom} ({len(convs)})"):

                for c in convs:
                    st.markdown(f"❓ {c.get('texte','')}")
                    st.markdown(f"🤖 {c.get('reponse','')}")
                    st.divider()
