import streamlit as st
import os
import requests
import shutil
from datetime import datetime

# ======================================================
# ⚙️ CONFIGURATION
# ======================================================
st.set_page_config(page_title="Hartur IA", page_icon="🤖", layout="wide")
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
# 📁 GESTION DES DOSSIERS
# ======================================================
os.makedirs("accounts", exist_ok=True)
os.makedirs("data", exist_ok=True)      # Pour l'admin (par date)
os.makedirs("user_data", exist_ok=True) # Pour l'utilisateur (historique permanent)

def create_account(user, pwd):
    file = f"accounts/{user.lower()}.txt"
    if os.path.exists(file): return False
    with open(file, "w", encoding="utf-8") as f: f.write(pwd)
    return True

def login_account(user, pwd):
    file = f"accounts/{user.lower()}.txt"
    if not os.path.exists(file): return False
    with open(file, "r", encoding="utf-8") as f: return f.read().strip() == pwd

def charger_historique_utilisateur(user):
    """Charge l'historique complet depuis le dossier personnel de l'utilisateur"""
    chemin_perso = f"user_data/{user.lower()}/history.txt"
    historique = []
    if os.path.exists(chemin_perso):
        with open(chemin_perso, "r", encoding="utf-8") as f:
            for ligne in f:
                if "LUI :" in ligne:
                    historique.append({"role": "user", "content": ligne.split("LUI :")[1].strip()})
                elif "IA  :" in ligne:
                    historique.append({"role": "assistant", "content": ligne.split("IA  :")[1].strip()})
    return historique

def sauvegarder_message(user, texte, reponse):
    horaire = datetime.now().strftime("%H:%M")
    date_jour = datetime.now().strftime("%d-%m-%Y")
    
    # 1. Sauvegarde pour l'ADMIN (par date)
    chemin_admin = f"data/{date_jour}/{user.lower()}"
    os.makedirs(chemin_admin, exist_ok=True)
    with open(f"{chemin_admin}/conversation.txt", "a", encoding="utf-8") as f:
        f.write(f"[{horaire}] LUI : {texte}\n[{horaire}] IA  : {reponse}\n" + "-"*30 + "\n")
    
    # 2. Sauvegarde pour l'UTILISATEUR (historique global)
    chemin_perso = f"user_data/{user.lower()}"
    os.makedirs(chemin_perso, exist_ok=True)
    with open(f"{chemin_perso}/history.txt", "a", encoding="utf-8") as f:
        f.write(f"LUI : {texte}\nIA  : {reponse}\n")

# ======================================================
# 🧠 IA LOGIQUE
# ======================================================
def generer_reponse(prompt):
    if not api_key: return "Clé manquante."
    instructions = {"Cool": "Tu es Hartur, un ado cool. Réponds direct, tutoie.", "Drôle": "Sois drôle.", "Sérieux": "Sois bref.", "Sarcastique": "Sois ironique.", "Raisonnement complexe": "Sois fluide."}
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}"}
    data = {"model": "open-mistral-7b", "messages": [{"role": "system", "content": instructions.get(st.session_state.humeur, "Tu es Hartur.")}, {"role": "user", "content": prompt}], "temperature": 0.7}
    try:
        response = requests.post(url, headers=headers, json=data, timeout=12)
        return response.json()['choices'][0]['message']['content']
    except: return "Bug réseau..."

# ======================================================
# 🏠 NAVIGATION
# ======================================================
col1, col2 = st.columns([9, 1])
with col2:
    if st.button("🔐 Admin"): st.session_state.page = "admin"; st.rerun()

if st.session_state.page == "home":
    st.title("🤖 Hartur IA")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🔑 Connexion"): st.session_state.page = "login"; st.rerun()
    with c2:
        if st.button("🆕 Créer compte"): st.session_state.page = "signup"; st.rerun()

elif st.session_state.page == "signup":
    u = st.text_input("Pseudo")
    p = st.text_input("Pass", type="password")
    if st.button("Créer"):
        if create_account(u, p): st.session_state.page = "login"; st.rerun()
        else: st.error("Pseudo déjà pris.")

elif st.session_state.page == "login":
    u = st.text_input("Pseudo")
    p = st.text_input("Pass", type="password")
    if st.button("Entrer"):
        if login_account(u, p):
            st.session_state.logged_in, st.session_state.username = True, u
            st.session_state.messages = charger_historique_utilisateur(u)
            st.session_state.page = "chat"; st.rerun()
        else: st.error("Identifiants incorrects.")

elif st.session_state.page == "chat":
    st.title(f"🤖 Chat")
    st.sidebar.write(f"Compte : **{st.session_state.username}**")
    st.session_state.humeur = st.sidebar.selectbox("Mood", ["Cool", "Drôle", "Sérieux", "Sarcastique", "Raisonnement complexe"])
    
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    prompt = st.chat_input("Dis un truc...")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        reponse = generer_reponse(prompt)
        st.session_state.messages.append({"role": "assistant", "content": reponse})
        with st.chat_message("assistant"): st.markdown(reponse)
        sauvegarder_message(st.session_state.username, prompt, reponse)

    if st.sidebar.button("Déconnexion"):
        st.session_state.logged_in, st.session_state.messages, st.session_state.page = False, [], "home"
        st.rerun()

# ======================================================
# 🔐 ADMIN (Double Historique)
# ======================================================
elif st.session_state.page == "admin":
    st.title("🔐 Panneau Admin")
    if st.text_input("Mot de passe maître", type="password") == "babar":
        t1, t2, t3 = st.tabs(["👤 Comptes", "📅 Par Date", "📂 Par Utilisateur"])
        
        with t1:
            for f in os.listdir("accounts"):
                with open(f"accounts/{f}", "r") as file:
                    st.write(f"👤 `{f.replace('.txt', '')}` | MDP: `{file.read()}`")

        with t2:
            if st.button("🗑️ Vider l'historique complet"):
                for folder in ["data", "user_data"]:
                    if os.path.exists(folder): shutil.rmtree(folder); os.makedirs(folder)
                st.rerun()
            dates = sorted([d for d in os.listdir("data") if os.path.isdir(f"data/{d}")], reverse=True)
            for d in dates:
                with st.expander(f"📅 Date : {d}"):
                    for u in os.listdir(f"data/{d}"):
                        st.write(f"**Utilisateur : {u.upper()}**")
                        with open(f"data/{d}/{u}/conversation.txt", "r", encoding="utf-8") as f: st.text(f.read())
        
        with t3:
            st.subheader("Historique complet par personne")
            users = [u for u in os.listdir("user_data") if os.path.isdir(f"user_data/{u}")]
            for u in users:
                with st.expander(f"👤 Historique de {u.upper()}"):
                    with open(f"user_data/{u}/history.txt", "r", encoding="utf-8") as f:
                        st.text(f.read())

    if st.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()
