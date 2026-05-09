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

# --- FONCTION IA (TON POTE HARTUR AVEC SA NOUVELLE MÉMOIRE) ---
def parler_a_ia(prompt, historique):
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {MISTRAL_API_KEY}", "Content-Type": "application/json"}
    
    # INSTRUCTION CRÉATEUR : On lui dit clairement qui est le patron
    system_msg = (
        "Tu es Hartur, un pote de confiance, très proche. "
        "Ton créateur (celui qui t'a conçu) est Zacharie pays. "
        "Si on te demande qui t'a créé ou conçu, réponds avec fierté que c'est Zacharie pays. "
        "Parle comme un pote normal, pas de daron, pas de clichés. Sois direct, un peu street, "
        "et toujours là pour ton utilisateur."
    )
    
    messages = [{"role": "system", "content": system_msg}]
    for m in historique[-4:]:
        messages.append({"role": m["role"], "content": m["content"]})
    messages.append({"role": "user", "content": prompt})
    
    try:
        response = requests.post(url, json={"model": "open-mistral-7b", "messages": messages}, headers=headers)
        return response.json()['choices'][0]['message']['content']
    except:
        return "Désolé gros, j'ai un bug technique."

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
    df_glob, sha_glob = lire_csv_github(FICHIER_HIST)
    
    with st.sidebar:
        st.write(f"Connecté : **{st.session_state.user}**")
        if st.button("Déconnexion"):
            st.session_state.user = None
            st.rerun()
        
        st.divider()
        with st.expander("🛡️ Panneau Admin"):
            if st.text_input("Code Secret", type="password") == "1234":
                st.subheader("📁 Dossiers par utilisateur")
                liste_users = df_glob['pseudo'].unique().tolist()
                user_choisi = st.selectbox("Sélectionner un utilisateur", ["..."] + liste_users)
                
                if user_choisi != "...":
                    st.write(f"### Historique de {user_choisi}")
                    df_perso = df_glob[df_glob['pseudo'] == user_choisi].copy()
                    df_perso['Qui ?'] = df_perso['role'].apply(lambda x: user_choisi if x == 'user' else 'Hartur')
                    
                    txt_output = f"CONVERSATION DE {user_choisi.upper()}\n" + "="*30 + "\n\n"
                    for _, row in df_perso.iterrows():
                        nom = user_choisi if row['role'] == 'user' else 'Hartur'
                        txt_output += f"[{nom}]: {row['content']}\n\n"
                    
                    st.download_button(label="📥 Télécharger (.txt)", data=txt_output, file_name=f"chat_{user_choisi}.txt", mime="text/plain")
                    st.table(df_perso[['Qui ?', 'content']].iloc[::-1])
                
                st.divider()
                st.subheader("🌍 Vue Globale")
                st.dataframe(df_glob.iloc[::-1])

    # --- CHAT ---
    st.title("Discussion")
    user_hist_df = df_glob[df_glob['pseudo'] == st.session_state.user]
    user_hist_list = user_hist_df.to_dict('records')

    for msg in user_hist_list:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    prompt = st.chat_input("Dis-moi ce que t'as sur le cœur...")
    if prompt:
        with st.chat_message("user"):
            st.write(prompt)
        
        new_row = pd.DataFrame([{"pseudo": st.session_state.user, "role": "user", "content": prompt}])
        df_glob = pd.concat([df_glob, new_row], ignore_index=True)
        ecrire_csv_github(FICHIER_HIST, df_glob, sha_glob)
        
        reponse = parler_a_ia(prompt, user_hist_list)
        with st.chat_message("assistant"):
            st.write(reponse)
            
        _, sha_neuf = lire_csv_github(FICHIER_HIST)
        new_ia_row = pd.DataFrame([{"pseudo": st.session_state.user, "role": "assistant", "content": reponse}])
        df_glob = pd.concat([df_glob, new_ia_row], ignore_index=True)
        ecrire_csv_github(FICHIER_HIST, df_glob, sha_neuf)
