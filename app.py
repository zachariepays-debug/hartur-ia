import streamlit as st

# --- INITIALISATION DE L'HISTORIQUE ---
if 'messages' not in st.session_state:
    st.session_state.messages = []

# --- LOGIQUE DE NAVIGATION ---
# Tu peux adapter cette partie selon comment ton menu est construit (sidebar ou autre)
menu = ["Interface Chat", "Admin"]
page = st.sidebar.selectbox("Menu", menu)

if page == "Interface Chat":
    st.title("Conversation") # Ou ton titre habituel
    
    # Zone de chat
    if prompt := st.chat_input("Votre message..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Ici ton code pour la réponse de l'IA
        response = "Ceci est une réponse automatique." 
        st.session_state.messages.append({"role": "assistant", "content": response})

# --- SECTION ADMIN (CORRIGÉE) ---
elif page == "Admin":
    # Titre et icône exactement comme sur ta capture d'écran
    st.markdown("## 🔐 Admin")
    
    if st.button("Se déconnecter"):
        # Logique de déconnexion
        st.info("Déconnexion...")

    st.markdown("### Historique des conversations")
    st.write("---")

    # Affichage des messages stockés
    if not st.session_state.messages:
        st.write("Aucun message dans l'historique.")
    else:
        for i, msg in enumerate(st.session_state.messages):
            if msg["role"] == "user":
                with st.chat_message("user"):
                    st.write(f"**Utilisateur:** {msg['content']}")
            else:
                with st.chat_message("assistant"):
                    st.write(f"**IA:** {msg['content']}")
                    
    # Petit ajout pratique : bouton pour vider les logs
    if st.session_state.messages:
        if st.button("Vider l'historique"):
            st.session_state.messages = []
            st.rerun()
