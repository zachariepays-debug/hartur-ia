import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import requests
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="Hartur IA", layout="centered")

# --- CONNEXION ---
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
        return "Hartur est indisponible."

# --- INTERFACE PRINCIPALE ---
st.title("🤖 Hartur IA")

if "user" not in st.session_state:
    st.session_state.user = None

# --- AFFICHAGE SI NON CONNECTÉ (L'interface qui défile) ---
if st.session_state.user is None:
    
    # 1. SECTION CONNEXION
    st.header("🔑 Se connecter")
    p_co = st.text_input("Pseudo", key="p_co")
    m_co = st.text_input("Mot de passe", type="password", key="m_co")
    if st.button("Connexion"):
        df = lire_donnees("comptes")
        if not df.empty and ((df['pseudo'] == p_co) & (df['password'] == str(m_co))).any():
            st.session_state.user = p_co
            st.rerun()
        else:
            st.error("Identifiants incorrects.")

    st.divider() # Petite ligne de séparation

    # 2. SECTION INSCRIPTION
    st.header("📝 Inscription")
    p_ins = st.text_input("Nouveau pseudo", key="p_ins")
    m_ins = st.text_input("Nouveau mot de passe", type="password", key="m_ins")
    if st.button("Créer un compte"):
        df = lire_donnees("comptes")
        if not df.empty and p_ins in df['pseudo'].values:
            st.warning("Pseudo déjà utilisé.")
        else:
            nouveau = pd.DataFrame([{"pseudo": p_ins, "password": str(m_ins)}])
            if ecrire_donnees("comptes", pd.concat([df, nouveau], ignore_index=True)):
                st.success("Compte créé avec succès ! Connectez-vous en haut.")

    st.divider()

    # 3. SECTION ADMIN
    st.header("🛡️ Admin")
    code = st.text_input("Code secret", type="password", key="admin_code")
    if code.lower() == "babar":
        st.write("### Historique des Titans (Logs)")
        st.dataframe(lire_donnees("logs"))

# --- AFFICHAGE SI CONNECTÉ (Le Chat) ---
else:
    st.subheader(f"Connecté : {st.session_state.user}")
    if st.button("Se déconnecter"):
        st.session_state.user = None
        st.rerun()

    if "chat" not in st.session_state:
        st.session_state.chat = []

    for msg in st.session_state.chat:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if p_input := st.chat_input("Parle à Hartur..."):
        st.session_state.chat.append({"role": "user", "content": p_input})
        with st.chat_message("user"):
            st.markdown(p_input)

        rep = demander_ia(p_input)
        st.session_state.chat.append({"role": "assistant", "content": rep})
        with st.chat_message("assistant"):
            st.markdown(rep)
        
        # Enregistrement des Logs
        df_logs = lire_donnees("logs")
        nouveau_log = pd.DataFrame([{
            "date": datetime.now().strftime("%d/%m %H:%M"),
            "pseudo": st.session_state.user,
            "message": p_input,
            "reponse": rep
        }])
        ecrire_donnees("logs", pd.concat([df_logs, nouveau_log], ignore_index=True))
