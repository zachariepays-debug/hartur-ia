import streamlit as st
import pandas as pd
import requests

# --- CONFIGURATION ---
st.set_page_config(page_title="Hartur IA", layout="centered")
FICHIER = "comptes.csv"

# Vérification de la clé Mistral
if "MISTRAL_KEY" in st.secrets:
    MISTRAL_API_KEY = st.secrets["MISTRAL_KEY"]
else:
    st.error("Clé MISTRAL_KEY manquante dans les Secrets Streamlit.")
    MISTRAL_API_KEY = ""

# Fonction pour appeler l'IA Mistral
def parler_a_ia(message_utilisateur):
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {MISTRAL_API_KEY}"
    }
    data = {
        "model": "mistral-tiny",
        "messages": [{"role": "user", "content": message_utilisateur}]
    }
    try:
        response = requests.post(url, json=data, headers=headers)
        return response.json()['choices'][0]['message']['content']
    except:
        return "Désolé, j'ai un petit souci technique pour répondre."

# --- LOGIQUE DE SESSION ---
if "user" not in st.session_state:
    st.session_state.user = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- INTERFACE PRINCIPALE ---
st.title("🤖 Hartur IA")

if st.session_state.user is None:
    # --- CONNEXION / INSCRIPTION ---
    menu = st.tabs(["Connexion", "Inscription"])
    
    with menu[0]:
        p_co = st.text_input("Pseudo", key="p_co")
        m_co = st.text_input("Mot de passe", type="password", key="m_co")
        if st.button("Se connecter"):
            df = pd.read_csv(FICHIER)
            if not df.empty and ((df['pseudo'] == p_co) & (df['password'].astype(str) == str(m_co))).any():
                st.session_state.user = p_co
                st.rerun()
            else:
                st.error("Identifiants incorrects.")

    with menu[1]:
        p_ins = st.text_input("Nouveau pseudo", key="p_ins")
        m_ins = st.text_input("Nouveau mot de passe", type="password", key="m_ins")
        if st.button("Créer mon compte"):
            df = pd.read_csv(FICHIER)
            if p_ins in df['pseudo'].values:
                st.warning("Pseudo déjà pris.")
            else:
                nouveau = pd.DataFrame([{"pseudo": p_ins, "password": str(m_ins)}])
                df = pd.concat([df, nouveau], ignore_index=True)
                df.to_csv(FICHIER, index=False)
                st.success("Compte créé ! Connecte-toi maintenant.")

else:
    # --- ESPACE CHAT (Connecté) ---
    st.sidebar.write(f"Connecté en tant que : **{st.session_state.user}**")
    if st.sidebar.button("Se déconnecter"):
        st.session_state.user = None
        st.rerun()

    # Affichage du chat
    for chat in st.session_state.chat_history:
        with st.chat_message(chat["role"]):
            st.write(chat["content"])

    # Zone de saisie
    prompt = st.chat_input("Pose-moi une question...")
    if prompt:
        with st.chat_message("user"):
            st.write(prompt)
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        reponse = parler_a_ia(prompt)
        
        with st.chat_message("assistant"):
            st.write(reponse)
        st.session_state.chat_history.append({"role": "assistant", "content": reponse})

# --- SECTION ADMIN (Tout en bas) ---
st.divider()
with st.expander("🛡️ Zone Admin"):
    code_admin = st.text_input("Code secret admin", type="password")
    if code_admin == "1234":  # Tu peux changer ce code par ce que tu veux
        st.write("### Liste des utilisateurs inscrits :")
        df_admin = pd.read_csv(FICHIER)
        st.dataframe(df_admin)
    elif code_admin != "":
        st.error("Code incorrect")
