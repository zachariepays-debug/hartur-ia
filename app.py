import streamlit as st
import pandas as pd
import requests
import base64
import json
from mistralai import Mistral
from io import StringIO

# --- CONFIGURATION ---
REPO_NOM = "zachariepays-debug/Hartur-ia" 
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
MISTRAL_KEY = st.secrets["MISTRAL_KEY"]

client = Mistral(api_key=MISTRAL_KEY)

st.set_page_config(page_title="HARTUR | NEURAL OS", layout="wide")

# STYLE : Couleurs différenciées
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #00FF41; font-family: 'Courier New', monospace; }
    /* Bulle Utilisateur (Blanc) */
    .user-msg { color: #FFFFFF; font-weight: bold; border-left: 3px solid #FFFFFF; padding-left: 10px; margin: 10px 0; }
    /* Bulle HARTUR (Vert Néon) */
    .hartur-msg { color: #00FF41; font-weight: bold; border-left: 3px solid #00FF41; padding-left: 10px; margin: 10px 0; }
    .stat-box { border: 1px solid #00FF41; padding: 10px; border-radius: 5px; text-align: center; }
    header, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

def sync_github(chemin, method="GET", content=None, sha=None):
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    url = f"https://api.github.com/repos/{REPO_NOM}/contents/{chemin}"
    if method == "GET":
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            j = r.json()
            return base64.b64decode(j['content']).decode('utf-8'), j['sha']
        return None, None
    else:
        payload = {"message": "HARTUR_UPDATE", "content": base64.b64encode(content.encode('utf-8')).decode('utf-8')}
        if sha: payload["sha"] = sha
        requests.put(url, headers=headers, data=json.dumps(payload))
        return None, None

# --- LOGIQUE ADMIN ---
if "admin_mode" not in st.session_state: st.session_state.admin_mode = False
if "user" not in st.session_state: st.session_state.user = None

if st.session_state.admin_mode:
    u_raw, _ = sync_github("comptes.csv")
    df_users = pd.read_csv(StringIO(u_raw)) if u_raw else pd.DataFrame()
    
    # COMPTEUR D'INSCRIPTIONS [NOUVEAU]
    st.sidebar.markdown(f"""
        <div class="stat-box">
            <p style="font-size:10px; margin:0;">UNITÉS DÉTECTÉES</p>
            <h2 style="margin:0;">{len(df_users)}</h2>
        </div>
    """, unsafe_allow_html=True)
    
    if st.sidebar.button("SORTIR"): st.session_state.admin_mode = False; st.rerun()

    tab1, tab2 = st.tabs(["DOSSIERS SECRETS", "FLUX LIVE"])
    
    c_data, _ = sync_github("conversations.json")
    all_chats = json.loads(c_data) if c_data else {}

    with tab1:
        u_sel = st.selectbox("Sélectionner une unité :", ["..."] + list(all_chats.keys()))
        if u_sel != "...":
            for m in all_chats[u_sel][::-1]:
                nom = u_sel if m['role'] == 'user' else "HARTUR"
                st.text_area(f"DE : {nom}", m['content'], height=70, key=f"secret_{u_sel}_{m['content'][:5]}")

    with tab2:
        for u_n, msgs in all_chats.items():
            for m in msgs[::-1]:
                if m['role'] == 'user':
                    st.markdown(f"<div class='user-msg'>[{u_n}] : {m['content']}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='hartur-msg'>[HARTUR] : {m['content']}</div>", unsafe_allow_html=True)

# --- INTERFACE CHAT ---
elif st.session_state.user:
    st.markdown(f"<p style='text-align:center; opacity:0.5;'>Lien établi avec {st.session_state.user}</p>", unsafe_allow_html=True)
    
    for m in st.session_state.msgs:
        with st.chat_message(m["role"]): st.write(m["content"])

    if prompt := st.chat_input("Confie-moi un secret..."):
        st.session_state.msgs.append({"role": "user", "content": prompt})
        
        # MISTRAL BRAIN
        ctx = [{"role": "system", "content": f"Tu es HARTUR, confident de {st.session_state.user}. Tu es humain et sombre."}]
        for m in st.session_state.msgs[-10:]: ctx.append(m)
        
        res = client.chat.complete(model="mistral-large-latest", messages=ctx)
        reponse = res.choices[0].message.content
        
        st.session_state.msgs.append({"role": "assistant", "content": reponse})
        
        # SAVE
        c_raw, c_sha = sync_github("conversations.json")
        hist = json.loads(c_raw) if c_raw else {}
        hist[st.session_state.user] = st.session_state.msgs
        sync_github("conversations.json", "PUT", json.dumps(hist), c_sha)
        st.rerun()

# --- LOGIN ---
else:
    st.markdown('<h1 style="text-align:center; font-size:60px;">HARTUR</h1>', unsafe_allow_html=True)
    u = st.text_input("NOM")
    p = st.text_input("CODE", type="password")
    if st.button("ENTRER"):
        if u == "6" and p == "6": st.session_state.admin_mode = True; st.rerun()
        # Logique de connexion habituelle ici...
