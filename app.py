import streamlit as st
import os
import requests
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# ======================================================
# ⚙️ CONFIG ET CONNEXIONS
# ======================================================
st.set_page_config(page_title="Hartur IA", page_icon="🤖", layout="wide")

# Connexion Firebase pour l'Admin
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate('arthure-ia-firebase-adminsdk-fbsvc-8c2d7737ee.json')
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"Erreur Firebase : {e}")

db = firestore.client()
api_key = st.secrets.get("MISTRAL_KEY")

# ======================================================
# 💾 SESSION STATE (Initialisation)
# ======================================================
if "page" not in st.session_state: st.session_state.page = "home"
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "username" not in st.session_state: st.session_state.username = None
if "messages" not in st.session_state: st.session_state.messages = []
if "humeur" not in st.session_state: st.session_state.humeur = "Cool"

# ======================================================
# 📁 GESTION COMPTES LOCAUX
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
# 🧠 IA LOGIQUE (RÉPONSE DIRECTE ET FLUIDE)
# ======================================================
def generer_reponse(prompt):
    if not api_key:
        return "⚠️ Erreur : Clé Mistral non configurée."

    # Instructions pour forcer la fluidité et éviter les analyses robotiques
    instructions = {
        "Cool": "Tu es Hartur, un ado cool. Réponds directement, sans faire de listes, sois bref et amical. Tutoie.",
        "Drôle": "Sois super drôle, utilise des emojis et réponds de façon spontanée.",
        "Sérieux": "Réponds de manière concise et pro, sans fioritures.",
        "Sarcastique": "Réponds avec ironie, sois un peu piquant mais reste fluide.",
        "Raisonnement complexe": "Réponds intelligemment mais sous forme de paragraphe fluide, pas de listes numérotées."
    }
    
    system_content = instructions.get(st.session_state.humeur, "Tu es Hartur.")

    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}"}
    data = {
        "model": "open-mistral-7b",
        "messages": [
            {"role": "system", "content": system_content},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7 
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=12)
        return response.json()['choices'][0]['message']['content']
    except:
        return "Petit bug réseau, on peut recommencer ?"

# ======================================================
# 🏠 NAVIGATION
# ======================================================
col1, col2 = st.columns([9, 1])
with col2:
    if st.button("🔐 Admin"):
        st.session_state.page = "admin"
        st.rerun()

if st.session_state.page == "home":
    st.title("🤖 Hartur IA")
    st.info("IA fluide | Comptes locaux | Sauvegarde Firebase")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🔑 Connexion"): st.session_state.page = "login"; st.rerun()
    with c2:
        if st.button("🆕 Créer compte"): st.session_state.page = "signup"; st.rerun()

elif st.session_state.page == "signup":
    u = st.text_input("Choisis un identifiant")
    p = st.text_input("Choisis un mot de passe", type="password")
    if st.button("Créer le compte"):
        if create_account(u, p):
            st.success("Compte créé !")
            st.session_state.page = "login"
            st.rerun()
        else: st.error("Nom déjà utilisé.")
    if st.button("Retour"): st.session_state.page = "home"; st.rerun()

elif st.session_state.page == "login":
    u = st.text_input("Identifiant")
    p = st.text_input("Mot de passe", type="password")
    if st.button("Se connecter"):
        if login_account(u, p):
            st.session_state.logged_in = True
            st.session_state.username = u
            st.session_state.page = "chat"
            st.rerun()
        else: st.error("Identifiants incorrects.")
    if st.button("Retour"): st.session_state.page = "home"; st.rerun()

# ======================================================
# 💬 CHAT (FLUIDE ET SAUVEGARDÉ)
# ======================================================
elif st.session_state.page == "chat":
    st.title(f"🤖 Hartur")
    st.sidebar.write(f"Utilisateur : **{st.session_state.username}**")
    
    st.session_state.humeur = st.sidebar.selectbox(
        "Humeur de l'IA", ["Cool", "Drôle", "Sérieux", "Sarcastique", "Raisonnement complexe"]
    )

    # Affichage de la discussion
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    prompt = st.chat_input("Dis un truc...")
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
                "date": datetime.utcnow()
            })
        except: pass

    if st.sidebar.button("Déconnexion"):
        st.session_state.logged_in = False
        st.session_state.messages = []
        st.session_state.page = "home"
        st.rerun()

# ======================================================
# 🔐 ADMIN (VUE PAR UTILISATEUR)
# ======================================================
elif st.session_state.page == "admin":
    st.title("🔐 Admin Panel")
    if st.text_input("Mot de passe", type="password") == "babar":
        st.success("Accès autorisé")
        
        # Récupération des données Firebase
        docs = list(db.collection("discussions").order_by("date", direction=firestore.Query.DESCENDING).stream())
        convs = {}
        for d in docs:
            data = d.to_dict()
            u = data.get("nom", "Inconnu")
            if u not in convs: convs[u] = []
            convs[u].append(data)
        
        for user, messages in convs.items():
            with st.expander(f"👤 Conversation de {user}"):
                for m in messages:
                    st.write(f"**Lui:** {m.get('texte')}")
                    st.write(f"**Hartur:** {m.get('reponse')}")
                    st.divider()

    if st.button("⬅ Retour"):
        st.session_state.page = "home"
        st.rerun()
