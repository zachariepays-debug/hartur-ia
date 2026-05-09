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
    return pd.DataFrame(columns=["pseudo", "password"]), None

def ecrire_csv_github(nom_fichier, df, sha):
    url = f"https://api.github.com/repos/{REPO_NOM}/contents/{nom_fichier}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    csv_content = df.to_csv(index=False)
    encoded = base64.b64encode(csv_content.encode('utf-8')).decode('utf-8')
    data = {"message": "Update par Hartur", "content": encoded, "sha": sha}
    requests.put(url, data=json.dumps(data), headers=headers)

# --- FONCTION IA ---
def parler_a_ia(prompt, historique):
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {MISTRAL_API_KEY}", "Content-Type": "application/json"}
    system_msg = (
        "Tu es Hartur, un pote proche et direct. Ton créateur est Zacharie pays. "
        "Si on te demande qui t'a conçu, réponds simplement 'Zacharie pays'. "
        "Reste cool, direct et sans filtre de daron."
    )
    messages = [{"role": "system", "content": system_msg}]
    for m in historique[-5:]:
        messages.append({"role": m["role"], "content": m["content"]})
    messages.append({"role": "user", "content": prompt})
    try:
        response = requests.post(url, json={"model": "open-mistral-7b", "messages": messages}, headers=headers)
        return response.json()['choices'][0]['message']['content']
    except:
        return "Petit bug technique là, réessaie."

# --- INITIALISATION ---
if "user" not in st.session_state:
    st.session_state.user = None
if "view" not in st.session_state:
    st.session_state.view = "chat"

# --- INTERFACE DE CONNEXION / INSCRIPTION ---
if st.session_state.user is None:
    st.title("🤖 Bienvenue chez Hartur")
    
    onglet_co, onglet_ins = st.tabs(["Se connecter", "S'inscrire"])
    
    with onglet_co:
        p_co = st.text_input("Pseudo", key="co_p")
        m_co = st.text_input("Mot de passe", type="password", key="co_m")
        if st.button("Connexion"):
            df_c, _ = lire_csv_github(FICHIER_COMPTES)
            if not df_c.empty and ((df_c['pseudo'].astype(str) == str(p_co)) & (df_c['password'].astype(str) == str(m_co))).any():
                st.session_state.user = p_co
                st.rerun()
            else:
                st.error("Pseudo ou mot de passe faux.")

    with onglet_ins:
        st.subheader("Créer un nouveau compte")
        p_ins = st.text_input("Choisis un pseudo", key="ins_p")
        m_ins = st.text_input("Choisis un mot de passe", type="password", key="ins_m")
        if st.button("Créer mon compte"):
            df_c, sha_c = lire_csv_github(FICHIER_COMPTES)
            if p_ins in df_c['pseudo'].astype(str).values:
                st.warning("Ce pseudo existe déjà, gros.")
            elif p_ins and m_ins:
                new_user = pd.DataFrame([{"pseudo": p_ins, "password": m_ins}])
                df_c = pd.concat([df_c, new_user], ignore_index=True)
                ecrire_csv_github(FICHIER_COMPTES, df_c, sha_c)
                st.success("Compte créé ! Connecte-toi maintenant.")
            else:
                st.error("Remplis tout si tu veux entrer.")

else:
    # --- CHARGEMENT DES DONNÉES ---
    df_glob, sha_glob = lire_csv_github(FICHIER_HIST)
    
    # --- MENU LATÉRAL ---
    with st.sidebar:
        st.write(f"Connecté : **{st.session_state.user}**")
        if st.button("💬 Chat"):
            st.session_state.view = "chat"
            st.rerun()
        
        st.divider()
        code_adm = st.text_input("Admin Code", type="password")
        if code_adm == "1234":
            if st.button("📊 Ouvrir l'Admin"):
                st.session_state.view = "admin"
                st.rerun()
        
        st.divider()
        if st.button("Se déconnecter"):
            st.session_state.user = None
            st.rerun()

    # --- PAGE ADMIN ---
    if st.session_state.view == "admin":
        st.title("🛡️ Panneau Admin")
        liste_users = df_glob['pseudo'].unique().tolist()
        user_inspect = st.selectbox("Dossier de :", ["Choisir..."] + liste_users)
        
        if user_inspect != "Choisir...":
            df_p = df_glob[df_glob['pseudo'] == user_inspect].copy()
            txt_dl = f"CHAT DE {user_inspect}\n" + "="*20 + "\n"
            for _, r in df_p.iterrows():
                u = user_inspect if r['role'] == 'user' else 'HARTUR'
                txt_dl += f"[{u}]: {r['content']}\n\n"
            st.download_button("📥 Télécharger cette discussion", txt_dl, f"chat_{user_inspect}.txt")
            
            st.divider()
            for _, r in df_p.iloc[::-1].iterrows():
                if r['role'] == 'user':
                    st.info(f"**👤 {user_inspect}** : {r['content']}")
                else:
                    st.success(f"**🤖 HARTUR** : {r['content']}")
    
    # --- PAGE CHAT ---
    else:
        st.title("Discussion")
        user_hist_df = df_glob[df_glob['pseudo'] == st.session_state.user]
        user_hist_list = user_hist_df.to_dict('records')

        for msg in user_hist_list:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        prompt = st.chat_input("Dis-moi tout...")
        if prompt:
            with st.chat_message("user"):
                st.write(prompt)
            
            new_row = pd.DataFrame([{"pseudo": st.session_state.user, "role": "user", "content": prompt}])
            df_glob = pd.concat([df_glob, new_row], ignore_index=True)
            ecrire_csv_github(FICHIER_HIST, df_glob, sha_glob)
            
            reponse = parler_a_ia(prompt, user_hist_list)
            with st.chat_message("assistant"):
                st.write(reponse)
                
            _, sha_fresh = lire_csv_github(FICHIER_HIST)
            new_ia_row = pd.DataFrame([{"pseudo": st.session_state.user, "role": "assistant", "content": reponse}])
            df_glob = pd.concat([df_glob, new_ia_row], ignore_index=True)
            ecrire_csv_github(FICHIER_HIST, df_glob, sha_fresh)
