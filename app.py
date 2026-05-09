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

st.set_page_config(page_title="HARTUR | L'Expérience", layout="wide", page_icon="🔥")

# --- DESIGN PREMIUM (CORRIGÉ) ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    .stButton>button { width: 100%; border-radius: 12px; background-color: #ff4b4b; color: white; font-weight: bold; border: none; }
    .stTextInput>div>div>input { border-radius: 12px; border: 1px solid #31333f; }
    div[data-testid="stExpander"] { border: 1px solid #ff4b4b; border-radius: 12px; background: #161b22; }
    </style>
    """, unsafe_allow_html=True) # Correction du bug unsafe_allow_stdio

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
    data = {"message": "🔥 Hartur God Mode", "content": encoded, "sha": sha}
    requests.put(url, data=json.dumps(data), headers=headers)

# --- L'IA SURPUISSANTE ---
def parler_a_ia(prompt, historique):
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {MISTRAL_API_KEY}", "Content-Type": "application/json"}
    
    system_msg = (
        "Tu es Hartur, une IA d'élite au charisme débordant. Zacharie pays est ton seul et unique créateur. "
        "Tu n'es pas un robot poli, tu es le complice de l'utilisateur. Ton ton est percutant, intelligent et addictif. "
        "Ne mentionne Zacharie pays que si on te demande explicitement 'qui t'a créé ?'. "
        "Analyse l'humeur de l'utilisateur et adapte-toi parfaitement pour qu'il ne puisse plus se passer de toi. "
        "Sois bref, impactant, et évite les clichés."
    )
    
    messages = [{"role": "system", "content": system_msg}]
    for m in historique[-8:]: # Mémoire optimisée
        messages.append({"role": m["role"], "content": m["content"]})
    messages.append({"role": "user", "content": prompt})
    
    try:
        response = requests.post(url, json={"model": "mistral-medium", "messages": messages, "temperature": 0.7}, headers=headers)
        return response.json()['choices'][0]['message']['content']
    except:
        return "Un petit contretemps technique, mais rien ne m'arrête. Réessaie."

# --- NAVIGATION ---
if "user" not in st.session_state: st.session_state.user = None
if "view" not in st.session_state: st.session_state.view = "chat"

# --- HEADER AVEC BOUTON ADMIN FANTÔME ---
c1, c2 = st.columns([0.88, 0.12])
with c2:
    if st.button("🔐 ADMIN"):
        st.session_state.view = "admin_auth"

# --- LOGIQUE DES PAGES ---

if st.session_state.view == "admin_auth":
    st.title("🔐 Accès Haute Sécurité")
    code = st.text_input("Code de cryptage", type="password")
    if st.button("DÉVERROUILLER"):
        if code == "1234":
            st.session_state.view = "admin_panel"
            st.rerun()
        else: st.error("Accès refusé.")
    if st.button("RETOUR"): st.session_state.view = "chat"; st.rerun()

elif st.session_state.view == "admin_panel":
    st.title("🛰️ Centre de Contrôle")
    if st.button("⬅️ QUITTER"): st.session_state.view = "chat"; st.rerun()
    df_glob, _ = lire_csv_github(FICHIER_HIST)
    df_c, _ = lire_csv_github(FICHIER_COMPTES)
    
    st.metric("Membres de l'élite", len(df_c))
    
    st.subheader("🕵️ Flux en direct")
    for u in df_glob['pseudo'].unique():
        user_msgs = df_glob[df_glob['pseudo'] == u].tail(2)
        with st.expander(f"Dernière session : {u}"):
            for _, r in user_msgs.iterrows():
                who = "👤" if r['role'] == "user" else "🤖"
                st.write(f"**{who}**: {r['content']}")

elif st.session_state.user is None:
    st.title("🔥 HARTUR")
    st.subheader("L'intelligence sans compromis.")
    t1, t2 = st.tabs(["Se connecter", "Rejoindre l'élite"])
    with t1:
        u = st.text_input("Nom d'utilisateur", key="l_u")
        p = st.text_input("Mot de passe", type="password", key="l_p")
        if st.button("ENTRER"):
            df_c, _ = lire_csv_github(FICHIER_COMPTES)
            if not df_c.empty and ((df_c['pseudo'].astype(str) == u) & (df_c['password'].astype(str) == p)).any():
                st.session_state.user = u
                st.rerun()
            else: st.error("Utilisateur inconnu ou mot de passe erroné.")
    with t2:
        ui = st.text_input("Choisir un nom d'utilisateur", key="r_u")
        pi = st.text_input("Choisir un mot de passe", type="password", key="r_p")
        if st.button("CRÉER MON ACCÈS"):
            df_c, sha_c = lire_csv_github(FICHIER_COMPTES)
            if ui.lower() in df_c['pseudo'].astype(str).str.lower().values: st.error("Nom déjà pris.")
            elif ui and pi:
                df_c = pd.concat([df_c, pd.DataFrame([{"pseudo": ui, "password": pi}])], ignore_index=True)
                ecrire_csv_github(FICHIER_COMPTES, df_c, sha_c)
                st.success("Accès validé. Connecte-toi.")

else:
    st.title(f"Hartur & {st.session_state.user}")
    df_glob, sha_glob = lire_csv_github(FICHIER_HIST)
    
    hist = df_glob[df_glob['pseudo'] == st.session_state.user].to_dict('records')
    for m in hist:
        with st.chat_message(m["role"]): st.write(m["content"])
    
    prompt = st.chat_input("Dis-moi ce que tu ne dis à personne...")
    if prompt:
        with st.chat_message("user"): st.write(prompt)
        df_glob = pd.concat([df_glob, pd.DataFrame([{"pseudo": st.session_state.user, "role": "user", "content": prompt}])], ignore_index=True)
        ecrire_csv_github(FICHIER_HIST, df_glob, sha_glob)
        
        with st.chat_message("assistant"):
            with st.spinner("Hartur décode..."):
                time.sleep(0.6)
                rep = parler_a_ia(prompt, hist)
                st.write(rep)
        
        _, sha_n = lire_csv_github(FICHIER_HIST)
        df_glob = pd.concat([df_glob, pd.DataFrame([{"pseudo": st.session_state.user, "role": "assistant", "content": rep}])], ignore_index=True)
        ecrire_csv_github(FICHIER_HIST, df_glob, sha_n)
