import streamlit as st

# --- INITIALISATION DE L'ÉTAT (A mettre au début du script) ---
# Initialise l'historique s'il n'existe pas encore dans la session
if 'messages' not in st.session_state:
    st.session_state.messages = []

# --- INTERFACE UTILISATEUR (Simulation de chat) ---
def user_interface():
    st.title("Mon Application Junior")
    
    # Zone de saisie pour l'utilisateur
    if prompt := st.chat_input("Posez votre question ici..."):
        # Ajout du message utilisateur à l'historique
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Simulation d'une réponse de l'assistant
        response = f"Echo : {prompt}" 
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        # Affichage immédiat
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

# --- SECTION ADMIN MODIFIÉE ---
def admin_interface():
    st.markdown("## 🔐 Coin Admin")
    st.write("Bienvenue dans l'espace de gestion.")
    
    st.markdown("### 📜 Historique des conversations")
    st.write("---")

    if not st.session_state.messages:
        st.info("Aucune conversation enregistrée pour le moment.")
    else:
        # Affichage structuré de l'historique
        for i, msg in enumerate(st.session_state.messages):
            role_label = "👤 Utilisateur" if msg["role"] == "user" else "🤖 Assistant"
            # Utilisation de expanders ou de texte formaté pour la clarté
            with st.expander(f"Message {i+1} - {role_label}"):
                st.write(msg["content"])
        
        # Option pour nettoyer les logs
        if st.button("Effacer les historiques"):
            st.session_state.messages = []
            st.rerun()

# --- LOGIQUE DE NAVIGATION (MENU) ---
def main():
    menu = ["Accueil", "Admin"]
    choice = st.sidebar.selectbox("Navigation", menu)

    if choice == "Accueil":
        user_interface()
    elif choice == "Admin":
        # Ici, vous pouvez ajouter une vérification de mot de passe si besoin
        admin_interface()

if __name__ == "__main__":
    main()
