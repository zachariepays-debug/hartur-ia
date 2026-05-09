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

st.set_page_config(page_title="HARTUR | PROJET X", layout="wide", page_icon="⚡")

# --- CSS : L'INTERFACE DU FUTUR (PREMIER PLAN TOTAL) ---
st.markdown("""
    <style>
    .stApp { background-color: #05070a; }
    
    /* Overlay qui recouvre TOUT au premier plan */
    .future-overlay {
        position: fixed;
        top: 0; left: 0;
        width: 100vw; height: 100vh;
        background: radial-gradient(circle at center, #0d1117 0%, #000000 100%);
        z-index: 999999; /* Priorité absolue */
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    /* La fenêtre Néon centrée */
    .neon-card {
        background: rgba(13, 17, 23, 0.9);
        padding: 60px;
        border-radius: 20px;
        border: 2px solid #ff4b4b;
        box-shadow: 0 0 50px rgba(255, 75, 75, 0.3);
        text-align: center;
        max-width: 800px;
        width: 90%;
        backdrop-filter: blur(10px);
    }
    
    /* Centrage parfait du bloc Titre */
    .hero-section {
        display: flex;
        flex-direction: column;
        align-items: center;
        margin-bottom: 40px;
    }
    
    .giant-title { 
        font-size: clamp(50px, 8vw, 85px);
        font-weight: 900;
        letter-spacing: 15px;
        color: white;
        text-shadow: 0 0 20px rgba(255, 255, 255, 0.2);
        margin: 0;
        line-height: 1;
    }
    
    .signature-zac { 
        color: #58a6ff;
        font-weight: bold;
        font-size: 22px;
        margin-top: 15px;
        letter-spacing: 3px;
        text-transform: uppercase;
    }

    /* Description "Claque" */
    .future-desc {
        text-align: left;
        font-size: 20px;
        color: #e6edf3;
        line-height: 1.6;
        margin-bottom: 45px;
        border-left: 3px solid #ff4b4b;
        padding-left: 25px;
    }
    .future-desc b { color: #ff4b4b; text-transform: uppercase; }

    /* Bouton d'entrée Magistral */
    .stButton > button {
        width: 100% !important;
        background: linear-gradient(90deg, #ff4b4b 0%, #8b0000 100%) !important;
        color: white !important;
        border: none !important;
        padding: 25px !important;
        font-size: 26px !important;
        font-weight: 900 !important;
        border-radius: 15px !important;
        box-shadow: 0 10px 40px rgba(255, 75, 75, 0.5) !important;
        transition: 0.4s;
        cursor: pointer;
        text-transform: uppercase;
    }
    .stButton > button:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 50px rgba(255, 75, 75, 0.8) !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ÉTATS ---
if "access_granted" not in st.session_state:
    st.session_state.access_granted = False

# --- 1. L'ENTRÉE DANS LE FUTUR ---
if not st.session_state.access_granted:
    # On enferme tout dans l'overlay
    st.markdown('<div class="future-overlay">', unsafe_allow_html=True)
    st.markdown('<div class="neon-card">', unsafe_allow_html=True)
    
    # Bloc Titre + Signature (Alignement parfait)
    st.markdown("""
        <div class="hero-section">
            <h1 class="giant-title">HARTUR</h1>
            <p class="signature-zac">Créé par zacmite</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Description "Futuriste"
    st.markdown("""
        <div class="future-desc">
            🧬 <b>Système Neural :</b> Une IA ninja optimisée pour la vitesse pure.<br>
            ⚔️ <b>Zéro Limite :</b> Précision chirurgicale, sans aucune censure.<br>
            📡 <b>Omniprésence :</b> Code, stratégie, et analyse en temps réel.<br>
            🔥 <b>Impact Brut :</b> Conçu pour ceux qui n'ont pas de temps à perdre.
        </div>
    """, unsafe_allow_html=True)
    
    # Bouton de sortie intégré à la fenêtre
    if st.button("Initialiser la connexion"):
        st.session_state.access_granted = True
        st.rerun()
        
    st.markdown('</div></div>', unsafe_allow_html=True)
    st.stop() # Bloque tout le reste tant que pas cliqué

# --- 2. LE SITE PRINCIPAL (VISIBLE APRÈS CLIC) ---
st.title("HARTUR // TERMINAL OPÉRATIONNEL")
st.markdown('<p class="signature-zac">Créé par zacmite</p>', unsafe_allow_html=True)
st.chat_input("Le système est prêt...")
