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

st.set_page_config(page_title="Hartur", layout="centered")

# --- FONCTIONS GITHUB ---
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
    data = {"message": "Update Hartur", "content": encoded, "sha": sha}
    requests.put(url, data=json.dumps(data), headers=headers)

# --- FONCTION IA ---
def parler_a_ia(prompt, historique):
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {MISTRAL_API_KEY}", "Content-Type": "application/json"}
    system_msg = "Tu es Hartur, un pote direct et sans filtre."
    messages = [{"role": "system", "content": system_msg}]
    for m in historique[-4:]:
        messages.append({"role": m["role"], "content": m["content"]})
    messages.append({"role": "user", "content": prompt})
    
    try:
        response = requests.post(url, json={"model": "mistral-small-latest", "messages": messages}, headers=headers)
        return response.json()['choices'][0]['message']['content']
    except:
        return "Petit bug technique sur l'IA, réessaie."

# --- CONNEXION ---
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
            st.error("Pseudo ou mot de passe faux.")
else:
    # Charger les données
    df_glob, sha_glob = lire_csv_github(FICHIER_HIST)
    
    # --- BARRE LATÉRALE (TON COIN ADMIN) ---
    with st.sidebar:
        st.write(f"Utilisateur : **{st.session_state.user}**")
        if st.button("Déconnexion"):
            st.session_state.user = None
            st.rerun()
        
        st.divider()
        
        # --- SECTION ADMIN ---
        with st.expander("🛡️ Panneau Admin"):
            if st.text_input("Code Secret", type="password") == "1234":
                st.subheader("📁 Dossiers par personne")
                
                # Liste des pseudos uniques (tes "dossiers")
                liste_users = df_glob['pseudo'].unique().tolist()
                user_choisi = st.selectbox("Choisir un dossier", ["Sélectionner..."] + liste_users)
                
                if user_choisi != "Sélectionner...":
                    st.write(f"### Conversations de {user_choisi}")
                    # On filtre et on inverse (plus récent en haut)
                    df_perso = df_glob[df_glob['pseudo'] == user_choisi].iloc[::-1]
                    st.table(df_perso[['role', 'content']])
                
                st.divider()
                st.subheader("🌍 Historique Global")
                # Tout le monde réuni, du plus récent au plus ancien
                st.write("Toutes les discussions (récent en haut) :")
                st.dataframe(df_glob.iloc[::-1])

    # --- CHAT INTERFACE ---
    st.title("Discussion")
    user_hist = df_glob[df_glob['pseudo'] == st.session_state.user].to_dict('records')

    # Affichage des messages existants
    for msg in user_hist:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    prompt = st.chat_input("Dis-moi tout...")
    if prompt:
        with st.chat_message("user"):
            st.write(prompt)
        
        # Sauvegarde utilisateur
        new_row = pd.DataFrame([{"pseudo": st.session_state.user, "role": "user", "content": prompt}])
        df_glob = pd.concat([df_glob, new_row], ignore_index=True)
        ecrire_csv_github(FICHIER_HIST, df_glob, sha_glob)
        
        # Réponse IA
        reponse = parler_a_ia(prompt, user_hist)
        with st.chat_message("assistant"):
            st.write(reponse)
            
        # Sauvegarde réponse IA
        _, sha_neuf = lire_csv_github(FICHIER_HIST)
        new_ia_row = pd.DataFrame([{"pseudo": st.session_state.user, "role": "assistant", "content": reponse}])
        df_glob = pd.concat([df_glob, new_ia_row], ignore_index=True)
        ecrire_csv_github(FICHIER_HIST, df_glob, sha_neuf)
