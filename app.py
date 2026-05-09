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

st.set_page_config(page_title="HARTUR | SYSTEM", layout="wide", page_icon="🔥")

# --- DESIGN ULTIME (EFFETS GLOW & ALIGNEMENT GAUCHE) ---
st.markdown("""
    <style>
    .stApp { background-color: #05070a; color: #e6edf3; }
    .block-container { padding-left: 2rem !important; max-width: 800px !important; margin-left: 0 !important; }
    
    /* Titres et Accroches */
    h1, h2, h3 { color: #ffffff; text-align: left; font-family: 'Courier New', Courier, monospace; }
    .intro-box { border-left: 3px solid #ff4b4b; padding-left: 20px; margin-bottom: 30px; }
    
    /* Inputs stylés */
    .stTextInput>div>div>input {
        background-color: #0d1117 !important;
        color: #58a6ff !important;
        border: 1px solid #30363d !important;
        border-radius: 4px !important;
    }
    
    /* Bouton Flashy */
    .stButton>button {
        background: linear-gradient(90deg, #ff4b4b 0%, #ff1f1f 100%) !important;
        color: white !important;
        border: none !important;
        box-shadow: 0px 0px 15px rgba(255, 75, 75, 0.4);
        transition: 0.3s;
    }
    .stButton>button:hover { box-shadow: 0px 0px 25px rgba(255, 75, 75, 0.8); transform: scale(1.02); }

    /* Overlay Kill Switch */
    .locked-overlay {
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        background-color: black; z-index: 99999;
        display: flex; flex-direction: column; align-items: flex-start; justify-content: center;
        padding-left: 5%;
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
    return ({"active": True}, None) if est_json else (pd.DataFrame(columns=["pseudo", "password"]), None)

def ecrire_github(nom_fichier, contenu, sha, est_json=False):
    url = f"https://api.github.com/repos/{REPO_NOM}/contents/{nom_fichier}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    text = json.dumps(contenu) if est_json else contenu.to_csv(index=False)
    encoded = base64.b64encode(text.encode('utf-8')).decode('utf-8')
    payload = {"message": "Sync", "content": encoded, "sha": sha}
    requests.put(url, data=json.dumps(payload), headers=headers)

# --- SÉCURITÉ GLOBALE ---
status_data, sha_status = lire_github(FICHIER_STATUS, est_json=True)
if not status_data.get("active", True):
    st.markdown('<div class="locked-overlay"><h1>SYSTÈME ÉTEINT</h1><p>Relance manuelle requise.</p></div>', unsafe_allow_html=True)
    code_on = st.text_input("Code de réactivation", type="password")
    if st.button("RÉACTIVER"):
        if code_on == MASTER_CODE:
            ecrire_github(FICHIER_STATUS, {"active": True}, sha_status, est_json=True)
            st.rerun()
    st.stop()

# --- ÉTATS DE SESSION ---
if "user" not in st.session_state: st.session_state.user = None
if "intro_done" not in st.session_state: st.session_state.intro_done = False
if "view" not in st.session_state: st.session_state.view = "chat"

# --- 1. PAGE D'INTRODUCTION (AVANT CONNEXION) ---
if not st.session_state.intro_done:
    st.title("🔥 BIENVENUE SUR HARTUR")
    st.markdown("""
    <div class="intro-box">
        <h3>"Je ne suis pas une IA ordinaire."</h3>
        <p>Bonjour, je m'appelle <b>Hartur</b>. J'ai été conçu par <b>Zacharie pays</b> pour briser les codes.</p>
        <p>Contrairement aux autres, je ne tourne pas autour du pot. Je suis direct, percutant, et je n'ai pas de filtres inutiles.</p>
        <hr style="border: 0.1px solid #30363d;">
        <p><b>Mes Capacités :</b></p>
        <ul>
            <li>💬 <b>Réponses Cash :</b> Pas de blabla, juste la vérité.</li>
            <li>👻 <b>Mode Ghost :</b> Discute sans laisser de traces.</li>
            <li>🛡️ <b>Accès Élite :</b> Système sécurisé par protocole propriétaire.</li>
            <li>⚡ <b>Vitesse Alpha :</b> Temps de réponse optimisé.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("ACCÉDER AU SYSTÈME"):
        st.session_state.intro_done = True
        st.rerun()
    st.stop()

# --- 2. CONNEXION / INSCRIPTION ---
elif st.session_state.user is None:
    st.title("🔐 AUTHENTIFICATION")
    t1, t2 = st.tabs(["IDENTIFICATION", "NOUVEL ACCÈS"])
    
    with t1:
        u = st.text_input("Pseudo")
        p = st.text_input("Mot de passe", type="password")
        if st.button("LANCER LA SESSION"):
            df_c, _ = lire_github(FICHIER_COMPTES)
            if not df_c.empty and ((df_c['pseudo'].astype(str) == u) & (df_c['password'].astype(str) == p)).any():
                st.session_state.user = u
                st.rerun()
            else: st.error("Accès refusé.")

    with t2:
        nu = st.text_input("Choisir un pseudo")
        np = st.text_input("Choisir un mot de passe", type="password")
        if st.button("CRÉER MON ACCÈS ÉLITE"):
            df_c, sha_c = lire_github(FICHIER_COMPTES)
            if nu and np:
                df_c = pd.concat([df_c, pd.DataFrame([{"pseudo": nu, "password": np}])], ignore_index=True)
                ecrire_github(FICHIER_COMPTES, df_c, sha_c)
                st.success("Accès créé ! Connecte-toi.")

# --- 3. INTERFACE CHAT ---
else:
    # Option ADMIN rapide en haut à droite
    col_t, col_a = st.columns([0.9, 0.1])
    with col_a:
        if st.button("⚙️"): st.session_state.view = "admin_auth"
    
    if st.session_state.view == "admin_auth":
        # ... (Logique Admin avec le code 'babar' déjà faite)
        pass 

    st.title(f"HARTUR // {st.session_state.user}")
    
    # Nouvelle fonctionnalité : Mode Ghost
    ghost = st.toggle("Mode Ghost (Ne pas sauvegarder cette conversation)")
    
    st.write("---")
    st.write("Le terminal est prêt. Pose ta question.")
    
    # ... (Suite du code pour Mistral AI)
