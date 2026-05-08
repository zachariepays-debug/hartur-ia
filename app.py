import streamlit as st
import os
import requests
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# ======================================================
# ⚙️ CONFIGURATION ET CONNEXION
# ======================================================
st.set_page_config(page_title="Hartur IA", page_icon="🤖", layout="wide")

# --- Initialisation Firebase ---
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate('arthure-ia-firebase-adminsdk-fbsvc-8c2d7737ee.json')
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"Erreur Firebase : {e}")

db = firestore.client()

# --- Récupération Clé Mistral ---
api_key = st.secrets.get("MISTRAL_KEY")

# ======================================================
# 💾 SESSION STATE
# ======================================================
states = {
    "page": "home",
    "logged_in": False,
    "username": None,
    "messages": [],
    "nom_ia": "Hartur",
    "humeur": "Cool",
    "selected_user": None
}
for key, value in states.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ======================================================
# 📁 GESTION DES COMPTES (Local)
# ======================================================
os.makedirs("accounts", exist_ok=True)

def create_account(user, pwd):
    file = f"accounts/{user.lower()}.txt"
    if os.path.exists(file): return False
    with open(file, "w") as f: f.write(pwd)
    return True

def login_account(user, pwd):
    file = f"accounts/{user.lower()}.txt"
    if not os.path.exists(file): return False
    with open(file, "r") as f: return f.read() == pwd

# ======================================================
# 🧠 LOGIQUE IA (MISTRAL)
# ======================================================
def generer_reponse(prompt):
    if not api_key:
        return "⚠️ Erreur : Clé Mistral manquante dans les Secrets."

    # Adaptation du comportement selon l'humeur choisie
    instructions = {
        "Cool": "Tu es Hartur, un ado cool et détendu. Tutoie l'utilisateur.",
        "Drôle": "Tu es un humoriste qui fait beaucoup de blagues et utilise des emojis.",
        "Sérieux": "Tu es un expert formel, très précis et professionnel.",
        "Sarcastique": "Tu es très sarcastique, tu te moques gentiment de l'utilisateur.",
        "Raisonnement complexe": "Analyse la question étape par étape avec une logique scientifique."
    }
    
    system_prompt = instructions.get(st.session_state.humeur, "Tu es Hartur.")

    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}"}
    data = {
        "model": "open-mistral-7b",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
    }
    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        return response.json()['choices'][0]['message']['content']
    except:
        return "Désolé, Hartur a un petit bug de connexion là... 🔌"

# ======================================================
# 🏠 NAVIGATION / UI
# ======================================================
col1, col2 = st.columns([9, 1])
with col2:
    if st.button("🔐 Admin"):
        st.session_state.page = "admin"
        st.rerun()

# --- PAGES ---
if st.session_state.page == "home":
    st.title("🤖 Hartur IA")
    st.info("✔ IA Intelligente | ✔ Comptes Sécurisés | ✔ Admin Dashboard")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🔑 Connexion"):
            st.session_state.page = "login"
            st.rerun()
    with c2:
        if st.button("🆕 Créer compte"):
            st.session_state.page = "signup"
            st.rerun()

elif st.session_state.page == "signup":
    st.subheader("🆕 Créer un compte")
    u = st.text_input("Identifiant")
    p = st.text_input("Mot de passe", type="password")
    if st.button("Valider"):
        if create_account(u, p):
            st.success("Compte créé ! Connecte-toi.")
            st.session_state.page = "login"
            st.rerun()
        else: st.error("Nom déjà pris.")
    if st.button("Retour"):
        st.session_state.page = "home"
        st.rerun()

elif st.session_state.page == "login":
    st.subheader("🔑 Connexion")
    u = st.text_input("Identifiant")
    p = st.text_input("Mot de passe", type="password")
    if st.button("Entrer"):
        if login_account(u, p):
            st.session_state.logged_in = True
            st.session_state.username = u
            st.session_state.page = "chat"
            st.rerun()
        else: st.error("Identifiants incorrects.")
    if st.button("Retour"):
        st.session_state.page = "home"
        st.rerun()

# ======================================================
# 💬 CHAT (Avec sauvegarde Firebase)
# ======================================================
elif st.session_state.page == "chat" and st.session_state.logged_in:
    st.title(f"🤖 {st.session_state.nom_ia}")
    st.sidebar.success(f"👤 {st.session_state.username}")
    
    # Paramètres IA
    st.session_state.humeur = st.sidebar.selectbox(
        "Humeur IA", ["Cool", "Drôle", "Sérieux", "Sarcastique", "Raisonnement complexe"]
    )
    
    # Affichage historique
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    prompt = st.chat_input("Dis un truc à Hartur...")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        reponse = generer_reponse(prompt)
        
        st.session_state.messages.append({"role": "assistant", "content": reponse})
        with st.chat_message("assistant"): st.markdown(reponse)

        # 💾 SAUVEGARDE FIREBASE
        try:
            db.collection("discussions").add({
                "nom": st.session_state.username,
                "texte": prompt,
                "reponse": reponse,
                "humeur": st.session_state.humeur,
                "date": datetime.utcnow()
            })
        except: pass

    if st.sidebar.button("Déconnexion"):
        st.session_state.logged_in = False
        st.session_state.messages = []
        st.session_state.page = "home"
        st.rerun()

# ======================================================
# 🔐 ADMIN DASHBOARD (Lecture Firebase)
# ======================================================
elif st.session_state.page == "admin":
    st.title("🔐 Panneau de contrôle")
    mdp = st.text_input("Code secret", type="password")
    
    if mdp == "babar":
        menu = st.radio("Voir :", ["👤 Comptes Locaux", "💬 Conversations Firebase"])
        
        if menu == "👤 Comptes Locaux":
            for f in os.listdir("accounts"):
                st.write(f"✅ {f.replace('.txt', '')}")
        
        else:
            docs = list(db.collection("discussions").order_by("date", direction=firestore.Query.DESCENDING).stream())
            convs = {}
            for d in docs:
                data = d.to_dict()
                u = data.get("nom", "Anonyme")
                if u not in convs: convs[u] = []
                convs[u].append(data)
            
            for user, msgs in convs.items():
                with st.expander(f"👤 {user}"):
                    for m in msgs:
                        st.write(f"**Lui:** {m.get('texte')}")
                        st.write(f"**Hartur ({m.get('humeur')}):** {m.get('reponse')}")
                        st.divider()

    if st.button("⬅ Retour"):
        st.session_state.page = "home"
        st.rerun()
