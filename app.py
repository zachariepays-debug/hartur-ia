import streamlit as st
import pandas as pd
import requests
import base64
import json
from io import StringIO
from datetime import datetime

# --- CONFIGURATION ---
REPO_NOM = "zachariepays-debug/Hartur-ia" 
FICHIER_COMPTES = "comptes.csv"
FICHIER_CHATS = "conversations.json"
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
MASTER_CODE = "babar"

st.set_page_config(page_title="HARTUR | OS", layout="wide", page_icon="💀")

# --- FONCTIONS GITHUB (CORRIGÉES) ---
def github_fetch(chemin):
    url = f"https://api.github.com/repos/{REPO_NOM}/contents/{chemin}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        j = r.json()
        return base64.b64decode(j['content']).decode('utf-8'), j['sha']
    return None, None

def github_push(chemin, contenu, msg, sha=None):
    url = f"https://api.github.com/repos/{REPO_NOM}/contents/{chemin}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    data = {"message": msg, "content": base64.b64encode(contenu.encode('utf-8')).decode('utf-8')}
    if sha: data["sha"] = sha
    requests.put(url, headers=headers, data=json.dumps(data))

# --- INITIALISATION ---
if "user" not in st.session_state: st.session_state.user = None
if "admin_mode" not in st.session_state: st.session_state.admin_mode = False
if "msgs" not in st.session_state: st.session_state.msgs = []
if "system_active" not in st.session_state: st.session_state.system_active = True

# --- ÉCRAN NOIR (KILL SWITCH) ---
if not st.session_state.system_active:
    st.markdown("<style>.stApp { background-color: black !important; }</style>", unsafe_allow_html=True)
    st.markdown("<div style='text-align:center; color:white; margin-top:30vh;'><h1>REOUVRIR HARTUR</h1>", unsafe_allow_html=True)
    unlock = st.text_input("Code Système", type="password", label_visibility="collapsed")
    if unlock == MASTER_CODE:
        st.session_state.system_active = True
        st.rerun()
    st.stop()

# --- DESIGN HARTUR FLASHY ---
st.markdown("""
    <style>
    .stApp { background-color: #030507; color: white; }
    header { visibility: hidden; }
    .giant-title { font-size: 70px; font-weight: 900; letter-spacing: 15px; text-align: center; color: white; margin-bottom: 0; }
    .signature-zac { color: #ff4b4b; text-align: center; font-weight: 900; letter-spacing: 5px; font-size: 14px; margin-bottom: 30px; }
    </style>
    """, unsafe_allow_html=True)

# --- NAVIGATION ---

# 1. MODE ADMIN (ACCÈS DIRECT PAR 6/6 OU BOUTON)
if st.session_state.admin_mode:
    st.title("🛠️ PANNEAU DE CONTRÔLE ADMIN")
    if st.button("🔴 ÉTEINDRE HARTUR"):
        st.session_state.system_active = False
        st.rerun()
    
    if st.button("QUITTER ADMIN"): 
        st.session_state.admin_mode = False
        st.rerun()

    tab1, tab2 = st.tabs(["📁 COMPTES", "📜 CONVERSATIONS"])
    
    with tab1:
        raw_u, _ = github_fetch(FICHIER_COMPTES)
        if raw_u:
            df_u = pd.read_csv(StringIO(raw_u))
            st.dataframe(df_u, use_container_width=True)
            st.download_button("Télécharger Comptes", raw_u, "comptes.csv")

    with tab2:
        raw_c, _ = github_fetch(FICHIER_CHATS)
        if raw_c:
            convs = json.loads(raw_c)
            target = st.selectbox("Voir la discussion de :", list(convs.keys()))
            if target:
                # Plus récent en haut
                for m in convs[target][::-1]:
                    role = "👤 USER" if m['role'] == 'user' else "💀 HARTUR"
                    st.text_area(f"{role}", m['content'], height=80)
                st.download_button(f"Télécharger {target}", json.dumps(convs[target]), f"{target}.json")

# 2. ESPACE CHAT (PERSONNALITÉ ACCRO)
elif st.session_state.user:
    st.markdown("<h2 style='text-align:center;'>HARTUR</h2>", unsafe_allow_html=True)
    if st.sidebar.button("Déconnexion"): st.session_state.user = None; st.rerun()

    for m in st.session_state.msgs:
        with st.chat_message(m["role"]): st.write(m["content"])

    if prompt := st.chat_input("Parle-moi..."):
        st.session_state.msgs.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.write(prompt)
        
        with st.chat_message("assistant"):
            # Personnalité de pote
            reponse = f"Écoute mon pote, tu me dis '{prompt}'. Si je suis honnête avec toi..."
            st.write(reponse)
            st.session_state.msgs.append({"role": "assistant", "content": reponse})
            
        # Sauvegarde GitHub
        raw, sha = github_fetch(FICHIER_CHATS)
        data = json.loads(raw) if raw else {}
        data[st.session_state.user] = st.session_state.msgs
        github_push(FICHIER_CHATS, json.dumps(data), f"Update {st.session_state.user}", sha)

# 3. ACCUEIL (CONNEXION)
else:
    st.markdown('<h1 class="giant-title">HARTUR</h1>', unsafe_allow_html=True)
    st.markdown('<p class="signature-zac">CRÉÉ PAR ZACMITE</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        t1, t2 = st.tabs(["CONNEXION", "S'INSCRIRE"])
        with t1:
            u = st.text_input("Pseudo")
            p = st.text_input("Mot de passe", type="password")
            if st.button("ENTRER"):
                # RACCOURCI SECRET ADMIN
                if u == "6" and p == "6":
                    st.session_state.admin_mode = True
                    st.rerun()
                
                raw, _ = github_fetch(FICHIER_COMPTES)
                df = pd.read_csv(StringIO(raw)) if raw else pd.DataFrame(columns=["pseudo", "password"])
                if not df[(df['pseudo'] == u) & (df['password'] == p)].empty:
                    st.session_state.user = u
                    # Récupérer historique
                    raw_c, _ = github_fetch(FICHIER_CHATS)
                    if raw_c: st.session_state.msgs = json.loads(raw_c).get(u, [])
                    st.rerun()
                else: st.error("Accès refusé.")
        with t2:
            nu = st.text_input("Nouveau Pseudo")
            np = st.text_input("Nouveau MDP", type="password")
            if st.button("CRÉER COMPTE"):
                raw, sha = github_fetch(FICHIER_COMPTES)
                df = pd.read_csv(StringIO(raw)) if raw else pd.DataFrame(columns=["pseudo", "password"])
                if nu and np and nu not in df['pseudo'].values:
                    new_df = pd.concat([df, pd.DataFrame({"pseudo":[nu], "password":[np]})])
                    github_push(FICHIER_COMPTES, new_df.to_csv(index=False), f"Inscrit: {nu}", sha)
                    st.success("Compte validé !")
