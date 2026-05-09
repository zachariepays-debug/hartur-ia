import streamlit as st
import pandas as pd
import requests
import base64
import json
from io import StringIO

# --- CONFIGURATION ---
REPO_NOM = "zachariepays-debug/Hartur-ia" 
FICHIER_HIST = "historique.csv"
FICHIER_COMPTES = "comptes.csv"

MISTRAL_API_KEY = st.secrets["MISTRAL_KEY"]
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]

st.set_page_config(page_title="Hartur", layout="wide") 

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

# --- FONCTION IA (NETTOYAGE COMPLET) ---
def parler_a_ia(prompt, historique):
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {MISTRAL_API_KEY}", "Content-Type": "application/json"}
    
    # On enlève tout le blabla inutile ici
    system_msg = (
        "Tu es Hartur, un pote direct et cool conçu par Zacharie pays. "
        "INTERDICTION de parler de bière, de foot, de télé ou de frigo. "
        "Ne dis 'Zacharie pays' QUE si on te demande 'qui t'a créé ?'. "
        "Réponds de manière brève et naturelle, comme un SMS entre potes."
    )
    
    messages = [{"role": "system", "content": system_msg}]
    for m in historique[-5:]:
        messages.append({"role": m["role"], "content": m["content"]})
    messages.append({"role": "user", "content": prompt})
    
    try:
        response = requests.post(url, json={"model": "open-mistral-7b", "messages": messages}, headers=headers)
        return response.json()['choices'][0]['message']['content']
    except:
        return "Bug de connexion, réessaie gros."

# --- LOGIQUE ---
if "user" not in st.session_state:
    st.session_state.user = None
if "view" not in st.session_state:
    st.session_state.view = "chat"

if st.session_state.user is None:
    st.title("🤖 Hartur")
    onglet_co, onglet_ins = st.tabs(["Connexion", "Inscription"])
    with onglet_co:
        p = st.text_input("Pseudo", key="lp")
        m = st.text_input("Pass", type="password", key="lm")
        if st.button("Go"):
            df_c, _ = lire_csv_github(FICHIER_COMPTES)
            if not df_c.empty and ((df_c['pseudo'].astype(str) == str(p)) & (df_c['password'].astype(str) == str(m))).any():
                st.session_state.user = p
                st.rerun()
    with onglet_ins:
        pi = st.text_input("Nouveau Pseudo", key="ip").strip()
        mi = st.text_input("Nouveau Pass", type="password", key="im")
        if st.button("Créer"):
            df_c, sha_c = lire_csv_github(FICHIER_COMPTES)
            if pi.lower() in df_c['pseudo'].astype(str).str.lower().values:
                st.error("Déjà pris.")
            elif pi and mi:
                df_c = pd.concat([df_c, pd.DataFrame([{"pseudo": pi, "password": mi}])], ignore_index=True)
                ecrire_csv_github(FICHIER_COMPTES, df_c, sha_c)
                st.success("Compte OK !")

else:
    df_glob, sha_glob = lire_csv_github(FICHIER_HIST)
    
    with st.sidebar:
        if st.button("💬 Chat"): st.session_state.view = "chat"; st.rerun()
        st.divider()
        if st.text_input("Admin", type="password") == "1234":
            if st.button("📊 Dashboard"): st.session_state.view = "admin"; st.rerun()
        st.divider()
        if st.button("Quitter"): st.session_state.user = None; st.rerun()

    # --- PAGE ADMIN (MISE À JOUR) ---
    if st.session_state.view == "admin":
        st.title("🛡️ Dashboard Admin")
        
        st.subheader("⚡ Derniers échanges par utilisateur")
        if not df_glob.empty:
            # On regroupe par utilisateur et on prend les deux derniers messages (User + IA)
            for user in df_glob['pseudo'].unique():
                df_u = df_glob[df_glob['pseudo'] == user].tail(2)
                with st.expander(f"Dernière activité de {user}"):
                    for _, row in df_u.iterrows():
                        label = f"👤 {user}" if row['role'] == 'user' else "🤖 Hartur"
                        st.write(f"**{label}** : {row['content']}")
        
        st.divider()
        u_choisi = st.selectbox("Dossier complet :", ["..."] + df_glob['pseudo'].unique().tolist())
        if u_choisi != "...":
            df_p = df_glob[df_glob['pseudo'] == u_choisi]
            for _, r in df_p.iloc[::-1].iterrows():
                if r['role'] == 'user': st.info(f"**{u_choisi}** : {r['content']}")
                else: st.success(f"**Hartur** : {r['content']}")

    # --- PAGE CHAT ---
    else:
        st.title("Chat")
        hist = df_glob[df_glob['pseudo'] == st.session_state.user].to_dict('records')
        for m in hist:
            with st.chat_message(m["role"]): st.write(m["content"])
        
        p = st.chat_input("Dis-moi...")
        if p:
            with st.chat_message("user"): st.write(p)
            df_glob = pd.concat([df_glob, pd.DataFrame([{"pseudo": st.session_state.user, "role": "user", "content": p}])], ignore_index=True)
            ecrire_csv_github(FICHIER_HIST, df_glob, sha_glob)
            
            r = parler_a_ia(p, hist)
            with st.chat_message("assistant"): st.write(r)
            _, sha_n = lire_csv_github(FICHIER_HIST)
            df_glob = pd.concat([df_glob, pd.DataFrame([{"pseudo": st.session_state.user, "role": "assistant", "content": r}])], ignore_index=True)
            ecrire_csv_github(FICHIER_HIST, df_glob, sha_n)
