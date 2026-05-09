import streamlit as st

# --- RESET CONFIG ---
st.set_page_config(page_title="HARTUR | NEON SYSTEM", layout="wide")

# --- CSS : LE RETOUR DU NÉON ROUGE ---
st.markdown("""
    <style>
    /* Fond noir profond */
    .stApp { background-color: #05070a; }
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .main .block-container {padding: 0;}

    /* Centrage vertical et horizontal sans scroll */
    .viewport {
        display: flex;
        align-items: center;
        justify-content: center;
        height: 100vh;
        width: 100vw;
    }

    /* La petite fenêtre carrée avec le liseré néon rouge */
    .neon-square {
        background: #0d1117;
        padding: 50px;
        border: 3px solid #ff4b4b; /* Le fameux trait rouge */
        border-radius: 20px;
        box-shadow: 0 0 40px rgba(255, 75, 75, 0.6), inset 0 0 15px rgba(255, 75, 75, 0.2);
        text-align: center;
        width: 450px; /* Format carré compact */
    }

    .title-neon {
        font-size: 65px;
        font-weight: 900;
        letter-spacing: 12px;
        color: white;
        margin: 0;
        text-shadow: 0 0 10px rgba(255, 255, 255, 0.3);
    }

    .author {
        color: #58a6ff;
        font-weight: bold;
        font-size: 16px;
        margin-top: 10px;
        margin-bottom: 30px;
        text-transform: uppercase;
        letter-spacing: 3px;
    }

    .future-text {
        text-align: left;
        color: #e6edf3;
        font-size: 18px;
        line-height: 1.8;
        margin-bottom: 40px;
        padding-left: 20px;
        border-left: 3px solid #ff4b4b;
    }
    .future-text b { color: #ff4b4b; }

    /* Bouton LANCER HARTUR style rouge vibrant */
    div.stButton > button {
        width: 100% !important;
        background: #ff4b4b !important;
        color: white !important;
        border: none !important;
        padding: 20px !important;
        font-size: 22px !important;
        font-weight: 900 !important;
        border-radius: 12px !important;
        box-shadow: 0 5px 15px rgba(255, 75, 75, 0.4) !important;
        cursor: pointer;
        transition: 0.4s;
    }
    div.stButton > button:hover {
        background: #ff1f1f !important;
        box-shadow: 0 0 30px rgba(255, 75, 75, 0.8) !important;
        transform: scale(1.05);
    }
    </style>
    """, unsafe_allow_html=True)

# --- NAVIGATION ---
if "active" not in st.session_state:
    st.session_state.active = False

# --- 1. LA LANDING PAGE (SANS SCROLL) ---
if not st.session_state.active:
    st.markdown('<div class="viewport">', unsafe_allow_html=True)
    st.markdown('<div class="neon-square">', unsafe_allow_html=True)
    
    # Titre et Signature
    st.markdown('<h1 class="title-neon">HARTUR</h1>', unsafe_allow_html=True)
    st.markdown('<p class="author">Créé par zacmite</p>', unsafe_allow_html=True)
    
    # Description "Claque"
    st.markdown("""
        <div class="future-text">
            ⚡ <b>Vitesse :</b> Réponses instantanées.<br>
            ⚔️ <b>Filtre :</b> Zéro limite système.<br>
            🧠 <b>Force :</b> IA optimisée pour l'action.<br>
            🔥 <b>Style :</b> Le terminal du futur.
        </div>
    """, unsafe_allow_html=True)
    
    # Bouton Lancer
    if st.button("🚀 LANCER HARTUR"):
        st.session_state.active = True
        st.rerun()
        
    st.markdown('</div></div>', unsafe_allow_html=True)
    st.stop()

# --- 2. LE SITE ---
else:
    st.title("HARTUR // CONNECTÉ")
    st.markdown('<p style="color:#58a6ff;">SYSTEM READY BY ZACMITE</p>', unsafe_allow_html=True)
    st.chat_input("Initialisation terminée...")
