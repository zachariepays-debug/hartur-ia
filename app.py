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

# --- FONCTIONS GITHUB (SÉCURISÉES) ---
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

# --- LOGIQUE KILL SWITCH (ÉTAT GLOBAL) ---
# On simule l'état système (tu peux le stocker sur GitHub pour qu'il soit réel)
if "system_active" not in st.session_state: st.session_state.system_active = True

# --- ÉCRAN NOIR (SYSTÈME ÉTEINT) ---
if not st.session_state.system_active:
    st.markdown("""<style>.stApp { background-color: black; color: white; }</style>""", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align:center; margin-top:20vh;'>SYSTÈME HARTUR HORS TENSION</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;'>REOUVRIR HARTUR</p>", unsafe_allow_html=True)
    unlock = st.text_input("Code de réactivation", type="password", label_visibility="collapsed")
    if unlock == MASTER_CODE:
        st.session_state.system_active = True
        st.rerun()
    st.stop()

# --- DESIGN CSS CUSTOM ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #030507; color: white; }}
    header {{ visibility: hidden; }}
    .giant-title {{ font-size: 70px; font-weight: 900; letter-spacing: 15px; text-align: center; color: white; margin: 0; }}
    .signature-zac {{ color: #ff4b4b; text-align: center; font-weight: 900; letter-spacing: 5px; font-size: 14px; margin-bottom: 30px; }}
    .admin-trigger {{ position: fixed; top: 10px; right: 10px; z-index: 999; cursor: pointer; }}
    </style>
    """, unsafe_allow_html=True)

# --- BOUTON ADMIN (DISCRET) ---
st.markdown('<div class="admin-trigger">', unsafe_allow_html=True)
if st.button("⚙️"):
    st.session_state.show_admin_login = not st.session_state.get("show_admin_login", False)
st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.get("show_admin_login"):
    with st.sidebar:
        st.title("🛡️ ZONE CORE")
        code = st.text_input("Code Maître", type="password")
        if code == MASTER_CODE:
            st.session_state.admin_mode = True
            st.success("God Mode Activé")

# --- NAVIGATION ---

# 1. MODE ADMIN (COMPTES ET DISCUSSIONS)
if st.session_state.admin_mode:
    st.title("🛠️ PANNEAU DE CONTRÔLE ADMIN")
    if st.button("QUITTER ADMIN"): st.session_state.admin_mode = False; st.rerun()
    
    if st.button("🔴 ÉTEINDRE TOUT LE SYSTÈME"):
        st.session_state.system_active = False
        st.rerun()

    tab1, tab2 = st.tabs(["📁 DOSSIER COMPTES", "📜 DOSSIER CONVERSATIONS"])
    
    with tab1:
        raw_u, _ = github_fetch(FICHIER_COMPTES)
        if raw_u:
            df_u = pd.read_csv(StringIO(raw_u))
            st.dataframe(df_u, use_container_width=True)
            st.download_button("Télécharger CSV Comptes", raw_u, "comptes_hartur.csv")

    with tab2:
        raw_c, _ = github_fetch(FICHIER_CHATS)
        if raw_c:
            convs = json.loads(raw_c)
            target = st.selectbox("Sélectionner un utilisateur", list(convs.keys()))
            if target:
                user_msgs = convs[target][::-1] # Dernier message en haut
                for m in user_msgs:
                    role = "👤 UTILISATEUR" if m['role'] == 'user' else "💀 HARTUR"
                    st.text_area(f"{role} ({m.get('time', 'Ancien')})", m['content'], height=100)
                st.download_button(f"Télécharger conversation de {target}", json.dumps(user_msgs), f"chat_{target}.json")

# 2. ESPACE CHAT (IMMERSION)
elif st.session_state.user:
    st.markdown("<h2 style='text-align:center;'>HARTUR ONLINE</h2>", unsafe_allow_html=True)
    if st.sidebar.button("Déconnexion"): st.session_state.user = None; st.rerun()

    # Affichage
    for m in st.session_state.msgs:
        with st.chat_message(m["role"]): st.write(m["content"])

    if prompt := st.chat_input("Dis-moi tout..."):
        st.session_state.msgs.append({"role": "user", "content": prompt, "time": str(datetime.now())})
        with st.chat_message("user"): st.write(prompt)
        
        with st.chat_message("assistant"):
            # Personnalité : Le pote honnête qui se souvient
            reponse = f"Écoute mon pote, tu me dis '{prompt}'. Si je suis honnête avec toi, je pense que..."
            st.write(reponse)
            st.session_state.msgs.append({"role": "assistant", "content": reponse, "time": str(datetime.now())})
            
        # SAUVEGARDE GITHUB AUTO (PERSISTENCE)
        raw, sha = github_fetch(FICHIER_CHATS)
        data = json.loads(raw) if raw else {}
        data[st.session_state.user] = st.session_state.msgs
        github_push(FICHIER_CHATS, json.dumps(data), f"Update chat {st.session_state.user}", sha)

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
                raw, _ = github_fetch(FICHIER_COMPTES)
                df = pd.read_csv(StringIO(raw)) if raw else pd.DataFrame(columns=["pseudo", "password"])
                if not df[(df['pseudo'] == u) & (df['password'] == p)].empty:
                    st.session_state.user = u
                    # Charger historique
                    raw_c, _ = github_fetch(FICHIER_CHATS)
                    if raw_c: st.session_state.msgs = json.loads(raw_c).get(u, [])
                    st.rerun()
                else: st.error("Inconnu.")
        with t2:
            nu = st.text_input("Nouveau Pseudo")
            np = st.text_input("Nouveau MDP", type="password")
            if st.button("VALIDER"):
                raw, sha = github_fetch(FICHIER_COMPTES)
                df = pd.read_csv(StringIO(raw)) if raw else pd.DataFrame(columns=["pseudo", "password"])
                if nu and np and nu not in df['pseudo'].values:
                    new_df = pd.concat([df, pd.DataFrame({"pseudo":[nu], "password":[np]})])
                    github_push(FICHIER_COMPTES, new_df.to_csv(index=False), f"Inscrit: {nu}", sha)
                    st.success("Inscrit !")
