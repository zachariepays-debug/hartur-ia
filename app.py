import streamlit as st
import pandas as pd
import requests
import base64
from io import StringIO

# --- CONFIGURATION ---
REPO_NOM = "zachariepays-debug/Hartur-ia" 
FICHIER_COMPTES = "comptes.csv"
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]

st.set_page_config(page_title="HARTUR | BIENVENUE", layout="wide", page_icon="🔥")

# --- CSS : DESIGN ÉPURÉ ET CENTRAGE ---
st.markdown("""
    <style>
    .stApp { background-color: #05070a; color: #e6edf3; }
    
    /* Conteneur de la page d'accueil */
    .landing-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        padding: 100px 20px;
    }
    
    /* Box avec le trait rouge */
    .description-card {
        border: 2px solid #ff4b4b;
        padding: 50px;
        border-radius: 20px;
        max-width: 800px;
        background: #0d1117;
        box-shadow: 0 0 30px rgba(255, 75, 75, 0.2);
    }
    
    .giant-title { 
        font-size: 80px; 
        font-weight: 900; 
        letter-spacing: 12px; 
        color: white; 
        margin: 0;
    }
    
    .signature-zac { 
        color: #58a6ff; 
        font-weight: bold; 
        font-size: 20px; 
        margin-top: 10px;
        margin-bottom: 40px;
    }

    .promo-text {
        font-size: 22px;
        line-height: 1.6;
        color: #c9d1d9;
        text-align: left;
        margin-bottom: 40px;
    }
    .promo-text b { color: #ff4b4b; }

    /* Bouton d'entrée */
    div.stButton > button {
        background: linear-gradient(90deg, #ff4b4b, #8b0000) !important;
        color: white !important;
        border: none !important;
        padding: 20px 50px !important;
        font-size: 22px !important;
        font-weight: bold !important;
        border-radius: 10px !important;
        cursor: pointer;
    }
    </style>
    """, unsafe_allow_html=True)

# --- GESTION DE LA NAVIGATION ---
if "page" not in st.session_state:
    st.session_state.page = "accueil"

# --- ÉTAPE 1 : L'AFFICHE DE BIENVENUE ---
if st.session_state.page == "accueil":
    st.markdown('<div class="landing-container">', unsafe_allow_html=True)
    
    st.markdown('<div class="description-card">', unsafe_allow_html=True)
    
    # Centrage Titre + Signature
    st.markdown('<h1 class="giant-title">HARTUR</h1>', unsafe_allow_html=True)
    st.markdown('<p class="signature-zac">Créé par zacmite</p>', unsafe_allow_html=True)
    
    # Description du futur
    st.markdown("""
        <div class="promo-text">
            🚀 <b>Vitesse :</b> Des réponses sans aucun temps mort.<br>
            🛡️ <b>Sécurité :</b> Tes données sont cryptées et protégées.<br>
            🧠 <b>Intelligence :</b> Un expert IA pour le code et la rédaction.<br>
            🔥 <b>Style :</b> Pas de blabla, juste de l'efficacité pure.<br><br>
            <i>Prêt à libérer la puissance du terminal ?</i>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("ACCÉDER AU SITE"):
        st.session_state.page = "site"
        st.rerun()
        
    st.markdown('</div></div>', unsafe_allow_html=True)

# --- ÉTAPE 2 : LE SITE (CONNEXION / CHAT) ---
else:
    st.title("HARTUR // TERMINAL")
    st.markdown('<p class="signature-zac" style="text-align:left;">Créé par zacmite</p>', unsafe_allow_html=True)
    
    if st.button("← Retour à l'accueil"):
        st.session_state.page = "accueil"
        st.rerun()
    
    st.write("---")
    st.chat_input("Pose ta question ici...")
