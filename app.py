import streamlit as st
import pandas as pd
import requests
import base64
import json
from io import StringIO

# --- CONFIGURATION ---
REPO_NOM = "zachariepays-debug/Hartur-ia" 
FICHIER_HIST = "historique.csv"
FICHIER_COMPTES = "comptes.csv"
FICHIER_STATUS = "status.json"

MISTRAL_API_KEY = st.secrets["MISTRAL_KEY"]
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
MASTER_CODE = "babar"

st.set_page_config(page_title="HARTUR", layout="wide", page_icon="🔥")

# --- DESIGN (SIGNATURE ZACMITE + ALIGNEMENT GAUCHE + OLED BLACK) ---
st.markdown("""
    <style>
    .stApp { background-color: #05070a; color: #e6edf3; }
    .block-container { 
        padding-left: 2rem !important; 
        max-width: 800px !important; 
        margin-left: 0 !important; 
        text-align: left !important; 
    }
    
    .signature { color: #58a6ff; font-size: 14px; margin-top: -20px; margin-bottom: 20px; text-align: left; font-weight: bold; }
    .intro-box { border-left: 3px solid #ff4b4b; padding-left: 20px; margin-bottom: 30px; text-align: left; }
    
    input { text-align: left !important; }
    .stTextInput>div>div>input { background-color: #0d1117 !important; color: white !important; border: 1px solid #30363d !important; }
    
    /* Bouton rouge Hartur */
    .stButton>button { 
        background: #ff4b4b !important; 
        color: white !important; 
        border: none !important; 
        font-weight: bold !important; 
        width: auto !important;
        padding: 0.5rem 2rem !important;
        border-radius: 5px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- FONCTIONS GITHUB ---
def lire_github(nom_fichier, est_json=False):
    url = f"https://api.github.com/repos/{REPO_NOM}/contents/{nom_fichier}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        data = r.json()
        content = base64.b64decode(data['content']).decode('utf-8')
        if est_json: return json.loads(content), data['sha']
        return pd.read_csv(StringIO(content)), data['sha']
    return ({"active": True}, None) if est_json else (pd.DataFrame(columns=["pseudo", "password", "role", "content"]), None)

def ecrire_github(nom_fichier, contenu, sha, est_json=False):
    url = f"https://api.github.com/repos/{REPO_NOM}/contents/{nom_fichier}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    text = json.dumps(contenu) if est_json else contenu.to_csv(index=False)
    encoded = base64.b64encode(text.encode('utf-8')).decode('utf-8')
    payload = {"message": "Sync System", "content": encoded, "sha": sha}
    requests.put(url, data=json.dumps(payload), headers=headers)

# --- BLOCAGE GLOBAL (SI ARTHUR EST ÉTEINT) ---
status_data, sha_status = lire_github(FICHIER_STATUS, est_json=True)
if not status_data.get("active", True):
    st.markdown("""
        <div style="background:black;height:100vh;padding:50px;">
            <h1 style="color:white;font-size:50px;">ARTHUR EST ÉTEINT</h1>
            <p style="color:#555;">Maintenance globale en cours...</p>
        </div>
    """, unsafe_allow_html=True)
    code_on = st.text_input("Code de réactivation", type="password")
    if st.button("RALLUMER ARTHUR"):
        if code_on == MASTER_CODE:
            ecrire_github(FICHIER_STATUS, {"active": True}, sha_status, est_json=True)
            st.rerun()
    st.stop()

# --- GESTION DES SESSIONS ---
if "user" not in st.session_state: st.session_state.user = None
if "intro_done" not in st.session_state: st.session_state.intro_done = False
if "view" not in st.session_state: st.session_state.view = "chat"

# --- LOGO ADMIN DISCRET ⚙️ ---
if st.session_state.intro_done:
    col_n1, col_n2 = st.columns([0.94, 0.06])
    with col_n2:
        if st.button("⚙️"):
            st.session_state.view = "admin_auth"
            st.rerun()

# --- 1. PAGE DE PRÉSENTATION ---
if not st.session_state.intro_done:
    st.title("HARTUR")
    st.markdown('<p class="signature">Écrit par zacmite</p>', unsafe_allow_html=True)
    st.markdown("""
    <div class="intro-box">
        <h3>L'IA sans limites.</h3>
        <p>Prêt à entrer dans le terminal ?</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("ENTRER DANS LE SYSTÈME"):
        st.session_state.intro_done = True
        st.rerun()
    st.stop()

# --- 2. AUTHENTIFICATION ---
if st.session_state.view == "admin_auth":
    st.title("Accès Propriétaire")
    adm_code = st.text_input("Code maître", type="password")
    if st.button("DÉVERROUILLER"):
        if adm_code == MASTER_CODE: 
            st.session_state.view = "admin_panel"
            st.rerun()
    if st.button("RETOUR"): 
        st.session_state.view = "chat"
        st.rerun()

elif st.session_state.view == "admin_panel":
    st.title("🛡️ Dashboard Admin")
    if st.button("🚨 ÉTEINDRE ARTHUR POUR TOUS"):
        ecrire_github(FICHIER_STATUS, {"active": False}, sha_status, est_json=True)
        st.rerun()
    if st.button("⬅️ QUITTER"):
        st.session_state.view = "chat"
        st.rerun()
    df_c, _ = lire_github(FICHIER_COMPTES)
    st.subheader("Utilisateurs connectés")
    st.table(df_c)

elif st.session_state.user is None:
    st.title("HARTUR // ACCÈS")
    st.markdown('<p class="signature">Écrit par zacmite</p>', unsafe_allow_html=True)
    
    tab_conn, tab_ins = st.tabs(["Connexion", "Inscription"])
    with tab_conn:
        u = st.text_input("Pseudo")
        p = st.text_input("Pass", type="password")
        if st.button("CONNEXION"):
            df_c, _ = lire_github(FICHIER_COMPTES)
            if not df_c.empty and ((df_c['pseudo'].astype(str) == u) & (df_c['password'].astype(str) == p)).any():
                st.session_state.user = u
                st.rerun()
    with tab_ins:
        nu = st.text_input("Pseudo souhaité")
        np = st.text_input("Pass souhaité", type="password")
        if st.button("CRÉER COMPTE"):
            df_c, sha_c = lire_github(FICHIER_COMPTES)
            df_c = pd.concat([df_c, pd.DataFrame([{"pseudo": nu, "password": np}])], ignore_index=True)
            ecrire_github(FICHIER_COMPTES, df_c, sha_c)
            st.success("Compte créé !")

# --- 3. TERMINAL DE CHAT ---
else:
    st.title("HARTUR // TERMINAL")
    st.markdown('<p class="signature">Écrit par zacmite</p>', unsafe_allow_html=True)
    st.write("---")
    
    # Tout ce qui est écrit ici est enregistré pour l'Admin
    prompt = st.chat_input("Le système écoute...")
