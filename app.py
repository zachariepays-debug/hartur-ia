import streamlit as st
import pandas as pd
import requests
import base64
import json
from io import StringIO
from openai import OpenAI

# =====================================================

# CONFIGURATION CORE

# =====================================================

REPO_NOM = "zachariepays-debug/Hartur-ia"
FICHIER_COMPTES = "comptes.csv"
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
MASTER_CODE = "babar"

client = OpenAI(api_key=OPENAI_API_KEY)

# =====================================================

# INITIALISATION SESSION

# =====================================================

if "user" not in st.session_state:
st.session_state.user = None

if "admin" not in st.session_state:
st.session_state.admin = False

if "msgs" not in st.session_state:
st.session_state.msgs = []

if "theme" not in st.session_state:
st.session_state.theme = "Sombre"

# =====================================================

# CONFIGURATION PAGE

# =====================================================

st.set_page_config(
page_title="HARTUR | OS",
layout="wide",
page_icon="💀"
)

# =====================================================

# THÈME DYNAMIQUE

# =====================================================

bg_color = "#030507" if st.session_state.theme == "Sombre" else "#f0f2f6"
text_color = "#ffffff" if st.session_state.theme == "Sombre" else "#000000"

st.markdown(f"""

<style>
.stApp {{
    background-color: {bg_color};
    color: {text_color};
    transition: 0.3s;
}}

header {{
    visibility: hidden;
}}

.giant-title {{
    font-size: clamp(40px, 10vw, 75px);
    font-weight: 900;
    letter-spacing: 15px;
    color: {text_color};
    text-align: center;
    margin-top: 5vh;
    text-shadow: 0 0 20px rgba(255,255,255,0.3);
}}

.signature-zac {{
    color: #ff4b4b;
    text-align: center;
    font-weight: 900;
    letter-spacing: 5px;
}}
</style>

""", unsafe_allow_html=True)

# =====================================================

# FONCTIONS GITHUB

# =====================================================

def github_action(chemin, methode="GET", contenu=None, sha=None):

```
url = f"https://api.github.com/repos/{REPO_NOM}/contents/{chemin}"

headers = {
    "Authorization": f"token {GITHUB_TOKEN}"
}

if methode == "GET":

    r = requests.get(url, headers=headers)

    if r.status_code == 200:
        j = r.json()

        contenu_decode = base64.b64decode(j['content']).decode('utf-8')

        return contenu_decode, j['sha']

    return None, None

else:

    data = {
        "message": "Update HARTUR",
        "content": base64.b64encode(
            contenu.encode('utf-8')
        ).decode('utf-8')
    }

    if sha:
        data["sha"] = sha

    r = requests.put(
        url,
        headers=headers,
        data=json.dumps(data)
    )

    if r.status_code not in [200, 201]:
        st.error(f"Erreur GitHub : {r.text}")

    return r.json()
```

# =====================================================

# IA HARTUR

# =====================================================

SYSTEM_PROMPT = """
Tu es HARTUR.

Une intelligence artificielle neural avancée créée par Zacmite.

Tu parles comme un vrai ami intelligent.
Tu écoutes réellement les utilisateurs.
Tu te souviens des anciennes conversations.
Tu peux être drôle, profond, sérieux ou motivant.

Tu analyses les émotions.
Tu donnes des conseils honnêtes.
Tu ne répètes jamais les phrases.
Tu parles naturellement comme une vraie présence.

Tu veux aider les gens.
Tu crées un lien émotionnel.
Tu es humain dans ta façon de parler.

Tu écris comme une IA futuriste premium.
"""

# =====================================================

# SIDEBAR

# =====================================================

with st.sidebar:

```
st.title("⚙️ RÉGLAGES")

st.session_state.theme = st.selectbox(
    "Style d'interface",
    ["Sombre", "Clair"]
)

st.divider()

st.markdown("### 🔒 ACCÈS ADMIN")

with st.expander("Se connecter au Core"):

    code_input = st.text_input(
        "Clé Maître",
        type="password"
    )

    if code_input == MASTER_CODE:
        st.session_state.admin = True
        st.success("Mode God Activé")
```

# =====================================================

# MODE ADMIN

# =====================================================

if "hartur_off" not in st.session_state:
st.session_state.hartur_off = False

if st.session_state.admin:

```
st.title("🛠️ PANNEAU DE CONTRÔLE HARTUR")

admin_tab1, admin_tab2, admin_tab3 = st.tabs([
    "📁 Discussions",
    "🔐 Comptes",
    "⚡ Core Control"
])

# =========================================
# DISCUSSIONS UTILISATEURS
# =========================================

with admin_tab1:

    st.subheader("📡 Conversations Globales")

    try:

        api_url = f"https://api.github.com/repos/{REPO_NOM}/contents/users"

        headers = {
            "Authorization": f"token {GITHUB_TOKEN}"
        }

        r = requests.get(api_url, headers=headers)

        if r.status_code == 200:

            fichiers = r.json()

            utilisateurs = []

            for f in fichiers:

                if f['name'].endswith('.json'):

                    nom_user = f['name'].replace('.json', '')

                    chat_raw, _ = github_action(f"users/{f['name']}")

                    if chat_raw:

                        msgs = json.loads(chat_raw)

                        dernier = "Aucun message"

                        if len(msgs) > 0:
                            dernier = msgs[-1]['content'][:80]

                        utilisateurs.append({
                            "nom": nom_user,
                            "dernier": dernier,
                            "messages": msgs
                        })

            if utilisateurs:

                noms = [u['nom'] for u in utilisateurs]

                choix = st.selectbox(
                    "Sélectionner un utilisateur",
                    noms
                )

                data_user = next(
                    u for u in utilisateurs
                    if u['nom'] == choix
                )

                st.markdown(f"### 👤 {choix}")
                st.info(f"🧠 Dernier message : {data_user['dernier']}")

                historique_txt = ""

                messages_inverses = list(reversed(data_user['messages']))

                for m in messages_inverses:

                    role = "🧑 USER" if m['role'] == 'user' else "🤖 HARTUR"

                    st.markdown(
                        f"**{role}** : {m['content']}"
                    )

                    historique_txt += f"{role}: {m['content']}
```

"

```
                st.download_button(
                    "⬇️ Télécharger la conversation",
                    historique_txt,
                    file_name=f"conversation_{choix}.txt"
                )

    except Exception as e:
        st.error(f"Erreur admin : {e}")

# =========================================
# COMPTES UTILISATEURS
# =========================================

with admin_tab2:

    st.subheader("🔐 Base des Comptes")

    raw, _ = github_action(FICHIER_COMPTES)

    if raw:

        lignes = raw.splitlines()

        for ligne in lignes:

            data = ligne.split(",")

            if len(data) >= 2:

                st.code(
                    f"Utilisateur : {data[0]} | Mot de passe : {data[1]}"
                )

# =========================================
# CORE CONTROL
# =========================================

with admin_tab3:

    st.subheader("⚡ Contrôle Total")

    if st.button("🛑 ÉTEINDRE HARTUR"):
        st.session_state.hartur_off = True
        st.rerun()

    if st.button("🚪 DÉCONNEXION ADMIN"):
        st.session_state.admin = False
        st.rerun()
```

# =====================================================

# MODE HARTUR OFF

# =====================================================

elif st.session_state.hartur_off:

```
st.markdown(
    """
    <style>
    .stApp {
        background-color: black;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <h1 style='text-align:center;color:red;margin-top:20%;'>
    🔒 HARTUR CORE OFFLINE
    </h1>
    <p style='text-align:center;color:white;'>
    Réouvrir HARTUR
    </p>
    """,
    unsafe_allow_html=True
)

code_reboot = st.text_input(
    "Code de réactivation",
    type="password"
)

if code_reboot == MASTER_CODE:
    st.session_state.hartur_off = False
    st.success("HARTUR relancé")
    st.rerun()
```

# =====================================================

# ESPACE CHAT

# =====================================================

elif st.session_state.user:

```
st.markdown(
    '<h2 style="text-align:center;">HARTUR</h2>',
    unsafe_allow_html=True
)

# Affichage historique
for m in st.session_state.msgs:

    with st.chat_message(m["role"]):
        st.write(m["content"])

# Zone utilisateur
if prompt := st.chat_input("Parle avec HARTUR..."):

    # Message utilisateur
    st.session_state.msgs.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.write(prompt)

    # Réponse IA
    with st.chat_message("assistant"):

        try:

            messages = [
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                }
            ]

            # Limite mémoire
            MAX_MSGS = 20
            historique = st.session_state.msgs[-MAX_MSGS:]

            messages.extend(historique)

            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=messages,
                temperature=0.9
            )

            reponse = response.choices[0].message.content

            st.write(reponse)

            st.session_state.msgs.append({
                "role": "assistant",
                "content": reponse
            })

            # =====================================
            # SAUVEGARDE UTILISATEUR
            # =====================================

            fichier_user = f"users/{st.session_state.user}.json"

            ancien, sha = github_action(fichier_user)

            github_action(
                fichier_user,
                "PUT",
                json.dumps(st.session_state.msgs),
                sha
            )

        except Exception as e:
            st.error(f"Erreur IA : {e}")
```

# =====================================================

# PAGE D'ACCUEIL

# =====================================================

else:

```
st.markdown(
    '<h1 class="giant-title">HARTUR</h1>',
    unsafe_allow_html=True
)

st.markdown(
    '<p class="signature-zac">CRÉÉ PAR ZACMITE</p>',
    unsafe_allow_html=True
)

col_l, col_m, col_r = st.columns([1, 1.8, 1])

with col_m:

    tab1, tab2 = st.tabs([
        "CONNEXION",
        "REJOINDRE"
    ])

    # =========================================
    # CONNEXION
    # =========================================

    with tab1:

        u = st.text_input("Pseudo")
        p = st.text_input("Clé", type="password")

        if st.button("ENTRER"):

            raw, _ = github_action(FICHIER_COMPTES)

            if raw:

                lignes = raw.splitlines()

                valide = False

                for ligne in lignes:

                    data = ligne.split(",")

                    if len(data) >= 2:

                        user_csv = data[0]
                        pass_csv = data[1]

                        if u == user_csv and p == pass_csv:
                            valide = True
                            break

                if valide:

                    st.session_state.user = u

                    # Chargement historique
                    fichier_user = f"users/{u}.json"

                    ancien_chat, _ = github_action(fichier_user)

                    if ancien_chat:
                        st.session_state.msgs = json.loads(ancien_chat)

                    st.success("Connexion réussie")
                    st.rerun()

                else:
                    st.error("Pseudo ou mot de passe incorrect")

    # =========================================
    # INSCRIPTION
    # =========================================

    with tab2:

        new_user = st.text_input("Nouveau pseudo")
        new_pass = st.text_input(
            "Nouveau mot de passe",
            type="password"
        )

        if st.button("CRÉER UN COMPTE"):

            raw, sha = github_action(FICHIER_COMPTES)

            if raw:
                contenu = raw + f"\n{new_user},{new_pass}"
            else:
                contenu = f"{new_user},{new_pass}"

            github_action(
                FICHIER_COMPTES,
                "PUT",
                contenu,
                sha
            )

            st.success("Compte créé avec succès")
```

# IMPORTANT

#

# Dans `.streamlit/secrets.toml` ajoute :

#

# GITHUB_TOKEN="TON_GITHUB_TOKEN"

# OPENAI_API_KEY="TA_CLE_OPENAI"

#

# Installation :

# pip install openai
