import streamlit as st
import pandas as pd
import requests
import base64
import json
from io import StringIO

# --- CONFIGURATION À MODIFIER ---
# REMPLACE BIEN ICI PAR TON PSEUDO ET LE NOM DE TON PROJET GITHUB
# Exemple: "Zach/hartur-ia"
REPO_NOM = "TON_PSEUDO/TON_PROJET" 

# On récupère tes clés que tu as mises dans les Secrets
MISTRAL_API_KEY = st.secrets["MISTRAL_KEY"]
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]

st.set_page_config(page_title="Hartur", layout="centered")

# --- FONCTIONS POUR GITHUB ---

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
        "message": "Sauvegarde automatique Hartur",
        "content": encoded,
        "sha": sha
    }
    requests.put(url, data=json.dumps(data), headers=headers)

# --- FONCTION IA (TON POTE HARTUR) ---
def parler_a_ia(prompt, historique):
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {MISTRAL_API_KEY}"}
    system_msg = "Tu es Hartur, un pote proche. Pas de politesse, sois direct, un peu vulgaire si besoin mais reste cool. Tu es là pour qu'on se confie à toi."
    
    messages = [{"role": "system", "content": system_msg}]
    for m in historique[-6:]:
        messages.append({"role": m["role"], "content": m["content"]})
    messages.append({"role": "user", "content": prompt})
    
    try:
        response = requests.post(url, json={"model": "mistral-small", "messages": messages}, headers=headers)
        return response.json()['choices'][0]['message']['content']
    except:
        return "Gros, j'ai un bug technique là."

# --- INTERFACE ---
if "user" not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    st.title("🤖 Hartur")
    p_co = st.text_input("Pseudo")
    m_co = st.text_input("Mot de passe", type="password")
    if st.button("Se connecter"):
        df_comptes, _ = lire_csv_github("comptes.csv")
        if not df_comptes.empty and ((df_comptes['pseudo'] == p_co) & (df_comptes['password'].astype(str) == str(m_co))).any():
            st.session_state.user = p_co
            st.rerun()
        else:
            st.error("Inconnu, t'es qui ?")
else:
    # On charge l'historique depuis GitHub
    df_glob, sha_glob = lire_csv_github("historique.csv")
    user_hist = df_glob[df_glob['pseudo'] == st.session_state.user]

    with st.sidebar:
        st.write(f"Utilisateur : **{st.session_state.user}**")
        if st.button("Se déconnecter"):
            st.session_state.user = None
            st.rerun()
        st.divider()
        with st.expander("🛡️ Admin"):
            if st.text_input("Code", type="password") == "1234":
                st.write("Historique complet :")
                st.dataframe(df_glob)

    st.title("Discussion avec Hartur")

    for _, row in user_hist.iterrows():
        with st.chat_message(row['role']):
            st.write(row['content'])

    prompt = st.chat_input("Dis-moi tout...")
    if prompt:
        with st.chat_message("user"):
            st.write(prompt)
        
        # Sauvegarde utilisateur sur GitHub
        new_row = pd.DataFrame([{"pseudo": st.session_state.user, "role": "user", "content": prompt}])
        df_glob = pd.concat([df_glob, new_row], ignore_index=True)
        ecrire_csv_github("historique.csv", df_glob, sha_glob)
        
        # Récupération de la réponse IA
        reponse = parler_a_ia(prompt, user_hist.to_dict('records'))
        
        with st.chat_message("assistant"):
            st.write(reponse)
        
        # On reprend le SHA tout neuf pour enregistrer la réponse de l'IA
        _, sha_neuf = lire_csv_github("historique.csv")
        new_row_ia = pd.DataFrame([{"pseudo": st.session_state.user, "role": "assistant", "content": reponse}])
        df_glob = pd.concat([df_glob, new_row_ia], ignore_index=True)
        ecrire_csv_github("historique.csv", df_glob, sha_neuf)
