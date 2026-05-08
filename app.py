import streamlit as st
import os
import requests
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# ======================================================
# ⚙️ CONFIGURATION & CONNEXIONS
# ======================================================
st.set_page_config(page_title="Hartur IA", page_icon="🤖", layout="wide")

# Initialisation Firebase
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate('arthure-ia-firebase-adminsdk-fbsvc-8c2d7737ee.json')
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"Erreur Firebase : {e}")

db = firestore.client()
api_key = st.secrets.get("MISTRAL_KEY")

# ======================================================
# 💾 SESSION STATE
# ======================================================
if "page" not in st.session_state: st.session_state.page = "home"
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "username" not in st.session_state: st.session_state.username = None
if "messages" not in st.session_state: st.session_state.messages = []
if "humeur" not in st.session_state: st.session_state.humeur = "Cool"

# ======================================================
# 📁 GESTION COMPTES (Local)
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
# 🧠 IA LOGIQUE (Fluide)
# ======================================================
def generer_reponse(prompt):
    if not api_key: return "Clé API manquante."
    
    instructions = {
        "Cool": "Tu es Hartur, un ado cool. Réponds directement, sois bref et tutoie.",
        "Drôle": "Sois drôle, utilise des emojis et réponds de façon vive.",
        "Sérieux": "Réponds de manière concise et pro.",
        "Sarcastique": "Sois ironique et un peu piquant.",
        "Raisonnement complexe": "Réponds avec intelligence mais reste fluide."
    }
    
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}"}
    data = {
        "model": "open-mistral-7b",
        "messages": [
            {"role": "system", "content": instructions.get(st.session_state.humeur, "Tu es Hartur.")},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }
    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        return response.json()['choices'][0]['message']['content']
    except:
        return "Désolé, petit bug réseau..."

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
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🔑 Connexion"): st.session_state.page = "login"; st.rerun()
    with c2:
        if st.button("🆕 Créer compte"): st.session_state.page = "signup"; st.rerun()

elif st.session_state.page == "signup":
    u = st.text_input("Identifiant")
    p = st.text_input("Mot de passe", type="password")
    if st.button("Créer"):
        if create_account(u, p): st.session_state.page = "login"; st.rerun()
        else: st.error("Nom déjà pris.")
    if st.button("Retour"): st.session_state.page = "home"; st.rerun()

elif st.session_state.page == "login":
    u = st.text_input("Identifiant")
    p = st.text_input("Mot de passe", type="password")
    if st.button("Entrer"):
        if login_account(u, p):
            st.session_state.logged_in = True
            st.session_state.username = u
            st.session_state.page = "chat"
            st.rerun()
        else: st.error("Erreur login.")
    if st.button("Retour"): st.session_state.page = "home"; st.rerun()

# ======================================================
# 💬 CHAT
# ======================================================
elif st.session_state.page == "chat":
    st.title(f"🤖 Hartur")
    st.sidebar.selectbox("Humeur", ["Cool", "Drôle", "Sérieux", "Sarcastique"], key="humeur")
    
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    prompt = st.chat_input("Écris ici...")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        reponse = generer_reponse(prompt)
        st.session_state.messages.append({"role": "assistant", "content": reponse})
        with st.chat_message("assistant"): st.markdown(reponse)

        # SAUVEGARDE FIREBASE
        try:
            db.collection("discussions").add({
                "nom": st.session_state.username,
                "texte": prompt,
                "reponse": reponse,
                "date": datetime.utcnow()
            })
        except: pass

# ======================================================
# 🔐 ADMIN (Réparé comme avant)
# ======================================================
elif st.session_state.page == "admin":
    st.title("🔐 Panneau Admin")
    
    if st.text_input("Mot de passe", type="password") == "babar":
        st.success("Accès autorisé")
        
        # Récupération et tri par utilisateur
        try:
            docs = list(db.collection("discussions").order_by("date", direction=firestore.Query.DESCENDING).stream())
            convs = {}
            for d in docs:
                data = d.to_dict()
                u = data.get("nom", "Inconnu")
                if u not in convs: convs[u] = []
                convs[u].append(data)
            
            st.subheader("📂 Conversations sauvegardées")
            for user, msgs in convs.items():
                with st.expander(f"👤 {user} ({len(msgs)} messages)"):
                    for m in msgs:
                        st.write(f"💬 **Lui:** {m.get('texte')}")
                        st.write(f"🤖 **IA:** {m.get('reponse')}")
                        st.caption(f"Le {m.get('date')}")
                        st.divider()
        except Exception as e:
            st.error(f"Erreur Firebase : {e}")

    if st.button("⬅ Retour"):
        st.session_state.page = "home"
        st.rerun()
