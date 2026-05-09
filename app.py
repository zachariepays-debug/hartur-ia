import streamlit as st
import pandas as pd
import os

# --- CONFIG ---
st.set_page_config(page_title="Hartur IA", layout="centered")
FICHIER = "comptes.csv"

# --- INTERFACE ---
st.title("🤖 Hartur IA")

if "user" not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    # 1. CONNEXION (En haut de la page)
    st.header("🔑 Connexion")
    p_co = st.text_input("Pseudo", key="p_co")
    m_co = st.text_input("Mot de passe", type="password", key="m_co")
    
    if st.button("Se connecter"):
        df = pd.read_csv(FICHIER)
        # On vérifie si le pseudo et le mot de passe correspondent
        if not df.empty and ((df['pseudo'] == p_co) & (df['password'].astype(str) == str(m_co))).any():
            st.session_state.user = p_co
            st.rerun()
        else:
            st.error("Identifiants incorrects.")

    st.divider()

    # 2. INSCRIPTION (En bas de la page, comme tu voulais)
    st.header("📝 Inscription")
    p_ins = st.text_input("Choisis un pseudo", key="p_ins")
    m_ins = st.text_input("Choisis un mot de passe", type="password", key="m_ins")
    
    if st.button("Créer mon compte"):
        if p_ins and m_ins:
            df = pd.read_csv(FICHIER)
            if p_ins in df['pseudo'].values:
                st.warning("Ce pseudo est déjà pris.")
            else:
                # On ajoute la nouvelle ligne
                nouveau = pd.DataFrame([{"pseudo": p_ins, "password": str(m_ins)}])
                df = pd.concat([df, nouveau], ignore_index=True)
                # On sauvegarde dans le fichier comptes.csv
                df.to_csv(FICHIER, index=False)
                st.success("Compte créé ! Tu peux te connecter en haut.")
        else:
            st.error("Veuillez remplir les deux champs.")
else:
    st.success(f"Bienvenue {st.session_state.user} !")
    if st.button("Se déconnecter"):
        st.session_state.user = None
        st.rerun()
