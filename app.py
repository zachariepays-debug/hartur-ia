import streamlit as st

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Arthur - Admin", page_icon="🔐")

# --- INITIALISATION DE L'ÉTAT DE LA SESSION ---
if 'conversation_history' not in st.session_state:
    st.session_state['conversation_history'] = [
        {"role": "user", "content": "Bonjour Arthur."},
        {"role": "assistant", "content": "Bonjour ! Comment puis-je t'aider ?"},
    ]

if 'is_admin' not in st.session_state:
    st.session_state['is_admin'] = False 

# --- INTERFACE ADMIN ---
if st.session_state['is_admin']:
    
    # En-tête conforme à ton image
    st.markdown("## 🔐 Admin")
    
    if st.button("Se déconnecter"):
        st.session_state['is_admin'] = False
        st.rerun()

    st.markdown("### Historique des conversations")
    st.write("---")

    # Affichage de l'historique
    for message in st.session_state['conversation_history']:
        if message["role"] == "user":
            with st.chat_message("user"):
                st.write(message["content"])
        else:
            with st.chat_message("assistant"):
                st.write(message["content"])

    st.write("---")
    if st.button("Effacer l'historique"):
        st.session_state['conversation_history'] = []
        st.rerun()

# --- INTERFACE ARTHUR (Connexion) ---
else:
    st.title("Arthur") # Titre remis sur Arthur
    
    admin_password = st.text_input("Mot de passe Admin", type="password")
    if st.button("Se connecter"):
        if admin_password == "admin123": 
            st.session_state['is_admin'] = True
            st.success("Connexion réussie !")
            st.rerun()
        else:
            st.error("Mot de passe incorrect.")
