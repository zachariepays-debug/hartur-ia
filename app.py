# ======================================================
# 👤 COMPTES UTILISATEURS
# ======================================================

# SESSION
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = None

if "show_popup" not in st.session_state:
    st.session_state.show_popup = True


# ======================================================
# 📂 DOSSIERS
# ======================================================
os.makedirs("accounts", exist_ok=True)
os.makedirs("data", exist_ok=True)


# ======================================================
# 💾 CREATION COMPTE
# ======================================================
def create_account(username, password):

    username = username.lower().strip()

    # 🔥 empêche doublons
    if os.path.exists(f"accounts/{username}.txt"):
        return False

    with open(f"accounts/{username}.txt", "w", encoding="utf-8") as f:

        f.write(f"IDENTIFIANT:{username}\n")
        f.write(f"MOTDEPASSE:{password}\n")
        f.write(f"DATE:{datetime.utcnow()}\n")

    return True


# ======================================================
# 🔑 CONNEXION
# ======================================================
def login_account(username, password):

    username = username.lower().strip()

    try:

        with open(
            f"accounts/{username}.txt",
            "r",
            encoding="utf-8"
        ) as f:

            content = f.read()

            saved_password = content.split(
                "MOTDEPASSE:"
            )[1].split("\n")[0]

            if saved_password == password:
                return True

    except:
        pass

    return False


# ======================================================
# 💬 FENETRE DESCRIPTION
# ======================================================
if st.session_state.show_popup:

    with st.container():

        st.info("""
# 🤖 Bienvenue sur Hartur IA

### Fonctionnalités :
• IA personnalisable  
• Mémoire des discussions  
• Historique automatique  
• Upload d'images  
• Modes et personnalités  

👉 Crée un compte ou connecte-toi 😄
""")

        if st.button("❌ Fermer"):

            st.session_state.show_popup = False
            st.rerun()


# ======================================================
# 👤 CONNEXION / CREATION
# ======================================================
if not st.session_state.logged_in:

    col1, col2 = st.columns(2)

    # ==================================================
    # 🔑 CONNEXION
    # ==================================================
    with col1:

        st.subheader("🔑 Se connecter")

        login_user = st.text_input(
            "Identifiant",
            key="login_user"
        )

        login_pass = st.text_input(
            "Mot de passe",
            type="password",
            key="login_pass"
        )

        if st.button("Connexion"):

            if login_account(login_user, login_pass):

                st.session_state.logged_in = True
                st.session_state.username = login_user

                # 🔥 recharge historique
                st.session_state.messages = load_old_messages(
                    login_user
                )

                st.success("Connexion réussie 😄")

                st.rerun()

            else:
                st.error("Identifiant ou mot de passe incorrect")


    # ==================================================
    # 🆕 CREER COMPTE
    # ==================================================
    with col2:

        st.subheader("🆕 Créer un compte")

        new_user = st.text_input(
            "Choisir un identifiant",
            key="new_user"
        )

        new_pass = st.text_input(
            "Choisir un mot de passe",
            type="password",
            key="new_pass"
        )

        if st.button("Créer le compte"):

            if len(new_user.strip()) < 3:

                st.error("Identifiant trop court")

            elif len(new_pass.strip()) < 3:

                st.error("Mot de passe trop court")

            else:

                created = create_account(
                    new_user,
                    new_pass
                )

                if created:

                    st.success("Compte créé 😄")

                else:

                    st.error(
                        "Cet identifiant existe déjà ❌"
                    )

    st.stop()


# ======================================================
# 👤 USER CONNECTE
# ======================================================
st.sidebar.success(
    f"👤 Connecté : {st.session_state.username}"
)

if st.sidebar.button("🚪 Déconnexion"):

    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.messages = []

    st.rerun()


# ======================================================
# 💾 SAVE MODIF
# ======================================================
# ⚠️ remplace :
# st.session_state.nom
#
# PAR :
# st.session_state.username

# Exemple :

# save_message(
#     st.session_state.username,
#     st.session_state.session_id,
#     prompt,
#     reponse
# )


# ======================================================
# 🔐 ADMIN AJOUT COMPTES
# ======================================================
# 👉 AJOUTE ÇA dans ton onglet ADMIN

st.subheader("👤 Comptes créés")

os.makedirs("accounts", exist_ok=True)

account_files = os.listdir("accounts")

if not account_files:

    st.info("Aucun compte.")

else:

    for file in account_files:

        if file.endswith(".txt"):

            username = file.replace(".txt", "")

            with st.expander(f"👤 {username}"):

                with open(
                    f"accounts/{file}",
                    "r",
                    encoding="utf-8"
                ) as f:

                    st.text(f.read())
