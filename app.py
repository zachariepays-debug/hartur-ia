import streamlit as st
import pandas as pd
import requests
import base64
import json
from io import StringIO

# --- CONFIGURATION STRICTE ---
REPO_NOM = "zachariepays-debug/Hartur-ia" 
FICHIER_HIST = "historique.csv"
FICHIER_COMPTES = "comptes.csv"
FICHIER_STATUS = "status.json"

MISTRAL_API_KEY = st.secrets["MISTRAL_KEY"]
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
MASTER_CODE = "babar"

# --- CONFIG PAGE ---
st.set_page_config(page_title="HARTUR", layout="wide", page_icon="🔥")

# --- DESIGN "LEFT-SIDE" & COMPACT ---
st.markdown("""
    <style>
    /* Fond sombre et texte à gauche */
    .stApp { background-color: #0b0e11; color: white; }
    .block-container { 
        padding-left: 2rem !important; 
        max-width: 700px !important; /* Taille opti pour pas que ce soit trop large */
        margin-left: 0 !important; 
    }
    
    /* Input design */
    .stTextInput>div>div>input {
        background-color: #161b22 !important;
        color: white !important;
        border: 1px solid #30363d !important;
        border-radius: 8px !important;
        text-align: left !important;
    }
    
    /* Boutons stylés */
    .stButton>button {
        background-color: #238636 !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: bold !important;
        width: auto !important;
        padding: 0.5rem 2rem !important;
    }
    
    /* Kill Switch Overlay */
    .locked-overlay {
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        background-color: #000000; z-index: 99999;
        display: flex; flex-direction: column; align-items: flex-start; justify-content: center;
        padding-left: 10%;
    }
    </style>
    """, unsafe_allow_html=True)

# --- MOTEUR GITHUB OPTIMISÉ ---
def lire_github(nom_fichier, est_json=False):
    url = f"https://api.github.com/repos/{REPO_NOM}/contents/{nom_fichier}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    try:
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            data = r.json()
            content = base64.b64decode(data['content']).decode('utf-8')
            if est_json: return json.loads(content), data['sha']
            return pd.read_csv(StringIO(content)), data['sha']
    except: pass
    return ({"active": True}, None) if est_json else (pd.DataFrame(columns=["pseudo", "password", "role", "content"]), None)

def ecrire_github(nom_fichier, contenu, sha, est_json=False):
    url = f"https://api.github.com/repos/{REPO_NOM}/contents/{nom_fichier}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    text = json.dumps(contenu) if est_json else contenu.to_csv(index=False)
    encoded = base64.b64encode(text.encode('utf-8')).decode('utf-8')
    payload = {"message": "Sync", "content": encoded, "sha": sha}
    requests.put(url, data=json.dumps(payload), headers=headers)

# --- SYSTÈME DE SÉCURITÉ GLOBALE (KILL SWITCH) ---
status_data, sha_status = lire_github(FICHIER_STATUS, est_json=True)
if not status_data.get("active", True):
    st.markdown('<div class="locked-overlay"><h1 style="font-size: 60px; color: red;">ARTHUR EST ÉTEINT</h1><p style="font-size: 20px;">Maintenance système en cours...</p></div>', unsafe_allow_html=True)
    with st.container():
        st.write("### 🔑 ACCÈS RÉACTIVATION")
        code_on = st.text_input("Code secret", type="password", key="global_wake")
        if st.button("RELANCER LE SYSTÈME"):
            if code_on == MASTER_CODE:
                ecrire_github(FICHIER_STATUS, {"active": True}, sha_status, est_json=True)
                st.rerun()
    st.stop()

# --- ÉTAT DE SESSION ---
if "user" not in st.session_state: st.session_state.user = None
if "view" not in st.session_state: st.session_state.view = "chat"

# --- GESTION ADMIN ---
if st.session_state.user:
    col_a, col_b = st.columns([0.8, 0.2])
    with col_b:
        if st.button("🔐 ADMIN"): st.session_state.view = "admin_auth"

if st.session_state.view == "admin_auth":
    st.title("🛡️ Panel Admin")
    pass_adm = st.text_input("Mot de passe maître", type="password")
    if st.button("CONFIRMER"):
        if pass_adm == MASTER_CODE: st.session_state.view = "admin_panel"; st.rerun()
    if st.button("RETOUR"): st.session_state.view = "chat"; st.rerun()

elif st.session_state.view == "admin_panel":
    st.title("⚡ Centre de Commande")
    if st.button("🚨 COUPER ARTHUR POUR TOUS"):
        ecrire_github(FICHIER_STATUS, {"active": False}, sha_status, est_json=True)
        st.rerun()
    
    st.divider()
    df_c, _ = lire_github(FICHIER_COMPTES)
    st.subheader("👥 Utilisateurs Inscrits")
    st.table(df_c[['pseudo', 'password']])
    
    if st.button("⬅️ QUITTER"): st.session_state.view = "chat"; st.rerun()

# --- CONNEXION ET INSCRIPTION ---
elif st.session_state.user is None:
    st.title("🔥 HARTUR")
    tab1, tab2 = st.tabs(["Se connecter", "S'inscrire"])
    
    with tab1:
        u = st.text_input("Pseudo", key="login_u")
        p = st.text_input("Pass", type="password", key="login_p")
        if st.button("GO"):
            df_c, _ = lire_github(FICHIER_COMPTES)
            if not df_c.empty and ((df_c['pseudo'].astype(str) == u) & (df_c['password'].astype(str) == p)).any():
                st.session_state.user = u
                st.rerun()
            else: st.error("Inconnu ou faux.")

    with tab2:
        nu = st.text_input("Nouveau Pseudo", key="reg_u")
        np = st.text_input("Nouveau Pass", type="password", key="reg_p")
        if st.button("REJOINDRE"):
            df_c, sha_c = lire_github(FICHIER_COMPTES)
            if nu and np:
                new_user = pd.DataFrame([{"pseudo": nu, "password": np}])
                df_c = pd.concat([df_c, new_user], ignore_index=True)
                ecrire_github(FICHIER_COMPTES, df_c, sha_c)
                st.success("Inscrit ! Connecte-toi.")

# --- INTERFACE DE CHAT ---
else:
    st.title(f"HARTUR x {st.session_state.user}")
    
    # Ici tu mets ton code Mistral pour les réponses
    st.write("Système opérationnel. Prêt à monter en puissance.")
    if st.button("Déconnexion"):
        st.session_state.user = None
        st.rerun()
