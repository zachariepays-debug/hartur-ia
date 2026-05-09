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

st.set_page_config(page_title="HARTUR | L'IA ULTIME", layout="wide", page_icon="🔥")

# --- DESIGN "CYBER-DYNAMIQUE" ---
st.markdown("""
    <style>
    .stApp { background-color: #05070a; color: #e6edf3; }
    
    .signature { color: #58a6ff; font-size: 18px; font-weight: bold; text-shadow: 0 0 10px rgba(88, 166, 255, 0.5); }
    
    /* Overlay sombre */
    .popup-overlay {
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background: radial-gradient(circle, rgba(13,17,23,0.98) 0%, rgba(0,0,0,1) 100%);
        z-index: 9999; display: flex; align-items: center; justify-content: center;
    }
    
    /* Pop-up Format Cinéma */
    .popup-content {
        background: #0d1117; padding: 50px; border-radius: 20px;
        border: 2px solid #ff4b4b; width: 85%; max-width: 900px;
        text-align: center; box-shadow: 0px 0px 60px rgba(255, 75, 75, 0.4);
    }
    
    .giant-title { font-size: 80px; font-weight: 900; letter-spacing: 15px; margin: 0; color: white; text-shadow: 0 0 20px rgba(255, 75, 75, 0.5); }

    /* Liste des Capacités */
    .capability-list { text-align: left; display: inline-block; font-size: 18px; line-height: 1.8; margin-top: 20px; color: #c9d1d9; }
    .capability-list b { color: #ff4b4b; }

    /* Bouton Spectaculaire */
    div.stButton > button {
        background: linear-gradient(90deg, #ff4b4b, #8b0000) !important;
        color: white !important; border: none !important;
        padding: 20px 80px !important; font-size: 26px !important;
        font-weight: 900 !important; border-radius: 50px !important;
        box-shadow: 0px 0px 30px rgba(255, 75, 75, 0.6) !important;
        text-transform: uppercase; cursor: pointer; transition: 0.5s;
    }
    div.stButton > button:hover { transform: scale(1.1); box-shadow: 0px 0px 50px rgba(255, 75, 75, 0.9) !important; }
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
    payload = {"message": "System Update", "content": encoded, "sha": sha}
    requests.put(url, data=json.dumps(payload), headers=headers)

# --- INITIALISATION ---
if "user" not in st.session_state: st.session_state.user = None
if "popup_closed" not in st.session_state: st.session_state.popup_closed = False
if "view" not in st.session_state: st.session_state.view = "chat"

# --- 1. L'INTERFACE DE PRÉSENTATION TOTALE ---
if not st.session_state.popup_closed:
    st.markdown("""
        <div class="popup-overlay">
            <div class="popup-content">
                <h1 class="giant-title">HARTUR</h1>
                <p class="signature">Écrit par zacmite</p>
                <div class="capability-list">
                    🔥 <b>Vitesse :</b> Réponses instantanées sans temps mort.<br>
                    🛡️ <b>Sécurité :</b> Terminal verrouillé et conversations chiffrées.<br>
                    🧠 <b>Multi-Talents :</b> Code, analyse de données, rédaction et brainstorming.<br>
                    🤖 <b>Pote du Futur :</b> Un compagnon qui apprend de vos besoins.<br>
                    ⚡ <b>Zéro Filtre :</b> Une liberté d'expression totale pour des résultats bruts.
                </div>
                <br><br>
                <p style="font-size: 22px; color: #8b949e;"><i>Prêt à libérer la puissance du terminal ?</i></p>
                <div style="height: 20px;"></div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("ENTRER DANS LE SYSTÈME"):
            st.session_state.popup_closed = True
            st.rerun()
    st.stop()

# --- 2. NAVIGATION ADMIN ---
c1, c2 = st.columns([0.96, 0.04])
with c2:
    if st.button("⚙️"):
        st.session_state.view = "admin_auth"
        st.rerun()

# --- 3. CONNEXION / INSCRIPTION ---
if st.session_state.user is None and st.session_state.view == "chat":
    st.title("AUTHENTIFICATION REQUISE")
    st.markdown('<p class="signature">Écrit par zacmite</p>', unsafe_allow_html=True)
    t1, t2 = st.tabs(["CONNEXION", "CRÉER UN ACCÈS"])
    with t1:
        u = st.text_input("Pseudo")
        p = st.text_input("Code Secret", type="password")
        if st.button("DÉVERROUILLER"):
            df_c, _ = lire_github(FICHIER_COMPTES)
            if not df_c.empty and ((df_c['pseudo'].astype(str) == u) & (df_c['password'].astype(str) == p)).any():
                st.session_state.user = u
                st.rerun()
    with t2:
        nu = st.text_input("Nouveau pseudo")
        np = st.text_input("Nouveau pass", type="password")
        if st.button("CRÉER MON ACCÈS"):
            df_c, sha_c = lire_github(FICHIER_COMPTES)
            df_c = pd.concat([df_c, pd.DataFrame([{"pseudo": nu, "password": np}])], ignore_index=True)
            ecrire_github(FICHIER_COMPTES, df_c, sha_c)
            st.success("Accès créé avec succès.")

# --- 4. PANNEAU ADMIN ---
elif st.session_state.view == "admin_auth":
    st.title("PROPRIÉTAIRE")
    ac = st.text_input("Code maître", type="password")
    if st.button("ACCÈS"):
        if ac == MASTER_CODE: st.session_state.view = "admin_panel"; st.rerun()
    if st.button("RETOUR"): st.session_state.view = "chat"; st.rerun()

elif st.session_state.view == "admin_panel":
    st.title("🛡️ Dashboard")
    df_c, _ = lire_github(FICHIER_COMPTES)
    st.table(df_c)
    if st.button("FERMER"): st.session_state.view = "chat"; st.rerun()

# --- 5. TERMINAL ---
else:
    st.title("HARTUR // TERMINAL")
    st.markdown('<p class="signature">Écrit par zacmite</p>', unsafe_allow_html=True)
    st.write("---")
    st.chat_input("Le système est à vos ordres...")
