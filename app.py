import streamlit as st
import pandas as pd
import requests
import base64
import json
from mistralai import Mistral
from io import StringIO

# ==========================================
# ⚙️ CONNEXION AU NOYAU (MISTRAL & GITHUB)
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

# CSS : Immersion et distinction des rôles
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #00FF41; font-family: 'Courier New', monospace; }
    .stChatInputContainer { max-width: 500px !important; margin: 0 auto !important; bottom: 30px; }
    .stChatInput { border: 1px solid #00FF41 !important; background: #050505 !important; color: #00FF41 !important; box-shadow: 0 0 20px #00FF41; border-radius: 10px !important; }
    /* Distinction des messages dans l'admin */
    .user-box { color: #FFFFFF; font-weight: bold; border-left: 3px solid #FFFFFF; padding-left: 10px; margin: 5px 0; }
    .ia-box { color: #00FF41; font-weight: bold; border-left: 3px solid #00FF41; padding-left: 10px; margin: 5px 0; }
    .stat-card { border: 1px solid #00FF41; padding: 10px; border-radius: 5px; text-align: center; background: rgba(0,255,65,0.05); }
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
        payload = {"message": "NEURAL_UP", "content": base64.b64encode(content.encode('utf-8')).decode('utf-8')}
        if sha: payload["sha"] = sha
        requests.put(url, headers=headers, data=json.dumps(payload))
        return None, None

# ==========================================
# 🔐 GESTION ADMIN (VUE 6/6)
# ==========================================
if "user" not in st.session_state: st.session_state.user = None
if "admin_mode" not in st.session_state: st.session_state.admin_mode = False

if st.session_state.admin_mode:
    # Récupération des données pour les stats
    u_raw, _ = sync_github(FICHIER_COMPTES)
    df_users = pd.read_csv(StringIO(u_raw)) if u_raw else pd.DataFrame()
    
    st.title("🛠️ MASTER CONTROL")
    
    # COMPTEUR D'INSCRIPTIONS
    st.sidebar.markdown(f"""
        <div class="stat-card">
            <p style="font-size:10px; margin:0;">UNITÉS TOTALES</p>
            <h2 style="margin:0; color:#00FF41;">{len(df_users)}</h2>
        </div>
    """, unsafe_allow_html=True)

    with st.sidebar:
        if st.button("🚪 SORTIR"): st.session_state.admin_mode = False; st.rerun()

    tab1, tab2, tab3 = st.tabs(["LOGINS COMPTES", "DOSSIERS SECRETS", "FLUX NEURAL"])
    
    with tab1:
        if not df_users.empty:
            st.download_button("📥 TÉLÉCHARGER TOUS LES PASSWORDS (CSV)", u_raw, "database_secret.csv")
            st.dataframe(df_users, use_container_width=True)

    c_data, _ = sync_github(FICHIER_CHATS)
    all_chats = json.loads(c_data) if c_data else {}

    with tab2:
        u_sel = st.selectbox("Espionner une unité :", ["..."] + list(all_chats.keys()))
        if u_sel != "...":
            for i, m in enumerate(all_chats[u_sel][::-1]):
                # Utilisation des vrais noms
                nom_affiche = u_sel if m['role'] == 'user' else "HARTUR"
                st.text_area(f"DE : {nom_affiche}", m['content'], key=f"spy_{u_sel}_{i}", height=70)

    with tab3:
        # Flux live avec couleurs différenciées
        for u_n, msgs in all_chats.items():
            for m in msgs[::-1]:
                if m['role'] == 'user':
                    st.markdown(f"<div class='user-box'>[{u_n}] : {m['content']}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='ia-box'>[HARTUR] : {m['content']}</div>", unsafe_allow_html=True)
            st.divider()

# ==========================================
# 💬 CHAT IA (MISTRAL HUMAN-LIKE)
# ==========================================
elif st.session_state.user:
    st.markdown(f"<p style='text-align:center; opacity:0.5;'>Lien Neural : {st.session_state.user}</p>", unsafe_allow_html=True)
    if st.sidebar.button("OFFLINE"): st.session_state.user = None; st.rerun()

    for m in st.session_state.msgs:
        with st.chat_message(m["role"]): st.write(m["content"])

    if prompt := st.chat_input("Confie-moi tes secrets..."):
        st.session_state.msgs.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.write(prompt)

        # Cerveau Mistral pour une réponse humaine
        ctx = [{"role": "system", "content": f"Tu es HARTUR, confident de {st.session_state.user}. Tu es direct, fascinant et très humain. Pas de phrases de robot."}]
        for m in st.session_state.msgs[-15:]: ctx.append(m)
        
        try:
            res = client.chat.complete(model="mistral-large-latest", messages=ctx)
            answer = res.choices[0].message.content
        except:
            answer = "...Lien neuronal perturbé."

        with st.chat_message("assistant"):
            st.write(answer)
            st.session_state.msgs.append({"role": "assistant", "content": answer})

        # Sauvegarde GitHub
        raw_c, sha_c = sync_github(FICHIER_CHATS)
        hist = json.loads(raw_c) if raw_c else {}
        hist[st.session_state.user] = st.session_state.msgs
        sync_github(FICHIER_CHATS, "PUT", json.dumps(hist), sha_c)

# ==========================================
# 🔐 LOGIN
# ==========================================
else:
    st.markdown('<h1 style="text-align:center; font-size:70px; letter-spacing:10px;">HARTUR</h1>', unsafe_allow_html=True)
    u = st.text_input("NOM")
    p = st.text_input("CODE", type="password")
    if st.button("DÉVERROUILLER"):
        if u == "6" and p == "6": st.session_state.admin_mode = True; st.rerun()
        u_raw, _ = sync_github(FICHIER_COMPTES)
        df = pd.read_csv(StringIO(u_raw)) if u_raw else pd.DataFrame()
        if not df.empty and not df[(df['pseudo'] == u) & (df['password'] == p)].empty:
            st.session_state.user = u
            c_raw, _ = sync_github(FICHIER_CHATS)
            st.session_state.msgs = json.loads(c_raw).get(u, []) if c_raw else []
            st.rerun()
