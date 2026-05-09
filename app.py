import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import requests
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="Hartur IA", layout="centered")

# --- CONNEXION ---
# Cette ligne gère toute la liaison avec ton Google Sheet
conn = st.connection("gsheets", type=GSheetsConnection)

def lire_donnees(onglet):
    try:
        return conn.read(worksheet=onglet, ttl=0)
    except:
        return pd.DataFrame()

def ecrire_donnees(onglet, df):
    try:
        conn.update(worksheet=onglet, data=df)
        return True
    except Exception as e:
        st.error(f"Erreur de sauvegarde : {e}")
        return False

# --- LOGIQUE IA MISTRAL ---
def demander_ia(prompt):
    key = st.secrets.get("MISTRAL_KEY")
    if not key:
        return "Clé API manquante dans les Secrets."
    
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {key}"}
    data = {
        "model": "open-mistral-7b",
        "messages": [{"role": "user", "content": prompt}]
    }
    try:
        r = requests.post(url, headers=headers, json=data)
        return r.json()['choices'][0]['message']['content']
    except:
        return "Hartur est indisponible pour le moment."

# --- INTERFACE ---
st.title("🤖 Hartur IA")

if "user" not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    choix = st.sidebar.selectbox("Menu", ["Connexion", "Inscription", "Admin"])
    
    if choix == "Connexion":
        p = st.text_input("Pseudo")
        m = st.text_input("Mot de passe", type="password")
        if st.button("Se connecter"):
            df = lire_donnees("comptes")
            if not df.empty and ((df['pseudo'] == p) & (df['password'] == str(m))).any():
                st.session_state.user = p
                st.rerun()
            else:
                st.error("Identifiants incorrects.")

    elif choix == "Inscription":
        p = st.text_input("Nouveau pseudo")
        m = st.text_input("Nouveau mot de passe", type="password")
        if st.button("Créer mon compte"):
            df = lire_donnees("comptes")
            if not df.empty and p in df['pseudo'].values:
                st.warning("Pseudo déjà utilisé.")
            else:
                nouveau = pd.DataFrame([{"pseudo": p, "password": str(m)}])
                if ecrire_donnees("comptes", pd.concat([df, nouveau], ignore_index=True)):
                    st.success("Compte créé ! Tu peux te connecter.")

    elif choix == "Admin":
        code = st.text_input("Code Admin", type="password")
        if code.lower() == "babar":
            st.write("### Historique (Logs)")
            st.dataframe(lire_donnees("logs"))

else:
    st.sidebar.write(f"Connecté : **{st.session_state.user}**")
    if st.sidebar.button("Déconnexion"):
        st.session_state.user = None
        st.rerun()

    # Zone de Chat
    if "chat" not in st.session_state:
        st.session_state.chat = []

    for m in st.session_state.chat:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    if p_input := st.chat_input("Parle à Hartur..."):
        st.session_state.chat.append({"role": "user", "content": p_input})
        with st.chat_message("user"):
            st.markdown(p_input)

        rep = demander_ia(p_input)
        st.session_state.chat.append({"role": "assistant", "content": rep})
        with st.chat_message("assistant"):
            st.markdown(rep)
        
        # Enregistrement Log
        df_logs = lire_donnees("logs")
        nouveau_log = pd.DataFrame([{
            "date": datetime.now().strftime("%d/%m %H:%M"),
            "pseudo": st.session_state.user,
            "message": p_input,
            "reponse": rep
        }])
        ecrire_donnees("logs", pd.concat([df_logs, nouveau_log], ignore_index=True))
