import streamlit as st

# --- CONFIGURATION ---
st.set_page_config(page_title="HARTUR | INTERFACE", layout="wide", page_icon="🔥")

# --- CSS : CENTRAGE ABSOLU ET NETTOYAGE ---
st.markdown("""
    <style>
    /* Fond OLED et suppression des marges Streamlit qui décalent tout */
    .stApp { background-color: #05070a; }
    header {visibility: hidden;}
    .main .block-container {padding-top: 0rem; padding-bottom: 0rem;}

    /* Conteneur de centrage vertical et horizontal total */
    .viewport-center {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 100vh; /* Prend toute la hauteur de l'écran */
        width: 100%;
    }
    
    /* La Carte Néon compacte et centrée */
    .neon-card {
        background: rgba(13, 17, 23, 0.95);
        padding: 45px;
        border-radius: 20px;
        border: 2px solid #ff4b4b;
        max-width: 600px;
        box-shadow: 0 0 40px rgba(255, 75, 75, 0.4);
        text-align: center;
    }
    
    .giant-title { 
        font-size: 70px;
        font-weight: 900; 
        letter-spacing: 12px; 
        color: white; 
        margin: 0;
        line-height: 1;
    }
    
    .signature-zac { 
        color: #58a6ff; 
        font-weight: bold; 
        font-size: 18px; 
        margin-top: 10px;
        letter-spacing: 2px;
        text-transform: uppercase;
    }

    .claque-desc {
        text-align: left;
        font-size: 19px;
        line-height: 1.7;
        color: #e6edf3;
        margin: 35px 0;
        border-left: 3px solid #ff4b4b;
        padding-left: 20px;
    }
    .claque-desc b { color: #ff4b4b; }

    /* Bouton d'entrée centré */
    div.stButton > button {
        width: 100% !important;
        background: linear-gradient(90deg, #ff4b4b 0%, #8b0000 100%) !important;
        color: white !important;
        border: none !important;
        padding: 18px !important;
        font-size: 22px !important;
        font-weight: 900 !important;
        border-radius: 12px !important;
        box-shadow: 0 10px 30px rgba(255, 75, 75, 0.4) !important;
        cursor: pointer;
    }
    </style>
    """, unsafe_allow_html=True)

# --- NAVIGATION ---
if "launched" not in st.session_state:
    st.session_state.launched = False

# --- 1. L'AFFICHE (DANS LE VIEWPORT CENTRÉ) ---
if not st.session_state.launched:
    # Ce div force le contenu au milieu exact de l'écran
    st.markdown('<div class="viewport-center">', unsafe_allow_html=True)
    
    st.markdown('<div class="neon-card">', unsafe_allow_html=True)
    
    # Titre + Signature
    st.markdown('<h1 class="giant-title">HARTUR</h1>', unsafe_allow_html=True)
    st.markdown('<p class="signature-zac">Créé par zacmite</p>', unsafe_allow_html=True)
    
    # Description
    st.markdown("""
        <div class="claque-desc">
            🧬 <b>Système Neural :</b> Une IA ninja optimisée pour la vitesse.<br>
            ⚔️ <b>Zéro Filtre :</b> Précision chirurgicale, sans censure.<br>
            📡 <b>Omniprésence :</b> Analyse et stratégie en temps réel.<br>
            🔥 <b>Impact Brut :</b> Pas de temps à perdre, juste des résultats.
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("INITIALISER LA CONNEXION"):
        st.session_state.launched = True
        st.rerun()
        
    st.markdown('</div>', unsafe_allow_html=True) # Fin neon-card
    st.markdown('</div>', unsafe_allow_html=True) # Fin viewport-center
    st.stop()

# --- 2. LE TERMINAL ---
else:
    st.title("HARTUR // TERMINAL")
    st.markdown('<p class="signature-zac" style="text-align:left;">Créé par zacmite</p>', unsafe_allow_html=True)
    st.chat_input("Système prêt...")
