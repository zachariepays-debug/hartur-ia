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
    .stChatMessage { border-radius: 15px; }
    .locked-bg { background-color: black; height: 100vh; width: 100vw; position: fixed; top: 0; left: 0; z-index: 9999; display: flex; align-items: center; justify-content: center; color: white; flex-direction: column; }
    /* Style pour le tableau des comptes */
    .account-table { width: 100%; border-collapse: collapse; margin-top: 10px; }
    .account-table td, .account-table th { border: 1px solid #ff4b4b; padding: 10px; color: white; }
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
    data = {"message": "Admin Update", "content": encoded, "sha": sha}
    requests.put(url, data=json.dumps(data), headers=headers)

# --- ÉCRAN NOIR (KILL SWITCH) ---
if not st.session_state.is_active:
    st.markdown('<div class="locked-bg">', unsafe_allow_html=True)
    st.title("HARTUR EST HORS-LIGNE")
    unlock_code = st.text_input("Code de réactivation", type="password", key="unlock")
    if st.button("RÉACTIVER HARTUR"):
        if unlock_code == "1234":
            st.session_state.is_active = True
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- IA ---
def parler_a_ia(prompt, historique):
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {MISTRAL_API_KEY}", "Content-Type": "application/json"}
    system_msg = "Tu es Hartur, créé par Zacharie pays. Percutant et direct."
    messages = [{"role": "system", "content": system_msg}]
    for m in historique[-10:]: messages.append({"role": m["role"], "content": m["content"]})
    messages.append({"role": "user", "content": prompt})
    try:
        response = requests.post(url, json={"model": "mistral-medium", "messages": messages}, headers=headers)
        return response.json()['choices'][0]['message']['content']
    except: return "Système en pause..."

# --- NAVIGATION ---
c1, c2 = st.columns([0.88, 0.12])
with c2:
    if st.button("🔐 ADMIN"): st.session_state.view = "admin_auth"

if st.session_state.view == "admin_auth":
    st.title("Accès Propriétaire")
    code = st.text_input("Code secret", type="password")
    if st.button("DÉVERROUILLER"):
        if code == "1234": st.session_state.view = "admin_panel"; st.rerun()
    if st.button("RETOUR"): st.session_state.view = "chat"; st.rerun()

elif st.session_state.view == "admin_panel":
    st.title("🛡️ Centre de Contrôle")
    
    if st.button("🚨 ÉTEINDRE HARTUR (KILL SWITCH)"):
        st.session_state.is_active = False
        st.session_state.view = "chat"
        st.rerun()

    if st.button("⬅️ RETOUR AU CHAT"): st.session_state.view = "chat"; st.rerun()
    
    df_glob, _ = lire_csv_github(FICHIER_HIST)
    df_c, _ = lire_csv_github(FICHIER_COMPTES)
    
    # --- SECTION RÉPERTOIRE DES COMPTES (LA MODIFICATION EST ICI) ---
    st.subheader("🗂️ Répertoire des Comptes")
    with st.expander("Ouvrir le dossier des comptes"):
        if not df_c.empty:
            # On affiche tout d'un coup dans un tableau propre
            st.table(df_c[['pseudo', 'password']])
        else:
            st.write("Aucun utilisateur inscrit.")
    
    st.divider()

    # --- ARCHIVES ---
    st.subheader("📁 Archives des Conversations")
    u_liste = df_glob['pseudo'].unique().tolist()
    u_choisi = st.selectbox("Membre :", ["..."] + u_liste)
    if u_choisi != "...":
        df_u = df_glob[df_glob['pseudo'] == u_choisi]
        for _, r in df_u.iterrows():
            if r['role'] == "user": st.info(f"**👤 {u_choisi} :** {r['content']}")
            else: st.success(f"**🤖 Hartur :** {r['content']}")

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
        ui = st.text_input("Nom", key="r_u"); pi = st.text_input("Mot de passe", type="password", key="r_p")
        if st.button("CRÉER MON ACCÈS"):
            df_c, sha_c = lire_csv_github(FICHIER_COMPTES)
            if ui and pi:
                df_c = pd.concat([df_c, pd.DataFrame([{"pseudo": ui, "password": pi}])], ignore_index=True)
                ecrire_csv_github(FICHIER_COMPTES, df_c, sha_c); st.success("Accès créé !")

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
