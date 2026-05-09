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

st.set_page_config(page_title="HARTUR", layout="wide", page_icon="🔥")

# --- DESIGN (POP-UP & ALIGNEMENT GAUCHE) ---
st.markdown("""
    <style>
    .stApp { background-color: #05070a; color: #e6edf3; }
    .block-container { padding-left: 2rem !important; max-width: 700px !important; margin-left: 0 !important; }
    
    .signature { color: #58a6ff; font-size: 14px; margin-top: -20px; margin-bottom: 20px; font-weight: bold; }
    
    /* Style de la Pop-up */
    .popup-overlay {
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0,0,0,0.85); z-index: 9999;
        display: flex; align-items: center; justify-content: center;
    }
    .popup-content {
        background: #0d1117; padding: 40px; border-radius: 10px;
        border: 1px solid #ff4b4b; max-width: 500px; text-align: left;
    }
    
    .stButton>button { background: #ff4b4b !important; color: white !important; border-radius: 5px; }
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

# --- INITIALISATION ---
if "user" not in st.session_state: st.session_state.user = None
if "popup_closed" not in st.session_state: st.session_state.popup_closed = False
if "view" not in st.session_state: st.session_state.view = "chat"

# --- 1. LA POP-UP DE BIENVENUE ---
if not st.session_state.popup_closed:
    st.markdown(f"""
        <div class="popup-overlay">
            <div class="popup-content">
                <h1 style="color:white; margin:0;">HARTUR</h1>
                <p style="color:#58a6ff; font-weight:bold; margin-bottom:20px;">Écrit par zacmite</p>
                <p><b>Description :</b> Je suis Hartur, une IA ninja conçue pour la rapidité et l'efficacité brute. Pas de filtres inutiles, juste du résultat.</p>
                <p><b>Pourquoi c'est une priorité ?</b> Parce que dans un monde de blabla, la précision chirurgicale est votre meilleure arme.</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Bouton Streamlit placé au-dessus pour fermer
    if st.button("OK, C'EST PARTI"):
        st.session_state.popup_closed = True
        st.rerun()
    st.stop()

# --- 2. NAVIGATION ET LOGO ADMIN DISCRET ⚙️ ---
col_logo, col_admin = st.columns([0.94, 0.06])
with col_admin:
    if st.button("⚙️"):
        st.session_state.view = "admin_auth"
        st.rerun()

# --- 3. LOGIQUE ADMIN ---
if st.session_state.view == "admin_auth":
    st.title("Accès Propriétaire")
    c = st.text_input("Code maître", type="password")
    if st.button("DÉVERROUILLER"):
        if c == MASTER_CODE: st.session_state.view = "admin_panel"; st.rerun()
    if st.button("RETOUR"): st.session_state.view = "chat"; st.rerun()

elif st.session_state.view == "admin_panel":
    st.title("🛡️ Dashboard")
    df_c, _ = lire_github(FICHIER_COMPTES)
    st.table(df_c)
    if st.button("QUITTER"): st.session_state.view = "chat"; st.rerun()

# --- 4. CONNEXION / INSCRIPTION ---
elif st.session_state.user is None:
    st.title("HARTUR // SYSTÈME")
    st.markdown('<p class="signature">Écrit par zacmite</p>', unsafe_allow_html=True)
    
    tab_c, tab_i = st.tabs(["Connexion", "Inscription"])
    with tab_c:
        u = st.text_input("Pseudo")
        p = st.text_input("Mot de passe", type="password")
        if st.button("ENTRER"):
            df_c, _ = lire_github(FICHIER_COMPTES)
            if not df_c.empty and ((df_c['pseudo'].astype(str) == u) & (df_c['password'].astype(str) == p)).any():
                st.session_state.user = u
                st.rerun()
    with tab_i:
        nu = st.text_input("Nouveau pseudo")
        np = st.text_input("Nouveau pass", type="password")
        if st.button("CRÉER MON COMPTE"):
            df_c, sha_c = lire_github(FICHIER_COMPTES)
            df_c = pd.concat([df_c, pd.DataFrame([{"pseudo": nu, "password": np}])], ignore_index=True)
            ecrire_github(FICHIER_COMPTES, df_c, sha_c)
            st.success("Compte validé !")

# --- 5. CHAT ---
else:
    st.title("HARTUR // TERMINAL")
    st.markdown('<p class="signature">Écrit par zacmite</p>', unsafe_allow_html=True)
    st.write("---")
    st.chat_input("Le ninja est prêt...")
