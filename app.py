# =========================================================
# ADMIN
# =========================================================

elif menu == "Espace Admin":

    st.title("🔐 Admin")

    # Session admin
    if "admin_ok" not in st.session_state:
        st.session_state.admin_ok = False

    # Mot de passe
    pwd = st.text_input(
        "Mot de passe :",
        type="password"
    )

    # Vérification
    if pwd == ADMIN_PASSWORD:
        st.session_state.admin_ok = True

    # Si connecté
    if st.session_state.admin_ok:

        st.success("Connexion réussie ✅")

        st.subheader("📂 Discussions sauvegardées")

        # Récupération messages
        msgs = db.collection('discussions') \
            .order_by('date', direction='ASCENDING') \
            .stream()

        groupes = {}

        for doc in msgs:

            d = doc.to_dict()

            nom = d.get('nom', 'Inconnu')

            if nom not in groupes:
                groupes[nom] = []

            groupes[nom].append(d)

        # Affichage en petits carrés
        cols = st.columns(3)

        noms = list(groupes.keys())

        for i, nom in enumerate(noms):

            with cols[i % 3]:

                with st.container(border=True):

                    st.markdown(f"### 👤 {nom}")

                    if st.button(
                        f"Voir la discussion",
                        key=f"btn_{nom}"
                    ):
                        st.session_state.selected_user = nom

        # Affichage conversation
        if "selected_user" in st.session_state:

            utilisateur = st.session_state.selected_user

            st.divider()

            st.subheader(f"💬 Conversation de {utilisateur}")

            for c in groupes[utilisateur]:

                st.markdown(f"**❓ Lui :** {c['texte']}")
                st.markdown(f"**🤖 Hartur :** {c['reponse']}")

                st.divider()
