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

st.set_page_config(page_title="HARTUR | SYSTEM", layout="wide", page_icon="🔥")

# --- DESIGN "PREMIUM CYBER" ---
st.markdown("""
    <style>
    .stApp { background-color: #05070a; color: #e6edf3; }
    .block-container { padding-left: 2rem !important; max-width: 800px !important; margin-left: 0 !important; }
    
    .signature { color: #58a6ff; font-size: 14px; margin-top: -10px; font-weight: bold; }
    
    /* Overlay sombre élégant */
    .popup-overlay {
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background: radial-gradient(circle, rgba(13,17,23,0.95) 0%, rgba(0,0,0,1) 100%);
        z-index: 9999; display: flex; align-items: center; justify-content: center;
    }
    
    /* Conteneur Pop-up avec Glow */
    .popup-content {
        background: #0d1117; padding: 50px; border-radius: 15px;
        border: 2px solid #ff4b4b; text-align: left;
        box-shadow: 0px 0px 30px rgba(255, 75, 75, 0.2);
    }
    
    /* Bouton "OK C'EST PARTI" Stylé */
    div.stButton > button {
        background: linear-gradient(90deg, #ff4b4b 0%, #ff1f1f 100%) !important;
        color: white !important;
        border: none !important;
        padding: 15px 40px !important;
        font-size: 18px !important;
        font-weight: bold !important;
        letter-spacing: 2px !important;
        border-radius: 50px !important;
        box-shadow: 0px 0px 15px rgba(255, 75, 75, 0.4) !important;
        transition: 0.4s !important;
    }
    div.stButton > button:hover {
        box-shadow: 0px 0px 30px rgba(255, 75, 75, 0.7) !important;
        transform: translateY(-3px) !important;
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
    payload = {"message": "Update", "content": encoded, "sha": sha}
    requests.put(url, data=json.dumps(payload), headers=headers)

# --- INITIALISATION ---
if "user" not in st.session_state: st.session_state.user = None
if "popup_closed" not in st.session_state: st.session_state.popup_closed = False
if "view" not in st.session_state: st.session_state.view = "chat"

# --- 1. LA POP-UP NÉON ---
if not st.session_state.popup_closed:
    st.markdown("""
        <div class="popup-overlay">
            <div class="popup-content">
                <h1 style="color:white; margin:0; font-size: 50px; letter-spacing: 5px;">HARTUR</h1>
                <p class="signature" style="color:#58a6ff; font-size: 18px;">Écrit par zacmite</p>
                <br>
                <p style="font-size: 20px; line-height: 1.6;">
                Je suis <b>Hartur</b>, une IA ninja optimisée pour la rapidité. <br>
                Zéro blabla, précision chirurgicale, efficacité brute. <br><br>
                <i>Ici, chaque seconde compte.</i>
                </p>
                <div style="height: 30px;"></div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Le bouton est placé ici pour être fonctionnel par-dessus l'interface
    if st.button("OK, C'EST PARTI"):
        st.session_state.popup_closed = True
        st.rerun()
    st.stop()

# --- 2. ADMIN DISCRET ⚙️ ---
col_l, col_adm = st.columns([0.95, 0.05])
with col_adm:
    if st.button("⚙️"):
        st.session_state.view = "admin_auth"
        st.rerun()

# --- 3. AUTHENTIFICATION ---
if st.session_state.view == "admin_auth":
    st.title("PROPRIÉTAIRE")
    c = st.text_input("Code maître", type="password")
    if st.button("DÉVERROUILLER"):
        if c == MASTER_CODE: st.session_state.view = "admin_panel"; st.rerun()
    if st.button("RETOUR"): st.session_state.view = "chat"; st.rerun()

elif st.session_state.view == "admin_panel":
    st.title("🛡️ Dashboard")
    df_c, _ = lire_github(FICHIER_COMPTES)
    st.table(df_c)
    if st.button("QUITTER"): st.session_state.view = "chat"; st.rerun()

elif st.session_state.user is None:
    st.title("ACCÈS SYSTÈME")
    st.markdown('<p class="signature">Écrit par zacmite</p>', unsafe_allow_html=True)
    t1, t2 = st.tabs(["CONNEXION", "INSCRIPTION"])
    with t1:
        u = st.text_input("Pseudo")
        p = st.text_input("Pass", type="password")
        if st.button("ENTRER"):
            df_c, _ = lire_github(FICHIER_COMPTES)
            if not df_c.empty and ((df_c['pseudo'].astype(str) == u) & (df_c['password'].astype(str) == p)).any():
                st.session_state.user = u
                st.rerun()
    with t2:
        nu = st.text_input("Nouveau pseudo")
        np = st.text_input("Nouveau pass", type="password")
        if st.button("S'INSCRIRE"):
            df_c, sha_c = lire_github(FICHIER_COMPTES)
            df_c = pd.concat([df_c, pd.DataFrame([{"pseudo": nu, "password": np}])], ignore_index=True)
            ecrire_github(FICHIER_COMPTES, df_c, sha_c)
            st.success("Accès créé !")

# --- 4. TERMINAL ---
else:
    st.title("HARTUR // TERMINAL")
    st.markdown('<p class="signature">Écrit par zacmite</p>', unsafe_allow_html=True)
    st.write("---")
    st.chat_input("Le ninja est prêt...")
