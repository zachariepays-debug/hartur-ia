import streamlit as st

# --- INITIALISATION ---
if 'messages' not in st.session_state:
    st.session_state.messages = []

# --- NAVIGATION ---
# Remplacez cette partie par votre système de navigation habituel si nécessaire
page = st.sidebar.selectbox("Navigation", ["Chat", "Admin"])

if page == "Chat":
    # Titre standard de votre interface de discussion
    st.title("Conversation")
    
    # Gestion de l'entrée utilisateur
    if prompt := st.chat_input("Posez votre question..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Simulation de la réponse (à lier avec votre moteur d'IA)
        reponse_ia = f"Réponse à : {prompt}"
        st.session_state.messages.append({"role": "assistant", "content": reponse_ia})

        # Affichage des messages dans l'interface de chat
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

# --- SECTION ADMIN ---
elif page == "Admin":
    # Affichage conforme à votre capture d'écran
    st.markdown("## 🔐 Admin")
    
    if st.button("Se déconnecter"):
        st.write("Déconnexion en cours...")

    st.markdown("### Historique des conversations")
    st.write("---")

    # Affichage des logs pour l'administrateur
    if not st.session_state.messages:
        st.info("L'historique est actuellement vide.")
    else:
        for i, msg in enumerate(st.session_state.messages):
            if msg["role"] == "user":
                st.text(f"Utilisateur : {msg['content']}")
            else:
                st.text(f"Assistant : {msg['content']}")
                st.write("---")
