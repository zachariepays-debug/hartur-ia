import streamlit as st
import requests
from datetime import datetime
import uuid
import os

# ======================================================
# ⚙️ CONFIG
# ======================================================
st.set_page_config(
    page_title="Hartur IA",
    page_icon="🤖",
    layout="wide"
)

# ======================================================
# 🔐 SESSION
# ======================================================
if "admin_mode" not in st.session_state:
    st.session_state.admin_mode = False

if "admin_popup" not in st.session_state:
    st.session_state.admin_popup = False

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = None

if "messages" not in st.session_state:
    st.session_state.messages = []

# ======================================================
# 🔐 BOUTON ADMIN (EN HAUT À DROITE)
# ======================================================
col1, col2 = st.columns([9, 1])

with col2:
    if st.button("🔐 Admin"):
        st.session_state.admin_popup = True

# ======================================================
# 🔐 POPUP ADMIN
# ======================================================
if st.session_state.admin_popup:

    st.warning("🔐 Accès Admin")

    mdp = st.text_input("Mot de passe admin", type="password")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Valider"):

            if mdp == "babar":
                st.session_state.admin_mode = True
                st.session_state.admin_popup = False
                st.success("Mode admin activé 🔓")
                st.rerun()

            else:
                st.error("Mot de passe incorrect")

    with col2:
        if st.button("Annuler"):
            st.session_state.admin_popup = False
            st.rerun()

    st.stop()

# ======================================================
# 💬 INTERFACE PRINCIPALE
# ======================================================
st.title("🤖 Hartur IA")

# ======================================================
# 👤 CONNEXION SIMPLE
# ======================================================
if not st.session_state.logged_in:

    st.subheader("Connexion")

    user = st.text_input("Identifiant")
    pwd = st.text_input("Mot de passe", type="password")

    if st.button("Se connecter"):

        if user and pwd:

            st.session_state.logged_in = True
            st.session_state.username = user

            st.success("Connecté 😄")
            st.rerun()

    st.stop()

# ======================================================
# 👤 USER CONNECTÉ
# ======================================================
st.sidebar.success(f"👤 {st.session_state.username}")

if st.sidebar.button("Déconnexion"):
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.messages = []
    st.rerun()

# ======================================================
# 🔐 MODE ADMIN
# ======================================================
if st.session_state.admin_mode:

    st.subheader("🔐 PANEL ADMIN")

    st.info("Ici tu pourras afficher comptes + conversations")

# ======================================================
# 💬 CHAT
# ======================================================
for m in st.session_state.messages:

    with st.chat_message(m["role"]):
        st.markdown(m["content"])

prompt = st.chat_input("Écris ici...")

if prompt:

    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    # simulation IA
    reponse = "Réponse IA (à connecter)"

    st.session_state.messages.append({
        "role": "assistant",
        "content": reponse
    })

    st.rerun()
