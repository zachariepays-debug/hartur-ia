# =========================
# 📊 DISPLAY PRO (PAR NOM)
# =========================
if not groupes:
    st.info("Aucune conversation")
else:
    st.success(f"{len(groupes)} utilisateur(s) trouvé(s)")

    for nom, convs in sorted(groupes.items(), key=lambda x: len(x[1]), reverse=True):

        # tri interne par date si dispo
        convs = sorted(convs, key=lambda x: x.get("date", 0))

        dernier = convs[-1] if convs else None

        with st.expander(f"👤 {nom} — {len(convs)} messages"):

            # aperçu dernier message
            if dernier:
                st.caption(f"💬 Dernier message : {dernier.get('texte','')}")

            st.divider()

            # affichage conversation complète
            for c in convs:

                user_msg = c.get("texte", "")
                bot_msg = c.get("reponse", "")

                if user_msg:
                    st.markdown(
                        f"<div style='background:#1f2937;padding:10px;border-radius:10px;margin-bottom:5px'>"
                        f"🧑‍💬 {user_msg}</div>",
                        unsafe_allow_html=True
                    )

                if bot_msg:
                    st.markdown(
                        f"<div style='background:#0f172a;padding:10px;border-radius:10px;margin-bottom:15px'>"
                        f"🤖 {bot_msg}</div>",
                        unsafe_allow_html=True
                    )

            st.divider()
