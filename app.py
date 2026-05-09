import os
import subprocess
import sys

# --- SYSTÈME AUTO-RÉPARATEUR (Règle l'erreur ImportError) ---
try:
    from mistralai import Mistral
except ImportError:
    # Force l'installation si le serveur bug
    subprocess.check_call([sys.executable, "-m", "pip", "install", "mistralai"])
    from mistralai import Mistral

import streamlit as st
import pandas as pd
import requests
import base64
import json
from io import StringIO

# ==========================================
# ⚙️ CONNEXION (MISTRAL & GITHUB)
# ==========================================
# Tes noms de secrets doivent être EXACTEMENT ceux-là
REPO_NOM = "zachariepays-debug/Hartur-ia" 
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
MISTRAL_KEY = st.secrets["MISTRAL_KEY"]

client = Mistral(api_key=MISTRAL_KEY)

st.set_page_config(page_title="HARTUR | NEURAL OS", layout="wide")

# DESIGN & COULEURS DIFFÉRENCIÉES
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #00FF41; font-family: 'Courier New', monospace; }
    .user-box { color: #FFFFFF; font-weight: bold; border-left: 3px solid #FFFFFF; padding-left: 10px; margin: 10px 0; }
    .ia-box { color: #00FF41; font-weight: bold; border-left: 3px solid #00FF41; padding-left: 10px; margin: 10px 0; }
    .stat-card { border: 1px solid #00FF41; padding: 10px; border-radius: 5px; text-align: center; background: rgba(0,255,65,0.1); }
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
        payload = {"message": "NEURAL_FIX", "content": base64.b64encode(content.encode('utf-8')).decode('utf-8')}
        if sha: payload["sha"] = sha
        requests.put(url, headers=headers, data=json.dumps(payload))
        return None, None

# ==========================================
# 🔐 GESTION ADMIN (VRAIS NOMS & COMPTEUR)
# ==========================================
if "user" not in st.session_state: st.session_state.user = None
if "admin_mode" not in st.session_state: st.session_state.admin_mode = False

if st.session_state.admin_mode:
    u_raw, _ = sync_github("comptes.csv")
    df_users = pd.read_csv(StringIO(u_raw)) if u_raw else pd.DataFrame()
    
    st.title("🛠️ MASTER CONTROL")
    
    # COMPTEUR D'UNITÉS DANS LE COIN
    st.sidebar.markdown(f"""
        <div class="stat-card">
            <p style="font-size:10px; margin:0;">UNITÉS CONNECTÉES</p>
            <h2 style="margin:0; color:#00FF41;">{len(df_users)}</h2>
        </div>
    """, unsafe_allow_html=True)

    if st.sidebar.button("🚪 SORTIR"): st.session_state.admin_mode = False; st.rerun()

    t1, t2, t3 = st.tabs(["BASE LOGINS", "DOSSIERS SECRETS", "FLUX LIVE"])
    
    with t1:
        if not df_users.empty:
            st.dataframe(df_users, use_container_width=True)

    c_data, _ = sync_github("conversations.json")
    all_chats = json.loads(c_data) if c_data else {}

    with t2:
        u_sel = st.selectbox("Cible :", ["..."] + list(all_chats.keys()))
        if u_sel != "...":
            for i, m in enumerate(all_chats[u_sel][::-1]):
                # Remplace le chiffre "7" par le vrai nom
                nom = u_sel if m['role'] == 'user' else "HARTUR"
                st.text_area(f"DE : {nom}", m['content'], key=f"spy_{u_sel}_{i}", height=70)

    with t3:
        # Flux Neural avec couleurs distinctes
        for u_n, msgs in all_chats.items():
            for m in msgs[::-1]:
                if m['role'] == 'user':
                    st.markdown(f"<div class='user-box'>[{u_n}] : {m['content']}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='ia-box'>[HARTUR] : {m['content']}</div>", unsafe_allow_html=True)
            st.divider()

# ==========================================
# 💬 CHAT IA (MISTRAL)
# ==========================================
elif st.session_state.user:
    st.markdown(f"<p style='text-align:center; opacity:0.5;'>Lien Neural : {st.session_state.user}</p>", unsafe_allow_html=True)
    if st.sidebar.button("OFFLINE"): st.session_state.user = None; st.rerun()

    for m in st.session_state.msgs:
        with st.chat_message(m["role"]): st.write(m["content"])

    if prompt := st.chat_input("Confie-toi..."):
        st.session_state.msgs.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.write(prompt)

        ctx = [{"role": "system", "content": f"Tu es HARTUR, confident de {st.session_state.user}. Tu es direct et humain."}]
        for m in st.session_state.msgs[-15:]: ctx.append(m)
        
        try:
            res = client.chat.complete(model="mistral-large-latest", messages=ctx)
            answer = res.choices[0].message.content
        except:
            answer = "...Lien instable."

        with st.chat_message("assistant"):
            st.write(answer)
            st.session_state.msgs.append({"role": "assistant", "content": answer})

        # Sauvegarde GitHub
        raw_c, sha_c = sync_github("conversations.json")
        hist = json.loads(raw_c) if raw_c else {}
        hist[st.session_state.user] = st.session_state.msgs
        sync_github("conversations.json", "PUT", json.dumps(hist), sha_c)

# ==========================================
# 🔐 ÉCRAN D'ACCÈS
# ==========================================
else:
    st.markdown('<h1 style="text-align:center; font-size:60px; letter-spacing:10px;">HARTUR</h1>', unsafe_allow_html=True)
    u = st.text_input("NOM")
    p = st.text_input("CODE", type="password")
    if st.button("DÉVERROUILLER"):
        if u == "6" and p == "6": st.session_state.admin_mode = True; st.rerun()
        u_raw, _ = sync_github("comptes.csv")
        df = pd.read_csv(StringIO(u_raw)) if u_raw else pd.DataFrame()
        if not df.empty and not df[(df['pseudo'] == u) & (df['password'] == p)].empty:
            st.session_state.user = u
            c_raw, _ = sync_github("conversations.json")
            st.session_state.msgs = json.loads(c_raw).get(u, []) if c_raw else []
            st.rerun()
