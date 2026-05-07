import streamlit as st
import requests
import firebase_admin
from firebase_admin import credentials, firestore

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Hartur IA", page_icon="🤖")

# =========================
# FIREBASE INIT SAFE
# =========================
db = None

if not firebase_admin._apps:
    try:
        cred = credentials.Certificate(
            "arthure-ia-firebase-adminsdk-fbsvc-8c2d7737ee.json"
        )
        firebase_admin.initialize_app(cred)
        db = firestore.client()
    except Exception as e:
        st.error(f"Erreur Firebase : {e}")

if db is None and firebase_admin._apps:
    db = firestore.client()


# =========================
# API KEY MISTRAL
# =========================
api_key = st.secrets.get("MISTRAL_KEY", "TA_CLE_POUR_TEST_LOCAL")


# =========================
# IA FUNCTION
# =========================
def appeler_mistral(prompt):
    p = prompt.lower()

    # 👑 CREATOR FIX (corrigé propre)
    if any(k in p for k in [
        "créateur", "createur", "qui t'a créé",
        "qui t'as créé", "qui est ton créateur",
        "ton créateur"
    ]):
        return "Je suis une création de Zacharie Pays."

    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    data = {
        "model": "open-mistral-7b",
        "messages": [
            {
                "role": "system",
                "content": "Tu es Hartur, une IA simple, fluide et amicale."
            },
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.8
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Erreur API : {e}"


# =========================
# MENU
# =========================
menu = st.sidebar.selectbox("Navigation", ["Discussion avec Hartur", "Espace Admin"])


# =========================
# 💬 CHAT
# =========================
if menu == "Discussion avec Hartur":

    st.title("🤖 Hartur IA")

    if "nom" not in st.session_state:
        nom = st.text_input("Ton nom ?")

        if st.button("Go") and nom:
            st.session_state.nom = nom
            st.session_state.messages = []
            st.rerun()

    else:
        st.subheader(f"Bienvenue {st.session_state.nom} 👋")

        if "messages" not in st.session_state:
            st.session_state.messages = []

        # affichage messages
        for m in st.session_state.messages:
            with st.chat_message(m["role"]):
                st.markdown(m["content"])

        prompt = st.chat_input("Écris un message...")

        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})

            reponse = appeler_mistral(prompt)

            st.session_state.messages.append({"role": "assistant", "content": reponse})

            # sauvegarde firebase
            if db:
                db.collection("discussions").add({
                    "nom": st.session_state.nom,
                    "texte": prompt,
                    "reponse": reponse,
                    "date": firestore.SERVER_TIMESTAMP
                })


# =========================
# 🔐 ADMIN PANEL
# =========================
elif menu == "Espace Admin":

    st.title("🔐 Admin Panel")

    if "is_admin" not in st.session_state:
        st.session_state.is_admin = False

    # LOGIN
    if not st.session_state.is_admin:

        pwd = st.text_input("Mot de passe :", type="password")

        if st.button("Connexion"):
            if pwd == st.secrets.get("ADMIN_PASS", "babar"):
                st.session_state.is_admin = True
                st.rerun()
            else:
                st.error("Mot de passe incorrect ❌")

        st.stop()

    # =========================
    # SEARCH
    # =========================
    search = st.text_input("🔎 Rechercher utilisateur / message")

    docs = db.collection("discussions") \
        .order_by("date", direction=firestore.Query.DESCENDING) \
        .stream()

    groupes = {}

    for doc in docs:
        d = doc.to_dict()
        if not d:
            continue

        nom = d.get("nom", "Inconnu")

        if search:
            s = search.lower()
            if s not in nom.lower() \
            and s not in d.get("texte", "").lower() \
            and s not in d.get("reponse", "").lower():
                continue

        groupes.setdefault(nom, []).append(d)

    # =========================
    # DISPLAY
    # =========================
    if not groupes:
        st.info("Aucune conversation")
    else:
        for nom, convs in sorted(groupes.items(), key=lambda x: len(x[1]), reverse=True):

            with st.expander(f"👤 {nom} ({len(convs)})"):

                for c in convs:
                    st.markdown(f"❓ **Utilisateur :** {c.get('texte','')}")
                    st.markdown(f"🤖 **Hartur :** {c.get('reponse','')}")
                    st.divider()
