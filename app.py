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

# --- CSS : CENTRAGE ET BOUTON INTÉGRÉ ---
st.markdown("""
    <style>
    .stApp { background-color: #05070a; color: #e6edf3; }
    
    .welcome-overlay {
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0,0,0,0.95); z-index: 9999;
        display: flex; align-items: center; justify-content: center;
    }
    
    .neon-box {
        background: #0d1117; padding: 60px; border-radius: 20px;
        border: 2px solid #ff4b4b; width: 85%; max-width: 800px;
        text-align: center; box-shadow: 0px 0px 50px rgba(255, 75, 75, 0.4);
        display: flex; flex-direction: column; align-items: center;
    }
    
    .giant-title { font-size: 70px; font-weight: 900; letter-spacing: 12px; color: white; margin: 0; }
    .signature-zac { color: #58a6ff; font-weight: bold; font-size: 20px; margin-top: 5px; margin-bottom: 30px; }

    .description-text { font-size: 19px; line-height: 1.8; color: #c9d1d9; margin-bottom: 40px; text-align: left; }
    .description-text b { color: #ff4b4b; }

    /* Style du bouton Streamlit pour qu'il s'intègre parfaitement */
    .stButton > button {
        width: 100% !important;
        background: linear-gradient(90deg, #ff4b4b, #8b0000) !important;
        color: white !important; border: none !important;
        padding: 20px !important; font-size: 24px !important;
        font-weight: 900 !important; border-radius: 12px !important;
        box-shadow: 0px 10px 30px rgba(255, 75, 75, 0.3) !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- INITIALISATION ---
if "launched" not in st.session_state: st.session_state.launched = False
if "user" not in st.session_state: st.session_state.user = None

# --- 1. L'AFFICHE NÉON AVEC BOUTON INTERNE ---
if not st.session_state.launched:
    # On crée la structure de la box
    with st.container():
        st.markdown('<div class="welcome-overlay">', unsafe_allow_html=True)
        st.markdown('<div class="neon-box">', unsafe_allow_html=True)
        
        # Titre et Signature centrés
        st.markdown('<h1 class="giant-title">HARTUR</h1>', unsafe_allow_html=True)
        st.markdown('<p class="signature-zac">Créé par zacmite</p>', unsafe_allow_html=True)
        
        # Description complète
        st.markdown("""
            <div class="description-text">
                🚀 <b>Vitesse Extrême :</b> Réponses instantanées.<br>
                🛡️ <b>Sécurité Totale :</b> Cryptage de vos données.<br>
                🧠 <b>IA Multi-Tâches :</b> Expert en code et rédaction.<br>
                🔥 <b>Pote du Futur :</b> Efficacité brute sans blabla.<br>
                ⚡ <b>Liberté :</b> Aucune restriction système.
            </div>
        """, unsafe_allow_html=True)
        
        # LE BOUTON EST ICI, DANS LA BOX
        if st.button("🚀 LANCER L'AVENTURE"):
            st.session_state.launched = True
            st.rerun()
            
        st.markdown('</div></div>', unsafe_allow_html=True)
    st.stop()

# --- 2. RESTE DU SITE (Accessible uniquement après clic) ---
st.title("HARTUR // TERMINAL ACTIVÉ")
st.markdown('<p class="signature-zac">Créé par zacmite</p>', unsafe_allow_html=True)

if st.session_state.user is None:
    tab1, tab2 = st.tabs(["CONNEXION", "INSCRIPTION"])
    # ... suite du code de connexion ...
