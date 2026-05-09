import streamlit as st

# --- CONFIGURATION ---
st.set_page_config(page_title="HARTUR | ACCUEIL", layout="wide", page_icon="🔥")

# --- CSS : CENTRAGE ABSOLU ET SUPPRESSION DU SCROLL ---
st.markdown("""
    <style>
    /* 1. On force le fond noir et on cache les éléments inutiles de Streamlit */
    .stApp { background-color: #05070a; }
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .main .block-container {padding: 0;}

    /* 2. Conteneur qui prend 100% de la hauteur visible de l'écran */
    .hero-fullscreen {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 100vh; /* Hauteur totale de la fenêtre */
        width: 100vw;
        margin: 0;
    }
    
    /* 3. La petite fenêtre néon compacte */
    .neon-mini-box {
        background: #0d1117;
        padding: 40px;
        border-radius: 15px;
        border: 2px solid #ff4b4b;
        box-shadow: 0 0 30px rgba(255, 75, 75, 0.4);
        text-align: center;
        width: 90%;
        max-width: 500px; /* On la garde petite et élégante */
    }
    
    .title-hartur { 
        font-size: 60px;
        font-weight: 900; 
        letter-spacing: 8px; 
        color: white; 
        margin: 0;
        line-height: 1;
    }
    
    .signature-zac { 
        color: #58a6ff; 
        font-weight: bold; 
        font-size: 16px; 
        margin-top: 8px;
        text-transform: uppercase;
    }

    .description-claque {
        text-align: left;
        font-size: 17px;
        color: #c9d1d9;
        margin: 25px 0;
        line-height: 1.6;
    }
    .description-claque b { color: #ff4b4b; }

    /* Bouton d'entrée */
    div.stButton > button {
        width: 100% !important;
        background: linear-gradient(90deg, #ff4b4b 0%, #8b0000 100%) !important;
        color: white !important;
        border: none !important;
        padding: 15px !important;
        font-size: 20px !important;
        font-weight: 900 !important;
        border-radius: 10px !important;
        cursor: pointer;
    }
    </style>
    """, unsafe_allow_html=True)

# --- NAVIGATION ---
if "site_access" not in st.session_state:
    st.session_state.site_access = False

# --- 1. AFFICHAGE DE LA FENÊTRE (SANS SCROLL) ---
if not st.session_state.site_access:
    # On utilise le div plein écran pour centrer la box
    st.markdown('<div class="hero-fullscreen">', unsafe_allow_html=True)
    
    st.markdown('<div class="neon-mini-box">', unsafe_allow_html=True)
    
    # Contenu de la box
    st.markdown('<h1 class="title-hartur">HARTUR</h1>', unsafe_allow_html=True)
    st.markdown('<p class="signature-zac">Créé par zacmite</p>', unsafe_allow_html=True)
    
    st.markdown("""
        <div class="description-claque">
            🚀 <b>Vitesse :</b> Réponses instantanées.<br>
            ⚔️ <b>Filtre :</b> Zéro barrière, 100% efficace.<br>
            🧠 <b>Intelligence :</b> Ton pote IA du futur.<br>
            🔥 <b>Style :</b> Un terminal brut et puissant.
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("Lancer le terminal"):
        st.session_state.site_access = True
        st.rerun()
        
    st.markdown('</div>', unsafe_allow_html=True) # Fin box
    st.markdown('</div>', unsafe_allow_html=True) # Fin fullscreen
    st.stop()

# --- 2. ACCÈS AU SITE ---
else:
    st.title("HARTUR // TERMINAL")
    st.markdown('<p class="signature-zac" style="text-align:left;">Créé par zacmite</p>', unsafe_allow_html=True)
    st.chat_input("Le système est prêt...")
