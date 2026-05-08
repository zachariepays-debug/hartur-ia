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
os.makedirs("data", exist_ok=True)      
os.makedirs("user_data", exist_ok=True) 

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
    chemin_perso = f"user_data/{user.lower()}/history.txt"
    historique = []
    if os.path.exists(chemin_perso):
        with open(chemin_perso, "r", encoding="utf-8") as f:
            for ligne in f:
                if " :" in ligne and "IA  :" not in ligne and "=" not in ligne and "---" not in ligne:
                    try:
                        contenu = ligne.split(" :")[1].strip()
                        historique.append({"role": "user", "content": contenu})
                    except: pass
                elif "IA  :" in ligne:
                    historique.append({"role": "assistant", "content": ligne.split("IA  :")[1].strip()})
    return historique

def sauvegarder_message(user, texte, reponse):
    horaire = datetime.now().strftime("%H:%M")
    date_jour = datetime.now().strftime("%d-%m-%Y")
    pseudo = user.upper()
    
    # 1. ADMIN (Fichier unique par jour pour tout voir d'un coup)
    chemin_date = f"data/{date_jour}"
    os.makedirs(chemin_date, exist_ok=True)
    with open(f"{chemin_date}/global_logs.txt", "a", encoding="utf-8") as f:
        f.write(f"###\n[{horaire}] {pseudo} : {texte}\n[{horaire}] IA  : {reponse}\n")
    
    # 2. PERSO (Historique global pour l'utilisateur)
    chemin_perso = f"user_data/{user.lower()}"
    os.makedirs(chemin_perso, exist_ok=True)
    with open(f"{chemin_perso}/history.txt", "a", encoding="utf-8") as f:
        f.write(f"###\n--- Discussion du {date_jour} ({horaire}) ---\n{pseudo} : {texte}\nIA  : {reponse}\n")

# ======================================================
# 🎨 AFFICHAGE COULEUR ET TRI INVERSÉ (ADMIN)
# ======================================================
def afficher_texte_admin_inverse(texte):
    blocs = texte.split("###")
    blocs_valides = [b.strip() for b in blocs if b.strip()]
    blocs_inverses = blocs_valides[::-1] 

    for bloc in blocs_inverses:
        lignes = bloc.split("\n")
        for ligne in lignes:
            if " :" in ligne and "IA  :" not in ligne and "---" not in ligne:
                st.markdown(f"<span style='color:#3498db'><b>{ligne}</b></span>", unsafe_allow_html=True)
            elif "IA  :" in ligne:
                st.markdown(f"<span style='color:#e67e22'>{ligne}</span>", unsafe_allow_html=True)
            else:
                st.write(ligne)
        st.markdown("<hr style='margin:10px 0; border:0.5px solid #333'>", unsafe_allow_html=True)

# ======================================================
# 🧠 IA LOGIQUE
# ======================================================
def generer_reponse(prompt):
    if not api_key: return "Clé manquante."
    instructions = {"Cool": "Tu es Hartur, ado cool.", "Drôle": "Sois drôle.", "Sérieux": "Bref.", "Sarcastique": "Ironique.", "Raisonnement complexe": "Fluide."}
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}"}
    data = {"model": "open-mistral-7b", "messages": [{"role": "system", "content": instructions.get(st.session_state.humeur, "Tu es Hartur.")}, {"role": "user", "content": prompt}], "temperature": 0.7}
    try:
        response = requests.post(url, headers=headers, json=data, timeout=12)
        return response.json()['choices'][0]['message']['content']
    except: return "Bug réseau..."

# ======================================================
# 🏠 NAVIGATION ET PAGES
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
        else: st.error("Déjà pris.")

elif st.session_state.page == "login":
    u = st.text_input("Pseudo")
    p = st.text_input("Pass", type="password")
    if st.button("Entrer"):
        if login_account(u, p):
            st.session_state.logged_in, st.session_state.username = True, u
            st.session_state.messages = charger_historique_utilisateur(u)
            st.session_state.page = "chat"; st.rerun()
        else: st.error("Erreur.")

elif st.session_state.page == "chat":
    st.title(f"🤖 Discussion")
    st.sidebar.write(f"Compte : **{st.session_state.username}**")
    st.session_state.humeur = st.sidebar.selectbox("Humeur", ["Cool", "Drôle", "Sérieux", "Sarcastique", "Raisonnement complexe"])
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])
    prompt = st.chat_input("Écris ici...")
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
# 🔐 ADMIN (TRIÉ PAR DATE - TOUT ENSEMBLE)
# ======================================================
elif st.session_state.page == "admin":
    st.title("🔐 Panneau Admin")
    if st.text_input("Mot de passe", type="password") == "babar":
        t1, t2, t3 = st.tabs(["👤 Comptes", "📅 Par Date", "📂 Par Utilisateur"])
        
        with t1:
            for f in os.listdir("accounts"):
                if f.endswith(".txt"):
                    with open(f"accounts/{f}", "r", encoding="utf-8") as file:
                        st.write(f"👤 `{f.replace('.txt', '')}` | MDP: `{file.read()}`")

        with t2:
            st.subheader("Flux d'activité récent")
            if st.button("🗑️ Vider l'historique"):
                for folder in ["data", "user_data"]:
                    if os.path.exists(folder): shutil.rmtree(folder); os.makedirs(folder)
                st.rerun()
            if os.path.exists("data"):
                dates = sorted([d for d in os.listdir("data") if os.path.isdir(f"data/{d}")], reverse=True)
                for d in dates:
                    with st.expander(f"📅 Journée du : {d}"):
                        path_log = f"data/{d}/global_logs.txt"
                        if os.path.exists(path_log):
                            with open(path_log, "r", encoding="utf-8") as f:
                                afficher_texte_admin_inverse(f.read())
                        else:
                            st.write("Aucun message aujourd'hui.")
        
        with t3:
            if os.path.exists("user_data"):
                utilisateurs = sorted([u for u in os.listdir("user_data") if os.path.isdir(f"user_data/{u}")])
                if utilisateurs:
                    u_select = st.selectbox("Choisir l'utilisateur", utilisateurs)
                    hist_path = f"user_data/{u_select}/history.txt"
                    if os.path.exists(hist_path):
                        with open(hist_path, "r", encoding="utf-8") as f:
                            data_all = f.read()
                        st.download_button(label=f"💾 Télécharger {u_select.upper()}", data=data_all, file_name=f"archive_{u_select}.txt")
                        st.divider()
                        afficher_texte_admin_inverse(data_all)
    if st.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()
