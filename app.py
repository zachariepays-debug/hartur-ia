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

# --- CSS : CENTRAGE ABSOLU ET FENÊTRE MODALE ---
st.markdown("""
    <style>
    .stApp { background-color: #05070a; color: #e6edf3; }
    
    /* Overlay plein écran */
    .modal-backdrop {
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0, 0, 0, 0.9); backdrop-filter: blur(10px);
        z-index: 9999; display: flex; align-items: center; justify-content: center;
    }
    
    /* Fenêtre Pop-up centrée */
    .modal-content {
        background: #0d1117; padding: 50px; border-radius: 20px;
        border: 2px solid #ff4b4b; width: 90%; max-width: 750px;
        text-align: center; position: relative;
        box-shadow: 0px 0px 50px rgba(255, 75, 75, 0.3);
    }
    
    /* Alignement Titre et Signature */
    .header-group {
        display: flex; flex-direction: column; align-items: center;
        width: 100%; margin-bottom: 30px;
    }
    .giant-title { font-size: 65px; font-weight: 900; letter-spacing: 8px; margin: 0; color: white; line-height: 1; }
    .signature-zac { color: #58a6ff; font-weight: bold; font-size: 18px; margin-top: 10px; }

    .capability-list { text-align: left; display: inline-block; font-size: 18px; line-height: 2; margin: 20px 0; }
    
    /* Bouton de fermeture stylé */
    div.stButton > button {
        background: linear-gradient(90deg, #ff4b4b, #8b0000) !important;
        color: white !important; border: none !important;
        padding: 15px 40px !important; font-size: 18px !important;
        font-weight: bold !important; border-radius: 8px !important;
        cursor: pointer;
    }
    </style>
    """, unsafe_allow_html=True)

# --- FONCTIONS SYSTÈME ---
def lire_comptes():
    url = f"https://api.github.com/repos/{REPO_NOM}/contents/{FICHIER_COMPTES}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        data = r.json()
        content = base64.b64decode(data['content']).decode('utf-8')
        return pd.read_csv(StringIO(content)), data['sha']
    return pd.DataFrame(columns=["pseudo", "password"]), None

# --- INITIALISATION ÉTATS ---
if "user" not in st.session_state: st.session_state.user = None
if "show_intro" not in st.session_state: st.session_state.show_intro = True
if "page" not in st.session_state: st.session_state.page = "chat"

# --- 1. LA FENÊTRE MODALE (POP-UP) ---
if st.session_state.show_intro:
    st.markdown("""
        <div class="modal-backdrop">
            <div class="modal-content">
                <div class="header-group">
                    <h1 class="giant-title">HARTUR</h1>
                    <p class="signature-zac">Créé par zacmite</p>
                </div>
                <div class="capability-list">
                    🚀 <b>Vitesse :</b> Réponses instantanées sans attente.<br>
                    🛡️ <b>Sécurité :</b> Chiffrement total de vos données.<br>
                    🧠 <b>IA Multi-Tâches :</b> Votre assistant personnel 24/7.<br>
                    🔥 <b>Pote du Futur :</b> Une interface cash et rapide.<br>
                    ⚡ <b>Liberté :</b> Aucune restriction sur vos requêtes.
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Le bouton Streamlit pour fermer et accéder au site
    col_l, col_btn, col_r = st.columns([1, 2, 1])
    with col_btn:
        if st.button("ACCÉDER AU TERMINAL"):
            st.session_state.show_intro = False
            st.rerun()
    st.stop()

# --- 2. BOUTON ADMIN DISCRET (EN HAUT À DROITE) ---
_, col_admin = st.columns([0.96, 0.04])
with col_admin:
    if st.button("⚙️"):
        st.session_state.page = "admin"
        st.rerun()

# --- 3. PAGE ADMIN ---
if st.session_state.page == "admin":
    st.title("Accès Propriétaire")
    pwd = st.text_input("Code maître", type="password")
    if st.button("DÉVERROUILLER"):
        if pwd == MASTER_CODE: st.write("Accès autorisé."); df, _ = lire_comptes(); st.table(df)
    if st.button("RETOUR"):
        st.session_state.page = "chat"
        st.rerun()

# --- 4. CONNEXION / INSCRIPTION ---
elif st.session_state.user is None:
    st.title("HARTUR // AUTHENTIFICATION")
    st.markdown('<p class="signature-zac">Créé par zacmite</p>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["SE CONNECTER", "S'INSCRIRE"])
    with tab1:
        u = st.text_input("Pseudo")
        p = st.text_input("Pass", type="password")
        if st.button("ENTRER"):
            df, _ = lire_comptes()
            if not df.empty and ((df['pseudo'].astype(str) == u) & (df['password'].astype(str) == p)).any():
                st.session_state.user = u
                st.rerun()
    with tab2:
        st.info("Inscriptions gérées par l'administrateur.")

# --- 5. CHAT (TERMINAL) ---
else:
    st.title("HARTUR // TERMINAL")
    st.markdown('<p class="signature-zac">Créé par zacmite</p>', unsafe_allow_html=True)
    st.write("---")
    st.chat_input("Le terminal est prêt. Pose ta question.")
