import streamlit as st
import pandas as pd
import requests
import base64
import json
from io import StringIO

# --- CONFIGURATION AUTOMATIQUE ---
REPO_NOM = "zachariepays-debug/Hartur-ia" 
FICHIER_HIST = "historique.csv"
FICHIER_COMPTES = "comptes.csv"

# Récupération des clés dans les Secrets Streamlit
MISTRAL_API_KEY = st.secrets["MISTRAL_KEY"]
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]

st.set_page_config(page_title="Hartur", layout="centered")

# --- FONCTIONS GITHUB (SAUVEGARDE ÉTERNELLE) ---

def lire_csv_github(nom_fichier):
    url = f"https://api.github.com/repos/{REPO_NOM}/contents/{nom_fichier}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        content = r.json()
        decoded = base64.b64decode(content['content']).decode('utf-8')
        return pd.read_csv(StringIO(decoded)), content['sha']
    return pd.DataFrame(columns=["pseudo", "role", "content"]), None

def ecrire_csv_github(nom_fichier, df, sha):
    url = f"https://api.github.com/repos/{REPO_NOM}/contents/{nom_fichier}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    csv_content = df.to_csv(index=False)
    encoded = base64.b64encode(csv_content.encode('utf-8')).decode('utf-8')
    
    data = {
        "message": "Mise à jour historique par Hartur",
        "content": encoded,
        "sha": sha
    }
    requests.put(url, data=json.dumps(data), headers=headers)

# --- FONCTION IA ---
def parler_a_ia(prompt, historique):
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {MISTRAL_API_KEY}"}
    
    system_msg = "Tu es Hartur, un pote proche. Parle normalement, sois direct, un peu brut mais toujours là pour écouter. Pas de politesse forcée, sois vrai."
    messages = [{"role": "system", "content": system_msg}]
    
    for m in historique[-6:]:
        messages.append({"role": m["role"], "content": m["content"]})
    messages.append({"role": "user", "content": prompt})
    
    try:
        response = requests.post(url, json={"model": "mistral-small", "messages": messages}, headers=headers)
        return response.json()['choices'][0]['message']['content']
    except:
        return "Désolé gros, j'ai un bug de connexion à l'IA."

# --- LOGIQUE DE SESSION ---
if "user" not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    st.title("🤖 Hartur")
    p_co = st.text_input("Pseudo")
    m_co = st.text_input("Mot de passe", type="password")
    if st.button("Se connecter"):
        df_comptes, _ = lire_csv_github(FICHIER_COMPTES)
        if not df_comptes.empty and ((df_comptes['pseudo'].astype(str) == str(p_co)) & (df_comptes['password'].astype(str) == str(m_co))).any():
            st.session_state.user = p_co
            st.rerun()
        else:
            st.error("Inconnu, t'es qui ?")
else:
    # Charger l'historique
    df_glob, sha_glob = lire_csv_github(FICHIER_HIST)
    user_hist_df = df_glob[df_glob['pseudo'] == st.session_state.user]
    user_hist_list = user_hist_df.to_dict('records')

    with st.sidebar:
        st.write(f"Utilisateur : **{st.session_state.user}**")
        if st.button("Se déconnecter"):
            st.session_state.user = None
            st.rerun()
        st.divider()
        with st.expander("🛡️ Admin"):
            if st.text_input("Code", type="password") == "1234":
                st.dataframe(df_glob)

    st.title("Discussion")

    for msg in user_hist_list:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    prompt = st.chat_input("Dis-moi tout...")
    if prompt:
        with st.chat_message("user"):
            st.write(prompt)
        
        # 1. Sauvegarde utilisateur
        new_row = pd.DataFrame([{"pseudo": st.session_state.user, "role": "user", "content": prompt}])
        df_glob = pd.concat([df_glob, new_row], ignore_index=True)
        ecrire_csv_github(FICHIER_HIST, df_glob, sha_glob)
        
        # 2. Récupérer nouveau SHA pour la réponse IA
        _, sha_neuf = lire_csv_github(FICHIER_HIST)
        
        # 3. Réponse IA
        reponse = parler_a_ia(prompt, user_hist_list)
        with st.chat_message("assistant"):
            st.write(reponse)
            
        # 4. Sauvegarde réponse IA
        new_row_ia = pd.DataFrame([{"pseudo": st.session_state.user, "role": "assistant", "content": reponse}])
        df_glob = pd.concat([df_glob, new_row_ia], ignore_index=True)
        ecrire_csv_github(FICHIER_HIST, df_glob, sha_neuf)
