import streamlit as st
import pandas as pd
import requests
import base64
import json
from io import StringIO
from datetime import datetime

# ==========================================
# ⚙️ CONFIGURATION CORE (GITHUB)
# ==========================================
REPO_NOM = "zachariepays-debug/Hartur-ia" 
FICHIER_COMPTES = "comptes.csv"
FICHIER_CHATS = "conversations.json"
FICHIER_SYSTEM = "system_state.json"
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
MASTER_CODE = "babar"

st.set_page_config(page_title="HARTUR | NEURAL OS", layout="wide", page_icon="💀")

# --- Fonction de synchronisation GitHub sans erreur ---
def sync_github(chemin, method="GET", content=None, sha=None):
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    url = f"https://api.github.com/repos/{REPO_NOM}/contents/{chemin}"
    
    if method == "GET":
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            j = r.json()
            return base64.b64decode(j['content']).decode('utf-8'), j['sha']
        return None, None
    else:
        payload = {"message": "HARTUR_SYNC", "content": base64.b64encode(content.encode('utf-8')).decode('utf-8')}
        if sha: payload["sha"] = sha
        requests.put(url, headers=headers, data=json.dumps(payload))
        return None, None

# ==========================================
# 🔐 VÉRIFICATION ÉTAT SYSTÈME (PERSISTANT)
# ==========================================
raw_sys, sha_sys = sync_github(FICHIER_SYSTEM)
# Si le fichier n'existe pas, on considère que c'est actif par défaut
sys_state = json.loads(raw_sys) if raw_sys else {"active": True}

if not sys_state["active"]:
    st.markdown("<style>.stApp { background-color: black !important; color: white !important; }</style>", unsafe_allow_html=True)
    st.markdown("<div style='text-align:center; padding-top:30vh;'><h1>HARTUR EST ÉTEINT</h1><p>REOUVRIR HARTUR</p></div>", unsafe_allow_html=True)
    unlock = st.text_input("SÉCURITÉ CORE", type="password", label_visibility="collapsed")
    if unlock == MASTER_CODE:
        sync_github(FICHIER_SYSTEM, "PUT", json.dumps({"active": True}), sha_sys)
        st.rerun()
    st.stop()

# ==========================================
# 🚀 INITIALISATION SESSION
# ==========================================
if "user" not in st.session_state: st.session_state.user = None
if "admin_mode" not in st.session_state: st.session_state.admin_mode = False
if "msgs" not in st.session_state: st.session_state.msgs = []

# ==========================================
# 🎨 DESIGN & STYLE
# ==========================================
st.markdown("""
    <style>
    .stApp { background-color: #030507; color: #ffffff; }
    header { visibility: hidden; }
    .giant-title { font-size: 70px; font-weight: 900; letter-spacing: 15px; text-align: center; color: white; margin: 0; }
    .signature-zac { color: #ff4b4b; text-align: center; font-weight: 900; letter-spacing: 5px; font-size: 13px; margin-bottom: 30px; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 🛠️ MODE ADMIN (GOD MODE)
# ==========================================
if st.session_state.admin_mode:
    st.title("🛠️ PANNEAU DE CONTRÔLE ADMIN")
    
    with st.sidebar:
        if st.button("🔴 ÉTEINDRE LE SYSTÈME"):
            sync_github(FICHIER_SYSTEM, "PUT", json.dumps({"active": False}), sha_sys)
            st.rerun()
        if st.button("🚪 QUITTER ADMIN"):
            st.session_state.admin_mode = False
            st.rerun()

    tab1, tab2, tab3 = st.tabs(["👥 COMPTES", "📂 DOSSIERS", "🌐 FLUX GLOBAL"])
    
    c_data, _ = sync_github(FICHIER_CHATS)
    all_chats = json.loads(c_data) if c_data else {}

    with tab1:
        u_raw, _ = sync_github(FICHIER_COMPTES)
        if u_raw:
            df = pd.read_csv(StringIO(u_raw))
            st.dataframe(df, use_container_width=True)
            st.download_button("Télécharger CSV Comptes", u_raw, "comptes.csv")

    with tab2:
        u_select = st.selectbox("Dossier de l'utilisateur :", ["Choisir..."] + list(all_chats.keys()))
        if u_select != "Choisir...":
            st.info(f"Archive de {u_select}")
            for i, m in enumerate(all_chats[u_select][::-1]):
                nom = u_select if m['role'] == 'user' else "💀 HARTUR"
                st.text_area(f"De : {nom}", m['content'], height=80, key=f"admin_u_{u_select}_{i}")
            st.download_button(f"Télécharger dossier {u_select}", json.dumps(all_chats[u_select]), f"{u_select}.json")

    with tab3:
        st.subheader("Flux Global (Messages mélangés)")
        tous_messages = []
        for user_name, messages in all_chats.items():
            for m in messages:
                tous_messages.append({"user": user_name, "role": m['role'], "content": m['content']})
        
        # Affichage du plus récent en haut
        for i, m in enumerate(tous_messages[::-1]):
            role_label = f"👤 {m['user']}" if m['role'] == 'user' else "💀 HARTUR"
            st.markdown(f"**{role_label}** : {m['content']}")
            st.divider()

# ==========================================
# 💬 INTERFACE CHAT (UTILISATEUR)
# ==========================================
elif st.session_state.user:
    st.markdown(f"<h3 style='text-align:center;'>HARTUR : SESSION {st.session_state.user}</h3>", unsafe_allow_html=True)
    if st.sidebar.button("DÉCONNEXION"):
        st.session_state.user = None
        st.rerun()

    for m in st.session_state.msgs:
        with st.chat_message(m["role"]): st.write(m["content"])

    if prompt := st.chat_input("Balance ce que t'as sur le coeur..."):
        # Ajout du message utilisateur
        st.session_state.msgs.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.write(prompt)
        
        # Réponse de l'IA (Personnalité de pote)
        with st.chat_message("assistant"):
            reponse = f"Écoute mon pote, tu me parles de '{prompt}', mais si on est honnête..."
            st.write(reponse)
            st.session_state.msgs.append({"role": "assistant", "content": reponse})
            
        # Sauvegarde GitHub Instantanée
        raw_c, sha_c = sync_github(FICHIER_CHATS)
        hist = json.loads(raw_c) if raw_c else {}
        hist[st.session_state.user] = st.session_state.msgs
        sync_github(FICHIER_CHATS, "PUT", json.dumps(hist), sha_c)

# ==========================================
# 🔐 ÉCRAN D'ACCUEIL (CONNEXION & 6/6)
# ==========================================
else:
    st.markdown('<h1 class="giant-title">HARTUR</h1>', unsafe_allow_html=True)
    st.markdown('<p class="signature-zac">CRÉÉ PAR ZACMITE</p>', unsafe_allow_html=True)
    
    col_l, col_m, col_r = st.columns([1, 1.5, 1])
    with col_m:
        tabs = st.tabs(["ENTRER", "REJOINDRE"])
        with tabs[0]:
            u = st.text_input("PSEUDO")
            p = st.text_input("MOT DE PASSE", type="password")
            if st.button("DÉVERROUILLER"):
                # RACCOURCI SECRET ADMIN
                if u == "6" and p == "6":
                    st.session_state.admin_mode = True
                    st.rerun()
                
                u_raw, _ = sync_github(FICHIER_COMPTES)
                df = pd.read_csv(StringIO(u_raw)) if u_raw else pd.DataFrame()
                if not df.empty and not df[(df['pseudo'] == u) & (df['password'] == p)].empty:
                    st.session_state.user = u
                    c_raw, _ = sync_github(FICHIER_CHATS)
                    if c_raw: st.session_state.msgs = json.loads(c_raw).get(u, [])
                    st.rerun()
                else: st.error("Accès refusé.")
        
        with tabs[1]:
            nu = st.text_input("NOUVEAU PSEUDO")
            np = st.text_input("NOUVELLE CLÉ", type="password")
            if st.button("CRÉER MON ACCÈS"):
                u_raw, u_sha = sync_github(FICHIER_COMPTES)
                df = pd.read_csv(StringIO(u_raw)) if u_raw else pd.DataFrame(columns=["pseudo", "password"])
                if nu and np and nu not in df['pseudo'].values:
                    new_df = pd.concat([df, pd.DataFrame({"pseudo":[nu], "password":[np]})])
                    sync_github(FICHIER_COMPTES, "PUT", new_df.to_csv(index=False), u_sha)
                    st.success("Compte créé sur GitHub !")
