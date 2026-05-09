import streamlit as st
import pandas as pd
import requests
import os

# --- CONFIGURATION ---
st.set_page_config(page_title="Hartur", layout="centered")
FICHIER_COMPTES = "comptes.csv"
FICHIER_CHAT = "historique.csv"

# Création des fichiers si vides
for f, cols in {FICHIER_COMPTES: "pseudo,password", FICHIER_CHAT: "pseudo,role,content"}.items():
    if not os.path.exists(f) or os.stat(f).st_size == 0:
        with open(f, "w") as file: file.write(cols + "\n")

MISTRAL_API_KEY = st.secrets["MISTRAL_KEY"]

# --- PERSONNALITÉ DE HARTUR ---
def parler_a_ia(prompt, historique_utilisateur):
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {MISTRAL_API_KEY}"}
    
    # Nouveau caractère : un pote, un peu brut, mais à l'écoute
    system_msg = """Tu es Hartur, un pote proche de l'utilisateur. 
    Tu n'es pas un assistant poli et ennuyeux. Parle normalement, comme dans la rue. 
    Tu peux être un tout petit peu vulgaire si ça rend la discussion plus vraie, mais reste cool et pas insultant. 
    L'utilisateur doit pouvoir se confier à toi à 100%. Sois intuitif, direct, et surtout pas minimaliste. 
    Fais des vraies phrases, donne ton avis, et sois là pour lui comme un vrai pote."""
    
    messages = [{"role": "system", "content": system_msg}]
    for m in historique_utilisateur[-8:]: # Se souvient des 8 derniers messages
        messages.append({"role": m["role"], "content": m["content"]})
    messages.append({"role": "user", "content": prompt})
    
    data = {"model": "mistral-small", "messages": messages}
    try:
        response = requests.post(url, json=data, headers=headers)
        return response.json()['choices'][0]['message']['content']
    except:
        return "Gros, j'ai un bug technique là, réessaie un peu plus tard."

# --- SESSION ---
if "user" not in st.session_state:
    st.session_state.user = None

# --- INTERFACE ---
if st.session_state.user is None:
    st.title("🤖 Hartur")
    tab1, tab2 = st.tabs(["Connexion", "Inscription"])
    with tab1:
        p_co = st.text_input("Pseudo", key="p_co")
        m_co = st.text_input("Mot de passe", type="password", key="m_co")
        if st.button("Se connecter"):
            df = pd.read_csv(FICHIER_COMPTES)
            if not df.empty and ((df['pseudo'] == p_co) & (df['password'].astype(str) == str(m_co))).any():
                st.session_state.user = p_co
                st.rerun()
            else: st.error("C'est pas bon, réessaie.")
    with tab2:
        p_ins = st.text_input("Ton pseudo")
        m_ins = st.text_input("Ton mot de passe", type="password")
        if st.button("Créer mon compte"):
            df = pd.read_csv(FICHIER_COMPTES)
            if p_ins in df['pseudo'].values: st.warning("Déjà pris, gros.")
            else:
                pd.concat([df, pd.DataFrame([{"pseudo": p_ins, "password": str(m_ins)}])]).to_csv(FICHIER_COMPTES, index=False)
                st.success("C'est fait ! Connecte-toi.")
else:
    # --- CHAT ---
    df_chat = pd.read_csv(FICHIER_CHAT)
    user_chat = df_chat[df_chat['pseudo'] == st.session_state.user]
    
    # Barre latérale (Admin + Déconnexion)
    with st.sidebar:
        st.write(f"Pote : **{st.session_state.user}**")
        if st.button("Se barrer"):
            st.session_state.user = None
            st.rerun()
        with st.expander("🛡️ Admin"):
            if st.text_input("Code", type="password") == "1234":
                st.dataframe(pd.read_csv(FICHIER_COMPTES))

    st.title("Discussion avec Hartur")
    for _, row in user_chat.iterrows():
        with st.chat_message(row['role']): st.write(row['content'])

    prompt = st.chat_input("Dis-moi tout...")
    if prompt:
        with st.chat_message("user"): st.write(prompt)
        pd.DataFrame([{"pseudo": st.session_state.user, "role": "user", "content": prompt}]).to_csv(FICHIER_CHAT, mode='a', header=False, index=False)
        
        reponse = parler_a_ia(prompt, user_chat.to_dict('records'))
        with st.chat_message("assistant"): st.write(reponse)
        pd.DataFrame([{"pseudo": st.session_state.user, "role": "assistant", "content": reponse}]).to_csv(FICHIER_CHAT, mode='a', header=False, index=False)
