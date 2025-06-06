import streamlit as st

st.set_page_config(page_title="Infos utiles", layout="centered")
st.title("🧾 Infos Utiles")

st.subheader("🛒 Leclerc Drive")
st.code("Identifiant : kyriazis@outlook.fr\nMot de passe : Waf1991x8!", language="text")

st.subheader("🏦 RIB Association SUMERIA")
st.code("IBAN : FR7617598000010000671413458\nBIC : LYDIFRP2XXX", language="text")

# ✅ Protection par question secrète
if "carte_visible" not in st.session_state:
    st.session_state["carte_visible"] = False

if not st.session_state["carte_visible"]:
    with st.expander("🔐 Afficher les coordonnées de la carte de paiement"):
        reponse = st.text_input("❓ Quel est le surnom de Peplum d'Andrik ?", type="password")
        if reponse.lower().strip() == "commode":
            st.session_state["carte_visible"] = True
        elif reponse != "":
            st.error("❌ Mauvaise réponse")

if st.session_state["carte_visible"]:
    st.subheader("💳 Carte de paiement")
    st.code("""Numéro : 4785 5430 2324 2672
Expiration : 12/26
CVV : 808
Titulaire : Arthur KYRIAZIS""", language="text")
