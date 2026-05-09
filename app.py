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

st.set_page_config(page_title="Hartur", layout="wide")

# --- STYLE CSS ---
st.markdown("""
    <style>
    .admin-btn { text-align: right; }
    .stChatMessage { border-radius: 15px; }
    </style>
    """, unsafe_allow_stdio=True)

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
    data = {"message": "Update Hartur", "content": encoded, "sha": sha}
    requests.put(url, data=json.dumps(data), headers=headers)

# --- FONCTION IA ---
def parler_a_ia(prompt, historique):
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {MISTRAL_API_KEY}", "Content-Type": "application/json"}
    system_msg = (
        "Tu es Hartur, un pote cool conçu par Zacharie pays. "
        "Pas de bière, pas de frigo. Réponds court et direct."
    )
    messages = [{"role": "system", "content": system_msg}]
    for m in historique[-5:]:
        messages.append({"role": m["role"], "content": m["content"]})
    messages.append({"role": "user", "content": prompt})
    try:
        response = requests.post(url, json={"model": "open-mistral-7b", "messages": messages}, headers=headers)
        return response.json()['choices'][0]['message']['content']
    except:
        return "Petit souci technique, réessaie."

# --- INITIALISATION ---
if "user" not in st.session_state: st.session_state.user = None
if "view" not in st.session_state: st.session_state.view = "chat"

# --- BARRE DE NAVIGATION HAUTE (ADMIN) ---
col_titre, col_admin = st.columns([0.9, 0.1])
with col_admin:
    if st.button("🔐 Admin"):
        st.session_state.view = "admin_auth"

# --- LOGIQUE D'AFFICHAGE ---

# 1. AUTHENTIFICATION ADMIN
if st.session_state.view == "admin_auth":
    st.title("Accès Restreint")
    code = st.text_input("Code secret", type="password")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Valider"):
            if code == "1234":
                st.session_state.view = "admin_panel"
                st.rerun()
            else: st.error("Code faux.")
    with col2:
        if st.button("Retour"):
            st.session_state.view = "chat"
            st.rerun()

# 2. PANNEAU ADMIN
elif st.session_state.view == "admin_panel":
    st.title("🛡️ Dashboard Admin")
    if st.button("⬅️ Retour au Chat"):
        st.session_state.view = "chat"
        st.rerun()
    
    df_glob, _ = lire_csv_github(FICHIER_HIST)
    df_c, _ = lire_csv_github(FICHIER_COMPTES)
    
    st.metric("Utilisateurs", len(df_c))
    
    st.subheader("Dernières activités")
    for u in df_glob['pseudo'].unique():
        last = df_glob[df_glob['pseudo'] == u].tail(2)
        with st.expander(f"Discussion de {u}"):
            for _, r in last.iterrows():
                st.write(f"**{r['role']}**: {r['content']}")

# 3. CONNEXION / INSCRIPTION USER
elif st.session_state.user is None:
    st.title("🤖 Bienvenue sur Hartur")
    t1, t2 = st.tabs(["Se connecter", "S'inscrire"])
    with t1:
        u = st.text_input("Pseudo", key="u1")
        p = st.text_input("Pass", type="password", key="p1")
        if st.button("Connexion"):
            df_c, _ = lire_csv_github(FICHIER_COMPTES)
            if not df_c.empty and ((df_c['pseudo'].astype(str) == u) & (df_c['password'].astype(str) == p)).any():
                st.session_state.user = u
                st.rerun()
    with t2:
        ui = st.text_input("Ton nom", key="u2")
        pi = st.text_input("Ton pass", type="password", key="p2")
        if st.button("Créer compte"):
            df_c, sha_c = lire_csv_github(FICHIER_COMPTES)
            if ui.lower() in df_c['pseudo'].astype(str).str.lower().values: st.error("Déjà pris.")
            elif ui and pi:
                df_c = pd.concat([df_c, pd.DataFrame([{"pseudo": ui, "password": pi}])], ignore_index=True)
                ecrire_csv_github(FICHIER_COMPTES, df_c, sha_c)
                st.success("Compte créé !")

# 4. CHAT PRINCIPAL
else:
    st.title(f"Salut {st.session_state.user}")
    df_glob, sha_glob = lire_csv_github(FICHIER_HIST)
    
    # Historique
    hist = df_glob[df_glob['pseudo'] == st.session_state.user].to_dict('records')
    for m in hist:
        with st.chat_message(m["role"]): st.write(m["content"])
    
    # Input
    prompt = st.chat_input("Dis-moi tout...")
    if prompt:
        with st.chat_message("user"): st.write(prompt)
        df_glob = pd.concat([df_glob, pd.DataFrame([{"pseudo": st.session_state.user, "role": "user", "content": prompt}])], ignore_index=True)
        ecrire_csv_github(FICHIER_HIST, df_glob, sha_glob)
        
        rep = parler_a_ia(prompt, hist)
        with st.chat_message("assistant"): st.write(rep)
        
        _, sha_n = lire_csv_github(FICHIER_HIST)
        df_glob = pd.concat([df_glob, pd.DataFrame([{"pseudo": st.session_state.user, "role": "assistant", "content": rep}])], ignore_index=True)
        ecrire_csv_github(FICHIER_HIST, df_glob, sha_n)
