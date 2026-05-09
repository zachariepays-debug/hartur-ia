import streamlit as st
import pandas as pd
import requests
import base64
from io import StringIO

# --- CONFIGURATION ---
REPO_NOM = "zachariepays-debug/Hartur-ia" 
FICHIER_COMPTES = "comptes.csv"
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]

st.set_page_config(page_title="HARTUR | PROJET X", layout="wide", page_icon="🔥")

# --- CSS : LE CADRE NÉON ULTIME ---
st.markdown("""
    <style>
    /* Fond OLED Noir */
    .stApp { background-color: #05070a; color: #e6edf3; }
    
    /* Conteneur pour le centrage absolu sur l'écran */
    .hero-wrapper {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 80vh;
        text-align: center;
    }
    
    /* La petite "Carte" Néon Rouge stylée */
    .neon-poster {
        background: rgba(13, 17, 23, 0.9);
        padding: 50px;
        border-radius: 20px;
        border: 2px solid #ff4b4b;
        max-width: 650px;
        box-shadow: 0 0 40px rgba(255, 75, 75, 0.4);
        position: relative;
    }
    
    /* Titre HARTUR */
    .giant-title { 
        font-size: clamp(40px, 8vw, 75px);
        font-weight: 900; 
        letter-spacing: 12px; 
        color: white; 
        margin: 0;
        line-height: 1.1;
    }
    
    /* Signature Créé par zacmite */
    .signature-zac { 
        color: #58a6ff; 
        font-weight: bold; 
        font-size: clamp(14px, 2vw, 18px); 
        margin-top: 10px;
        text-transform: uppercase;
        letter-spacing: 2px;
    }

    /* Description Claque, alignée à gauche */
    .claque-desc {
        text-align: left;
        display: inline-block;
        font-size: clamp(16px, 2vw, 20px);
        line-height: 1.8;
        margin: 30px 0;
        border-left: 3px solid #ff4b4b;
        padding-left: 20px;
    }
    .claque-desc b { color: #ff4b4b; }

    /* Bouton d'entrée */
    div.stButton > button {
        background: linear-gradient(90deg, #ff4b4b 0%, #ff1f1f 100%) !important;
        color: white !important;
        border: none !important;
        padding: clamp(15px, 2vw, 20px) 50px !important;
        font-size: clamp(18px, 2vw, 22px) !important;
        font-weight: 900 !important;
        border-radius: 12px !important;
        box-shadow: 0 5px 20px rgba(255, 75, 75, 0.3) !important;
        cursor: pointer;
        transition: 0.3s;
    }
    div.stButton > button:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(255, 75, 75, 0.6) !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- NAVIGATION ---
if "launched" not in st.session_state:
    st.session_state.launched = False

# --- ÉTAPE 1 : L'AFFICHE NÉON ---
if not st.session_state.launched:
    st.markdown('<div class="hero-wrapper">', unsafe_allow_html=True)
    
    st.markdown('<div class="neon-poster">', unsafe_allow_html=True)
    
    # Titre + Signature
    st.markdown('<h1 class="giant-title">HARTUR</h1>', unsafe_allow_html=True)
    st.markdown('<p class="signature-zac">Créé par zacmite</p>', unsafe_allow_html=True)
    
    # Description du futur
    st.markdown("""
        <div class="claque-desc">
            🧬 <b>Système Neural :</b> Une IA ninja optimisée pour la vitesse pure.<br>
            ⚔️ <b>Zéro Filtre :</b> Précision chirurgicale, sans aucune censure.<br>
            📡 <b>Omniprésence :</b> Code, stratégie, et analyse en temps réel.<br>
            🔥 <b>Style Impact :</b> Conçu pour ceux qui n'ont pas de temps à perdre.
        </div>
    """, unsafe_allow_html=True)
    
    # Bouton d'entrée
    if st.button("Initialiser la connexion"):
        st.session_state.launched = True
        st.rerun()
        
    st.markdown('</div></div>', unsafe_allow_html=True)

# --- ÉTAPE 2 : LE TERMINAL (VISIBLE APRÈS CLIC) ---
else:
    st.title("HARTUR // TERMINAL ACTIVÉ")
    st.markdown('<p class="signature-zac" style="text-align:left;">Créé par zacmite</p>', unsafe_allow_html=True)
    st.chat_input("Le terminal est opérationnel...")
