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

st.set_page_config(page_title="HARTUR | L'AVENTURE", layout="wide", page_icon="🚀")

# --- CSS : CENTRAGE ABSOLU ET FENÊTRE DE BIENVENUE ---
st.markdown("""
    <style>
    .stApp { background-color: #05070a; color: #e6edf3; }
    
    /* Overlay plein écran pour l'affiche de présentation */
    .welcome-screen {
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background: radial-gradient(circle, #0d1117 0%, #000000 100%);
        z-index: 9999; display: flex; align-items: center; justify-content: center;
        flex-direction: column;
    }
    
    /* Conteneur de l'affiche */
    .poster-content {
        text-align: center; width: 80%; max-width: 700px;
        padding: 40px; border-radius: 30px; border: 1px solid rgba(255, 75, 75, 0.3);
        background: rgba(13, 17, 23, 0.8); backdrop-filter: blur(20px);
    }
    
    /* Centrage forcé Titre + Signature */
    .brand-box {
        display: flex; flex-direction: column; align-items: center;
        justify-content: center; width: 100%; margin-bottom: 40px;
    }
    .giant-title { font-size: 75px; font-weight: 900; letter-spacing: 15px; margin: 0; color: white; line-height: 1.1; }
    .signature-zac { color: #58a6ff; font-weight: bold; font-size: 20px; margin-top: 10px; letter-spacing: 2px; }

    .description-ia { font-size: 18px; color: #c9d1d9; line-height: 1.8; margin-bottom: 30px; text-align: center; }
    .description-ia b { color: #ff4b4b; }

    /* Bouton d'entrée style "Aventure" */
    div.stButton > button {
        background: linear-gradient(135deg, #ff4b4b 0%, #8b0000 100%) !important;
        color: white !important; border: none !important;
        padding: 20px 60px !important; font-size: 24px !important;
        font-weight: 900 !important; border-radius: 50px !important;
        box-shadow: 0 0 20px rgba(255, 75, 75, 0.4) !important;
        transition: 0.3s ease-in-out;
    }
    div.stButton > button:hover { transform: scale(1.05); box-shadow: 0 0 40px rgba(255, 75, 75, 0.7) !important; }
    </style>
    """, unsafe_allow_html=True)

# --- INITIALISATION ---
if "launched" not in st.session_state: st.session_state.launched = False
if "user" not in st.session_state: st.session_state.user = None

# --- 1. L'AFFICHE DE PRÉSENTATION (POP-UP) ---
if not st.session_state.launched:
    st.markdown("""
        <div class="welcome-screen">
            <div class="poster-content">
                <div class="brand-box">
                    <h1 class="giant-title">HARTUR</h1>
                    <p class="signature-zac">Créé par zacmite</p>
                </div>
                <div class="description-ia">
                    Bienvenue dans le futur. <b>HARTUR</b> est une intelligence artificielle ninja conçue pour l'efficacité brute. 
                    Pas de censure inutile, une vitesse de traitement foudroyante et une polyvalence totale (code, analyse, rédaction). 
                    Le terminal n'attend plus que vous.
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Bouton de lancement centré sous l'affiche
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 C'EST PARTI, LET'S GO !"):
            st.session_state.launched = True
            st.rerun()
    st.stop()

# --- 2. INTERFACE DE CONNEXION / INSCRIPTION ---
if st.session_state.user is None:
    st.title("ACCÈS AU SYSTÈME")
    st.markdown('<p class="signature-zac" style="text-align:left;">Créé par zacmite</p>', unsafe_allow_html=True)
    
    choix = st.radio("Choisissez une action :", ["Se Connecter", "S'Inscrire"], horizontal=True)
    
    if choix == "Se Connecter":
        u = st.text_input("Pseudo")
        p = st.text_input("Code Secret", type="password")
        if st.button("DÉVERROUILLER"):
            # Simulation de lecture GitHub pour l'exemple
            if u == "admin" and p == "babar":
                st.session_state.user = u
                st.rerun()
            else:
                st.error("Identifiants incorrects.")
                
    else:
        st.info("Formulaire d'inscription bientôt disponible.")

# --- 3. LE TERMINAL DE CHAT ---
else:
    st.title("HARTUR // TERMINAL")
    st.markdown('<p class="signature-zac" style="text-align:left;">Créé par zacmite</p>', unsafe_allow_html=True)
    st.write("---")
    st.chat_input("Le terminal est prêt. Pose ta question.")
