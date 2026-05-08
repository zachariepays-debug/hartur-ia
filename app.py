# ======================================================
# 🎨 STYLE CSS MODERNE
# ======================================================
st.markdown("""
<style>

/* Fond principal */
.stApp {
    background-color: #0f1117;
    color: white;
}

/* Messages chat */
.stChatMessage {
    border-radius: 18px;
    padding: 12px;
    margin-bottom: 10px;
    border: none;
}

/* USER */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    background: linear-gradient(135deg, #2563eb, #1d4ed8);
    border-radius: 20px;
    padding: 15px;
    margin-left: 80px;
    box-shadow: 0 4px 15px rgba(37,99,235,0.4);
}

/* IA */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
    background: linear-gradient(135deg, #1f2937, #111827);
    border-radius: 20px;
    padding: 15px;
    margin-right: 80px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.4);
}

/* Zone input */
.stChatInputContainer {
    background-color: #111827;
    border-radius: 20px;
    padding: 10px;
}

/* Boutons */
.stButton>button {
    border-radius: 15px;
    background: linear-gradient(135deg, #2563eb, #7c3aed);
    color: white;
    border: none;
    transition: 0.3s;
    font-weight: bold;
}

.stButton>button:hover {
    transform: scale(1.03);
}

/* Inputs */
.stTextInput input {
    border-radius: 15px;
}

/* Expander admin */
.streamlit-expanderHeader {
    border-radius: 15px;
}

/* Titre */
.big-title {
    font-size: 55px;
    font-weight: bold;
    text-align: center;
    background: linear-gradient(90deg, #60a5fa, #a78bfa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 20px;
}

/* Scrollbar */
::-webkit-scrollbar {
    width: 10px;
}

::-webkit-scrollbar-thumb {
    background: #374151;
    border-radius: 10px;
}

/* Tabs */
.stTabs [data-baseweb="tab"] {
    font-size: 18px;
    border-radius: 12px;
    padding: 10px 20px;
}

/* Success */
.stSuccess {
    border-radius: 15px;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #111827;
}

</style>
""", unsafe_allow_html=True)
