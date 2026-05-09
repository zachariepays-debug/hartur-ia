import streamlit as st
import pandas as pd
import requests
import base64
import json
from io import StringIO

# --- CONFIGURATION ---
REPO_NOM = "zachariepays-debug/Hartur-ia" 
FICHIER_COMPTES = "comptes.csv"
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
MASTER_CODE = "babar"

st.set_page_config(page_title="HARTUR | SYSTEM", layout="wide", page_icon="🔥")

# --- DESIGN "CENTRE PARFAIT" ---
st.markdown("""
    <style>
    .stApp { background-color: #05070a; color: #e6edf3; }
    
    /* Pop-up Overlay */
    .popup-overlay {
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0,0,0,0.96); z-index: 9999;
        display: flex; align-items: center; justify-content: center;
    }
    
    /* Contenu Pop-up avec centrage absolu */
    .popup-content {
        background: #0d1117; padding: 60px; border-radius: 25px;
        border: 2px solid #ff4b4b; width: 90%; max-width: 850px;
        text-align: center; position: relative;
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        box-shadow: 0px 0px 60px rgba(255, 75, 75, 0.4);
    }
    
    .giant-title { font-size: 70px; font-weight: 900; letter-spacing: 12px; margin: 0; color: white; width: 100%; text-align: center; }
    .signature-zac { color: #58a6ff; font-weight: bold; font-size: 20px; margin-top: 5px; width: 100%; text-align: center; }

    .capability-list { text-align: left; display: inline-block; font-size: 19px; line-height: 2; margin: 30px 0; }
    
    /* Bouton Entrer */
    div.stButton > button {
        background: linear-gradient(90deg, #ff4b4b, #8b0000) !important;
        color: white !important; border: none !important;
        padding: 18px 60px !important; font-size: 22px !important;
        font-weight: bold !important; border-radius: 12px !important;
        box-shadow: 0px 5px 20px rgba(255, 75, 75, 0.5) !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- FONCTIONS GITHUB ---
def lire_github(nom_fichier):
    url = f"https://api.github.com/repos/{REPO_NOM}/contents/{nom_fichier}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        data = r.json()
        content = base64.b64decode(data['content']).decode('utf-8')
        return pd.read_csv(StringIO(content)), data['sha']
    return pd.DataFrame(columns=["pseudo", "password"]), None

# --- INITIALISATION ---
if "user" not in st.session_state: st.session_state.user = None
if "popup_closed" not in st.session_state: st.session_state.popup_closed = False
if "view" not in st.session_state: st.session_state.view = "chat"

# --- 1. POP-UP CENTREE "CREE PAR ZACMITE" ---
if not st.session_state.popup_closed:
    st.markdown("""
        <div class="popup-overlay">
            <div class="popup-content">
                <h1 class="giant-title">HARTUR</h1>
                <p class="signature-zac">Créé par zacmite</p>
                <div class="capability-list">
                    🚀 <b>Vitesse :</b> Réponses instantanées.<br>
                    🛡️ <b>Sécurité :</b> Chiffrement de vos données.<br>
                    🧠 <b>IA Multi-Tâches :</b> Aide au quotidien.<br>
                    🔥 <b>Pote du Futur :</b> Rapide et cash.<br>
                    ⚡ <b>Liberté :</b> Aucune restriction inutile.
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    col_l, col_btn, col_r = st.columns([1, 2, 1])
    with col_btn:
        if st.button("ENTRER DANS LE TERMINAL"):
            st.session_state.popup_closed = True
            st.rerun()
    st.stop()

# --- 2. NAVIGATION ADMIN ---
c_1, c_adm = st.columns([0.96, 0.04])
with c_adm:
    if st.button("⚙️"):
        st.session_state.view = "admin_auth"
        st.rerun()

# --- 3. CONNEXION / INSCRIPTION ---
if st.session_state.user is None and st.session_state.view == "chat":
    st.title("HARTUR // ACCÈS")
    st.markdown('<p class="signature-zac">Créé par zacmite</p>', unsafe_allow_html=True)
    
    t_c, t_i = st.tabs(["ME CONNECTER", "M'INSCRIRE"])
    with t_c:
        u = st.text_input("Pseudo")
        p = st.text_input("Mot de passe", type="password")
        if st.button("DÉVERROUILLER"):
            df_c, _ = lire_github(FICHIER_COMPTES)
            if not df_c.empty and ((df_c['pseudo'].astype(str) == u) & (df_c['password'].astype(str) == p)).any():
                st.session_state.user = u
                st.rerun()
    with t_i:
        st.info("Inscriptions ouvertes.")

# --- 4. TERMINAL DE CHAT ---
else:
    st.title("HARTUR // TERMINAL")
    st.markdown('<p class="signature-zac">Créé par zacmite</p>', unsafe_allow_html=True)
    st.write("---")
    st.chat_input("Pose ta question...")
