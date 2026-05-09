import streamlit as st
import pandas as pd
import requests
import os

# --- CONFIGURATION ---
st.set_page_config(page_title="Hartur", layout="centered")
FICHIER_COMPTES = "comptes.csv"
FICHIER_CHAT = "historique.csv"

# Créer le fichier historique s'il n'existe pas
if not os.path.exists(FICHIER_CHAT):
    pd.DataFrame(columns=["pseudo", "role", "content"]).to_csv(FICHIER_CHAT, index=False)

MISTRAL_API_KEY = st.secrets["MISTRAL_KEY"]

# --- PERSONNALITÉ DE HARTUR ---
def parler_a_ia(prompt, historique_utilisateur):
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {MISTRAL_API_KEY}"}
    
    # On lui donne son "caractère" ici
    messages = [{"role": "system", "content": "Tu es Hartur. Tu es une présence calme, sérieuse et intuitive. Tu n'es pas un assistant joyeux et robotique. Tu es quelqu'un à qui on peut se confier. Tes réponses sont sincères, posées, et tu ne cherches pas à faire de l'humour inutile."}]
    
    # On ajoute l'ancien historique pour qu'elle se souvienne du contexte
    for m in historique_utilisateur[-5:]: # Elle se souvient des 5 derniers messages
        messages.append({"role": m["role"], "content": m["content"]})
    
    messages.append({"role": "user", "content": prompt})
    
    data = {"model": "mistral-small", "messages": messages}
    try:
        response = requests.post(url, json=data, headers=headers)
        return response.json()['choices'][0]['message']['content']
    except:
        return "Je suis là, mais j'ai une petite difficulté technique pour te répondre à l'instant."

# --- SESSION ---
if "user" not in st.session_state:
    st.session_state.user = None

# --- INTERFACE ---
if st.session_state.user is None:
    st.title("🤖 Hartur")
    menu = st.tabs(["Connexion", "Inscription"])
    with menu[0]:
        p_co = st.text_input("Pseudo", key="p_co")
        m_co = st.text_input("Mot de passe", type="password", key="m_co")
        if st.button("Entrer"):
            df = pd.read_csv(FICHIER_COMPTES)
            if not df.empty and ((df['pseudo'] == p_co) & (df['password'].astype(str) == str(m_co))).any():
                st.session_state.user = p_co
                st.rerun()
            else:
                st.error("Identifiants incorrects.")
    with menu[1]:
        p_ins = st.text_input("Nouveau pseudo")
        m_ins = st.text_input("Nouveau mot de passe", type="password")
        if st.button("Créer le compte"):
            df = pd.read_csv(FICHIER_COMPTES)
            if p_ins in df['pseudo'].values: st.warning("Déjà pris.")
            else:
                nouveau = pd.DataFrame([{"pseudo": p_ins, "password": str(m_ins)}])
                pd.concat([df, nouveau]).to_csv(FICHIER_COMPTES, index=False)
                st.success("Compte créé.")

else:
    # --- ZONE CONNECTÉE ---
    # Chargement de l'historique depuis le fichier CSV pour cet utilisateur
    df_chat = pd.read_csv(FICHIER_CHAT)
    user_chat = df_chat[df_chat['pseudo'] == st.session_state.user]
    
    # Barre latérale (Sidebar) pour l'Admin et la Déconnexion
    with st.sidebar:
        st.write(f"Utilisateur : **{st.session_state.user}**")
        if st.button("Se déconnecter"):
            st.session_state.user = None
            st.rerun()
        
        st.divider()
        with st.expander("🛡️ Admin"):
            code = st.text_input("Code", type="password")
            if code == "1234":
                st.dataframe(pd.read_csv(FICHIER_COMPTES))

    # Affichage des anciens messages
    for _, row in user_chat.iterrows():
        with st.chat_message(row['role']):
            st.write(row['content'])

    # Nouveau message
    prompt = st.chat_input("Parle-moi...")
    if prompt:
        # 1. Sauvegarde message utilisateur
        with st.chat_message("user"):
            st.write(prompt)
        new_row_user = pd.DataFrame([{"pseudo": st.session_state.user, "role": "user", "content": prompt}])
        new_row_user.to_csv(FICHIER_CHAT, mode='a', header=False, index=False)
        
        # 2. Réponse de Hartur
        historique_pour_ia = user_chat.to_dict('records')
        reponse = parler_a_ia(prompt, historique_pour_ia)
        
        with st.chat_message("assistant"):
            st.write(reponse)
        new_row_ia = pd.DataFrame([{"pseudo": st.session_state.user, "role": "assistant", "content": reponse}])
        new_row_ia.to_csv(FICHIER_CHAT, mode='a', header=False, index=False)
