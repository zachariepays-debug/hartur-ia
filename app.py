import streamlit as st

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="HARTUR | SYSTEM", layout="wide", page_icon="🔥")

# --- STYLE CSS (LE CARRÉ NÉON SANS SCROLL) ---
st.markdown("""
    <style>
    /* On nettoie l'interface Streamlit pour le mode landing */
    .stApp { background-color: #05070a; }
    header {visibility: hidden;}
    .main .block-container {padding: 0;}

    /* Conteneur plein écran pour centrer la petite fenêtre */
    .screen-center {
        display: flex;
        align-items: center;
        justify-content: center;
        height: 100vh;
        width: 100vw;
    }

    /* La petite fenêtre carrée stylée */
    .hartur-box {
        background: #0d1117;
        padding: 40px;
        border: 2px solid #ff4b4b;
        border-radius: 15px;
        box-shadow: 0 0 30px rgba(255, 75, 75, 0.3);
        text-align: center;
        max-width: 450px;
        width: 90%;
    }

    .title {
        font-size: 55px;
        font-weight: 900;
        letter-spacing: 10px;
        color: white;
        margin-bottom: 5px;
    }

    .sub-title {
        color: #58a6ff;
        font-weight: bold;
        font-size: 14px;
        text-transform: uppercase;
        margin-bottom: 30px;
    }

    .desc {
        text-align: left;
        color: #e6edf3;
        font-size: 17px;
        line-height: 1.6;
        margin-bottom: 35px;
        border-left: 3px solid #ff4b4b;
        padding-left: 15px;
    }
    .desc b { color: #ff4b4b; }

    /* Bouton LANCER HARTUR */
    div.stButton > button {
        width: 100% !important;
        background: linear-gradient(90deg, #ff4b4b 0%, #a80000 100%) !important;
        color: white !important;
        border: none !important;
        padding: 18px !important;
        font-size: 20px !important;
        font-weight: 900 !important;
        border-radius: 8px !important;
        text-transform: uppercase;
        cursor: pointer;
        transition: 0.3s;
    }
    div.stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 0 20px rgba(255, 75, 75, 0.5) !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIQUE D'AFFICHAGE ---
if "access" not in st.session_state:
    st.session_state.access = False

# --- 1. LA FENÊTRE DE BIENVENUE ---
if not st.session_state.access:
    st.markdown('<div class="screen-center">', unsafe_allow_html=True)
    st.markdown('<div class="hartur-box">', unsafe_allow_html=True)
    
    # Header
    st.markdown('<div class="title">HARTUR</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">SYSTÈME NEURAL PAR ZACMITE</div>', unsafe_allow_html=True)
    
    # Description "Claque"
    st.markdown("""
        <div class="desc">
            ⚡ <b>Vitesse Brute :</b> Zéro latence, réponse directe.<br>
            ⚔️ <b>Zéro Filtre :</b> Une liberté totale d'exécution.<br>
            🧠 <b>Multitâche :</b> Code, analyse et stratégie futuriste.<br>
            🔥 <b>ADN Ninja :</b> Conçu pour l'efficacité pure.
        </div>
    """, unsafe_allow_html=True)
    
    # Bouton de lancement
    if st.button("🚀 LANCER HARTUR"):
        st.session_state.access = True
        st.rerun()
        
    st.markdown('</div></div>', unsafe_allow_html=True)
    st.stop()

# --- 2. LE SITE PRINCIPAL ---
else:
    st.title("HARTUR // ACCÈS TOTAL")
    st.markdown('<p style="color:#58a6ff; font-weight:bold;">CRÉÉ PAR ZACMITE</p>', unsafe_allow_html=True)
    st.chat_input("Le terminal est à toi...")
