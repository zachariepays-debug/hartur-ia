import streamlit as st

# --- CONFIGURATION ---
st.set_page_config(page_title="HARTUR", layout="wide")

# --- LE STYLE NÉON (PROPRE & CENTRÉ) ---
st.markdown("""
    <style>
    /* On cache tout le surplus de Streamlit pour ne pas avoir de scroll */
    .stApp { background-color: #05070a; }
    header {visibility: hidden;}
    .main .block-container {padding: 0;}

    /* Conteneur pour verrouiller la fenêtre au milieu de l'écran */
    .centrage-total {
        display: flex;
        align-items: center;
        justify-content: center;
        height: 100vh;
        width: 100vw;
    }

    /* La petite fenêtre carrée avec le liseré rouge */
    .boite-neon {
        background: #0d1117;
        padding: 40px;
        border: 2px solid #ff4b4b;
        border-radius: 15px;
        box-shadow: 0 0 25px rgba(255, 75, 75, 0.4);
        text-align: center;
        width: 400px; /* Format petit carré */
    }

    .titre {
        font-size: 50px;
        font-weight: 900;
        letter-spacing: 8px;
        color: white;
        margin: 0;
    }

    .signature {
        color: #58a6ff;
        font-size: 14px;
        font-weight: bold;
        margin-bottom: 25px;
    }

    .description-futur {
        text-align: left;
        color: #e6edf3;
        font-size: 16px;
        line-height: 1.6;
        margin-bottom: 30px;
        border-left: 3px solid #ff4b4b;
        padding-left: 15px;
    }
    .description-futur b { color: #ff4b4b; }

    /* Bouton Lancer Hartur */
    div.stButton > button {
        width: 100% !important;
        background: #ff4b4b !important;
        color: white !important;
        font-weight: 900 !important;
        padding: 15px !important;
        border-radius: 8px !important;
        border: none !important;
        cursor: pointer;
        text-transform: uppercase;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIQUE ---
if "lance" not in st.session_state:
    st.session_state.lance = False

# --- AFFICHAGE DE LA FENÊTRE ---
if not st.session_state.lance:
    st.markdown('<div class="centrage-total">', unsafe_allow_html=True)
    st.markdown('<div class="boite-neon">', unsafe_allow_html=True)
    
    # Titre et Auteur
    st.markdown('<div class="titre">HARTUR</div>', unsafe_allow_html=True)
    st.markdown('<div class="signature">CRÉÉ PAR ZACMITE</div>', unsafe_allow_html=True)
    
    # Description "Claque"
    st.markdown("""
        <div class="description-futur">
            🚀 <b>Vitesse :</b> Réponses instantanées.<br>
            ⚔️ <b>Filtre :</b> Aucune limite système.<br>
            🧠 <b>Force :</b> IA optimisée pour l'action.<br>
            🔥 <b>Style :</b> Le terminal du futur.
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("LANCER HARTUR"):
        st.session_state.lance = True
        st.rerun()
        
    st.markdown('</div></div>', unsafe_allow_html=True)
    st.stop()

# --- LE RESTE DU SITE ---
else:
    st.title("HARTUR // TERMINAL")
    st.chat_input("Pose ta question...")
