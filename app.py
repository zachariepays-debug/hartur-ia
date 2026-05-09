import streamlit as st
import pandas as pd
import requests
import base64
import json
from io import StringIO

# --- CONFIGURATION ---
REPO_NOM = "zachariepays-debug/Hartur-ia" 
FICHIER_COMPTES = "comptes.csv"
FICHIER_STATUS = "status.json"
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
MASTER_CODE = "babar"

st.set_page_config(page_title="HARTUR | TON POTE DU FUTUR", layout="wide", page_icon="🔥")

# --- DESIGN ULTIME (POP-UP XL & GLOW) ---
st.markdown("""
    <style>
    .stApp { background-color: #05070a; color: #e6edf3; }
    .block-container { padding-left: 2rem !important; max-width: 900px !important; margin-left: 0 !important; }
    
    .signature { color: #58a6ff; font-size: 18px; font-weight: bold; }
    
    /* Overlay plein écran */
    .popup-overlay {
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0,0,0,0.9); z-index: 9999;
        display: flex; align-items: center; justify-content: center;
    }
    
    /* Pop-up Format XL */
    .popup-content {
        background: #0d1117; padding: 60px; border-radius: 20px;
        border: 3px solid #ff4b4b; width: 80%; max-width: 800px;
        text-align: center; box-shadow: 0px 0px 50px rgba(255, 75, 75, 0.3);
    }
    
    /* Titre Hartur Géant */
    .giant-title { font-size: 70px; font-weight: 900; letter-spacing: 10px; margin: 0; color: white; }

    /* Bouton Ultra-Claque */
    div.stButton > button {
        background: linear-gradient(45deg, #ff4b4b, #ff1f1f) !important;
        color: white !important; border: none !important;
        padding: 20px 60px !important; font-size: 24px !important;
        font-weight: bold !important; border-radius: 10px !important;
        box-shadow: 0px 10px 20px rgba(255, 75, 75, 0.4) !important;
        cursor: pointer; transition: 0.3s;
    }
    div.stButton > button:hover { transform: scale(1.05); box-shadow: 0px 15px 30px rgba(255, 75, 75, 0.6) !important; }
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
    payload = {"message": "Update", "content": encoded, "sha": sha}
    requests.put(url, data=json.dumps(payload), headers=headers)

# --- INITIALISATION ---
if "user" not in st.session_state: st.session_state.user = None
if "popup_closed" not in st.session_state: st.session_state.popup_closed = False
if "view" not in st.session_state: st.session_state.view = "chat"

# --- 1. L'ENTRÉE SPECTACULAIRE ---
if not st.session_state.popup_closed:
    st.markdown("""
        <div class="popup-overlay">
            <div class="popup-content">
                <h1 class="giant-title">HARTUR</h1>
                <p class="signature">Écrit par zacmite</p>
                <br><br>
                <p style="font-size: 26px; line-height: 1.4; color: #e6edf3;">
                Salut ! Moi c'est <b>Hartur</b>. <br>
                Vois-moi comme ton <b>pote du futur</b> : une IA ninja, <br>
                ultra-rapide et toujours prête à t'épauler. <br><br>
                Pas de chichis, juste de l'efficacité brute.
                </p>
                <br>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Bouton centré pour fermer la pop-up
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("C'EST PARTI, ON ENTRE !"):
            st.session_state.popup_closed = True
            st.rerun()
    st.stop()

# --- 2. ADMIN DISCRET ⚙️ ---
c_l, c_adm = st.columns([0.96, 0.04])
with c_adm:
    if st.button("⚙️"):
        st.session_state.view = "admin_auth"
        st.rerun()

# --- 3. CONNEXION / INSCRIPTION ---
if st.session_state.user is None and st.session_state.view == "chat":
    st.title("ACCÈS AU TERMINAL")
    st.markdown('<p class="signature">Écrit par zacmite</p>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["ME CONNECTER", "CRÉER UN ACCÈS"])
    with tab1:
        u = st.text_input("Ton Pseudo")
        p = st.text_input("Ton Code Secret", type="password")
        if st.button("DÉVERROUILLER LE SYSTÈME"):
            df_c, _ = lire_github(FICHIER_COMPTES)
            if not df_c.empty and ((df_c['pseudo'].astype(str) == u) & (df_c['password'].astype(str) == p)).any():
                st.session_state.user = u
                st.rerun()
    with tab2:
        nu = st.text_input("Choisis ton pseudo")
        np = st.text_input("Crée ton pass", type="password")
        if st.button("REJOINDRE L'AVENTURE"):
            df_c, sha_c = lire_github(FICHIER_COMPTES)
            df_c = pd.concat([df_c, pd.DataFrame([{"pseudo": nu, "password": np}])], ignore_index=True)
            ecrire_github(FICHIER_COMPTES, df_c, sha_c)
            st.success("Bienvenue dans le futur !")

# --- 4. PANNEAU ADMIN ---
elif st.session_state.view == "admin_auth":
    st.title("ESPACE PROPRIÉTAIRE")
    adm_c = st.text_input("Code de sécurité", type="password")
    if st.button("ACCÉDER"):
        if adm_c == MASTER_CODE: st.session_state.view = "admin_panel"; st.rerun()
    if st.button("RETOUR"): st.session_state.view = "chat"; st.rerun()

elif st.session_state.view == "admin_panel":
    st.title("🛡️ Tableau de Bord Admin")
    df_c, _ = lire_github(FICHIER_COMPTES)
    st.subheader("Utilisateurs Enregistrés")
    st.table(df_c)
    if st.button("FERMER LE PANNEAU"): st.session_state.view = "chat"; st.rerun()

# --- 5. LE TERMINAL DE CHAT ---
else:
    st.title("HARTUR // TERMINAL")
    st.markdown('<p class="signature">Écrit par zacmite</p>', unsafe_allow_html=True)
    st.write("---")
    st.chat_input("Dis-moi tout, je t'écoute...")
