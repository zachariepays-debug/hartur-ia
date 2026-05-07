# =========================
# 🔐 ADMIN PANEL (CARDS UI)
# =========================
else:

    st.title("🔐 Admin Panel")

    if "admin" not in st.session_state:
        st.session_state.admin = False

    if not st.session_state.admin:

        pwd = st.text_input("Mot de passe", type="password")

        if st.button("Connexion"):
            if pwd == st.secrets.get("ADMIN_PASS", "babar"):
                st.session_state.admin = True
                st.rerun()
            else:
                st.error("Mot de passe incorrect")

        st.stop()


    # =========================
    # LOAD DATA
    # =========================
    docs = db.collection("discussions").stream()

    users = {}

    for d in docs:
        x = d.to_dict()
        if not x:
            continue

        nom = x.get("nom", "Inconnu")

        users.setdefault(nom, []).append(x)


    # =========================
    # STATE SELECTION
    # =========================
    if "selected_user" not in st.session_state:
        st.session_state.selected_user = None


    # =========================
    # VIEW 1 : CARDS
    # =========================
    if st.session_state.selected_user is None:

        st.subheader("👤 Utilisateurs")

        cols = st.columns(3)

        for i, (nom, conv) in enumerate(users.items()):

            with cols[i % 3]:

                if st.button(f"📦 {nom}\n({len(conv)} msgs)"):

                    st.session_state.selected_user = nom
                    st.rerun()


    # =========================
    # VIEW 2 : CHAT
    # =========================
    else:

        nom = st.session_state.selected_user

        st.subheader(f"💬 Conversation : {nom}")

        if st.button("⬅ Retour"):
            st.session_state.selected_user = None
            st.rerun()

        conv = users.get(nom, [])

        for c in conv:

            st.markdown(f"👤 **User :** {c.get('texte','')}")
            st.markdown(f"🤖 **IA :** {c.get('reponse','')}")
            st.divider()
