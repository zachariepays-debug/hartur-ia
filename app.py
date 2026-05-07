elif menu == "Espace Admin":
    st.title("🔐 Admin Panel")

    # --- AUTH ---
    if "is_admin" not in st.session_state:
        st.session_state.is_admin = False

    if not st.session_state.is_admin:
        pwd = st.text_input("Mot de passe :", type="password")

        if st.button("Connexion"):
            if pwd == "babar":
                st.session_state.is_admin = True
                st.success("Connecté ✔")
                st.rerun()
            else:
                st.error("Mot de passe incorrect ❌")

        st.stop()


    # =========================
    # 🔎 SEARCH GLOBAL
    # =========================
    search = st.text_input("🔎 Rechercher utilisateur ou message")

    # =========================
    # 📥 LOAD FIREBASE
    # =========================
    docs = db.collection('discussions') \
        .order_by('date') \
        .stream()

    groupes = {}

    for doc in docs:
        d = doc.to_dict()
        if not d:
            continue

        nom = d.get("nom", "Inconnu")

        # 🔎 filtre search
        if search:
            if search.lower() not in nom.lower() \
            and search.lower() not in d.get("texte","").lower() \
            and search.lower() not in d.get("reponse","").lower():
                continue

        if nom not in groupes:
            groupes[nom] = []

        groupes[nom].append(d)


    # =========================
    # 📊 AFFICHAGE GROUPÉ PAR USER
    # =========================
    if not groupes:
        st.info("Aucune conversation trouvée")
    else:

        # 🔥 tri par activité (les plus actifs en haut)
        for nom, convs in sorted(groupes.items(), key=lambda x: len(x[1]), reverse=True):

            with st.expander(f"👤 {nom} ({len(convs)} messages)"):

                for c in convs:
                    st.markdown(f"❓ **User :** {c.get('texte','')}")
                    st.markdown(f"🤖 **Hartur :** {c.get('reponse','')}")
                    st.divider()

                # 🗑 SUPPRESSION USER COMPLET
                if st.button(f"🗑 Supprimer toute la conversation de {nom}", key=f"del_{nom}"):
                    docs_to_delete = db.collection('discussions') \
                        .where('nom', '==', nom) \
                        .stream()

                    for d in docs_to_delete:
                        db.collection('discussions').document(d.id).delete()

                    st.success("Conversation supprimée ✔")
                    st.rerun()
