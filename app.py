import streamlit as st
import pandas as pd
import requests
import base64
import json
from io import StringIO

# --- CONFIGURATION ---
REPO_NOM = "zachariepays-debug/Hartur-ia" 
FICHIER_COMPTES = "comptes.csv"
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
MASTER_CODE = "babar"

st.set_page_config(page_title="HARTUR | SYSTEM", layout="wide", page_icon="🔥")

# --- CSS : LE RETOUR DU STYLE NÉON ROUGE ET CENTRAGE ---
st.markdown("""
    <style>
    .stApp { background-color: #05070a; color: #e6edf3; }
    
    /* Overlay pour bloquer le site tant qu'on n'a pas cliqué */
    .welcome-overlay {
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0,0,0,0.9); z-index: 9999;
        display: flex; flex-direction: column; align-items: center; justify-content: center;
    }
    
    /* La fenêtre avec le trait rouge qui claque */
    .neon-box {
        background: #0d1117; padding: 50px; border-radius: 20px;
        border: 2px solid #ff4b4b; width: 85%; max-width: 800px;
        text-align: center; box-shadow: 0px 0px 40px rgba(255, 75, 75, 0.3);
        display: flex; flex-direction: column; align-items: center;
    }
    
    /* Centrage Titre + Signature */
    .title-container { margin-bottom: 30px; width: 100%; }
    .giant-title { font-size: 70px; font-weight: 900; letter-spacing: 12px; color: white; margin: 0; }
    .signature-zac { color: #58a6ff; font-weight: bold; font-size: 20px; margin-top: 5px; letter-spacing: 2px; }

    /* Description */
    .description-text { font-size: 19px; line-height: 1.8; color: #c9d1d9; margin: 20px 0; text-align: left; display: inline-block; }
    .description-text b { color: #ff4b4b; }

    /* Bouton d'entrée "Let's Go" */
    div.stButton > button {
        background: linear-gradient(90deg, #ff4b4b, #8b0000) !important;
        color: white !important; border: none !important;
        padding: 20px 70px !important; font-size: 24px !important;
        font-weight: 900 !important; border-radius: 12px !important;
        box-shadow: 0px 10px 30px rgba(255, 75, 75, 0.4) !important;
        cursor: pointer;
    }
    </style>
    """, unsafe_allow_html=True)

# --- INITIALISATION ---
if "launched" not in st.session_state: st.session_state.launched = False
if "user" not in st.session_state: st.session_state.user = None

# --- 1. L'AFFICHE NÉON (POP-UP BLOQUANTE) ---
if not st.session_state.launched:
    st.markdown("""
        <div class="welcome-overlay">
            <div class="neon-box">
                <div class="title-container">
                    <h1 class="giant-title">HARTUR</h1>
                    <p class="signature-zac">Créé par zacmite</p>
                </div>
                <div class="description-text">
                    🚀 <b>Vitesse Extrême :</b> Réponses instantanées, précision chirurgicale.<br>
                    🛡️ <b>Sécurité Totale :</b> Chiffrement de bout en bout de vos échanges.<br>
                    🧠 <b>IA Multi-Tâches :</b> Un expert en code, rédaction et analyse.<br>
                    🔥 <b>Pote du Futur :</b> Une IA cash, sans blabla inutile.<br>
                    ⚡ <b>Liberté Totale :</b> Aucune barrière, juste de l'efficacité brute.
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Bouton placé physiquement ici pour être cliquable par Streamlit
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 C'EST PARTI, LET'S GO !"):
            st.session_state.launched = True
            st.rerun()
    st.stop()

# --- 2. ACCÈS AU SITE (CONNEXION / INSCRIPTION) ---
st.title("HARTUR // ACCÈS AU TERMINAL")
st.markdown('<p class="signature-zac">Créé par zacmite</p>', unsafe_allow_html=True)

if st.session_state.user is None:
    tab1, tab2 = st.tabs(["ME CONNECTER", "M'INSCRIRE"])
    with tab1:
        u = st.text_input("Pseudo")
        p = st.text_input("Mot de passe", type="password")
        if st.button("DÉVERROUILLER"):
            # Ici ta logique GitHub habituelle
            st.success("Connexion en cours...")
    with tab2:
        st.info("Espace de création de compte.")
else:
    st.write(f"Bienvenue, {st.session_state.user}.")
    st.chat_input("Pose ta question...")
