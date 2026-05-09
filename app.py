import streamlit as st
import pandas as pd
import requests
import base64
import json
import time
from io import StringIO

# --- CONFIGURATION ---
REPO_NOM = "zachariepays-debug/Hartur-ia" 
FICHIER_HIST = "historique.csv"
FICHIER_COMPTES = "comptes.csv"

MISTRAL_API_KEY = st.secrets["MISTRAL_KEY"]
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]

# LE NOUVEAU MOT DE PASSE MAÎTRE
MASTER_CODE = "babar"

st.set_page_config(page_title="HARTUR", layout="wide", page_icon="🔥")

# --- INITIALISATION ---
if "user" not in st.session_state: st.session_state.user = None
if "view" not in st.session_state: st.session_state.view = "chat"
if "is_active" not in st.session_state: st.session_state.is_active = True

# --- DESIGN ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    .stButton>button { width: 100%; border-radius: 12px; font-weight: bold; }
    .locked-container {
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        background-color: black; z-index: 9999;
        display: flex; flex-direction: column; align-items: center; justify-content: center;
    }
    .stTextInput>div>div>input { text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- FONCTIONS GITHUB ---
def lire_csv_github(nom_fichier):
    url = f"https://api.github.com/repos/{REPO_NOM}/contents/{nom_fichier}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        content = r.json()
        decoded = base64.b64decode(content['content']).decode('utf-8')
        return pd.read_csv(StringIO(decoded)), content['sha']
    return pd.DataFrame(columns=["pseudo", "password", "role", "content"]), None

def ecrire_csv_github(nom_fichier, df, sha):
    url = f"https://api.github.com/repos/{REPO_NOM}/contents/{nom_fichier}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    csv_content = df.to_csv(index=False)
    encoded = base64.b64encode(csv_content.encode('utf-8')).decode('utf-8')
    data = {"message": "Security Update", "content": encoded, "sha": sha}
    requests.put(url, data=json.dumps(data), headers=headers)

# --- LOGIQUE DU KILL SWITCH (ÉCRAN NOIR) ---
if not st.session_state.is_active:
    st.markdown('<div class="locked-container">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h3 style='color: white; text-align: center;'>SYSTÈME EN PAUSE</h3>", unsafe_allow_html=True)
        code_on = st.text_input("Code de réactivation", type="password", key="wake_up")
        if st.button("RÉACTIVER HARTUR"):
            if code_on == MASTER_CODE:
                st.session_state.is_active = True
                st.rerun()
            else: st.error("Code incorrect.")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- IA ---
def parler_a_ia(prompt, historique):
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {MISTRAL_API_KEY}", "Content-Type": "application/json"}
    system_msg = "Tu es Hartur, créé par Zacharie pays. Tu es une IA d'élite, percutante et addictive."
    messages = [{"role": "system", "content": system_msg}]
    for m in historique[-10:]: messages.append({"role": m["role"], "content": m["content"]})
    messages.append({"role": "user", "content": prompt})
    try:
        response = requests.post(url, json={"model": "mistral-medium", "messages": messages}, headers=headers)
        return response.json()['choices'][0]['message']['content']
    except: return "Hartur réfléchit..."

# --- NAVIGATION ---
c1, c2 = st.columns([0.88, 0.12])
with c2:
    if st.button("🔐 ADMIN"): st.session_state.view = "admin_auth"

# 1. AUTH ADMIN
if st.session_state.view == "admin_auth":
    st.title("Accès Propriétaire")
    c = st.text_input("Entrez le mot de passe admin", type="password")
    if st.button("DÉVERROUILLER"):
        if c == MASTER_CODE:
            st.session_state.view = "admin_panel"
            st.rerun()
        else: st.error("Code erroné.")
    if st.button("RETOUR"): st.session_state.view = "chat"; st.rerun()

# 2. PANNEAU ADMIN
elif st.session_state.view == "admin_panel":
    st.title("🛡️ Dashboard de Contrôle")
    
    with st.expander("🚨 ÉTEINDRE HARTUR"):
        st.write("Confirmez l'extinction avec le code secret.")
        code_off = st.text_input("Code de confirmation", type="password", key="kill_confirm")
        if st.button("CONFIRMER L'EXTINCTION"):
            if code_off == MASTER_CODE:
                st.session_state.is_active = False
                st.session_state.view = "chat"
                st.rerun()
            else: st.error("Code incorrect.")

    if st.button("⬅️ RETOUR AU CHAT"): st.session_state.view = "chat"; st.rerun()
    
    df_glob, _ = lire_csv_github(FICHIER_HIST)
    df_c, _ = lire_csv_github(FICHIER_COMPTES)
    
    st.subheader("🗂️ Répertoire des Comptes")
    with st.expander("Ouvrir le dossier"):
        st.table(df_c[['pseudo', 'password']])
    
    st.subheader("📁 Archives Conversations")
    u_liste = df_glob['pseudo'].unique().tolist()
    choix = st.selectbox("Membre :", ["..."] + u_liste)
    if choix != "...":
        df_u = df_glob[df_glob['pseudo'] == choix]
        for _, r in df_u.iterrows():
            if r['role'] == "user": st.info(f"**Question de {choix} :** {r['content']}")
            else: st.success(f"**Réponse de Hartur :** {r['content']}")

# 3. CONNEXION / INSCRIPTION
elif st.session_state.user is None:
    st.title("🔥 HARTUR")
    t1, t2 = st.tabs(["Connexion", "Inscription"])
    with t1:
        u = st.text_input("Nom d'utilisateur", key="l_u")
        p = st.text_input("Mot de passe", type="password", key="l_p")
        if st.button("ENTRER"):
            df_c, _ = lire_csv_github(FICHIER_COMPTES)
            if not df_c.empty and ((df_c['pseudo'].astype(str) == u) & (df_c['password'].astype(str) == p)).any():
                st.session_state.user = u; st.rerun()
    with t2:
        ui = st.text_input("Nouveau pseudo", key="r_u")
        pi = st.text_input("Nouveau mot de passe", type="password", key="r_p")
        if st.button("CRÉER MON ACCÈS"):
            df_c, sha_c = lire_csv_github(FICHIER_COMPTES)
            if ui and pi:
                df_c = pd.concat([df_c, pd.DataFrame([{"pseudo": ui, "password": pi}])], ignore_index=True)
                ecrire_csv_github(FICHIER_COMPTES, df_c, sha_c); st.success("Accès créé !")

# 4. CHAT
else:
    st.title(f"Hartur & {st.session_state.user}")
    df_glob, sha_glob = lire_csv_github(FICHIER_HIST)
    hist = df_glob[df_glob['pseudo'] == st.session_state.user].to_dict('records')
    for m in hist:
        with st.chat_message(m["role"]): st.write(m["content"])
    
    prompt = st.chat_input("Dis-moi tout...")
    if prompt:
        with st.chat_message("user"): st.write(prompt)
        df_glob = pd.concat([df_glob, pd.DataFrame([{"pseudo": st.session_state.user, "role": "user", "content": prompt}])], ignore_index=True)
        ecrire_csv_github(FICHIER_HIST, df_glob, sha_glob)
        with st.chat_message("assistant"):
            rep = parler_a_ia(prompt, hist); st.write(rep)
        _, sha_n = lire_csv_github(FICHIER_HIST)
        df_glob = pd.concat([df_glob, pd.DataFrame([{"pseudo": st.session_state.user, "role": "assistant", "content": rep}])], ignore_index=True)
        ecrire_csv_github(FICHIER_HIST, df_glob, sha_n)
