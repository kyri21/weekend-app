import streamlit as st

st.title("🧾 Infos utiles")

def bloc(titre, contenu):
    st.markdown(f"### {titre}")
    st.code(contenu, language='')

bloc("🔐 Login Drive Leclerc", "https://leclercdrive.fr\nmail : kyriazis@outlook.fr\nmdp : Waf1991x8!")

bloc("🏦 RIB Sumeria", "IBAN : FR7617598000010000671413458\nBIC : LYDIFRP2XXX")

mot_de_passe = st.text_input("Quel est le surnom de Peplum d'Andrik ?", type="password")
if mot_de_passe.strip().lower() == "commode":
    bloc("💳 Carte de paiement", "4785 5430 2324 2672\nexp : 12/26\nCVV : 808\ntitulaire : Arthur KYRIAZIS")
else:
    st.warning("Entrez la bonne réponse pour afficher la carte.")
