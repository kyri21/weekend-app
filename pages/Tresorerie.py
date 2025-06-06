import streamlit as st
from datetime import datetime
from utils.firebase import db

st.set_page_config(page_title="Trésorerie", layout="wide")
st.title("💰 Trésorerie")

# Solde actuel (modifiable)
solde = st.number_input("💳 Solde actuel de l'association (€)", value=735.75, step=0.01, format="%.2f")

# Ajouter une dépense
st.subheader("➕ Ajouter une dépense")

categories = ["Courses", "Goodies", "Activités", Maison := "Maison", "Autres"]
annee = st.selectbox("Année", list(range(2023, datetime.now().year + 2)), index=1)
categorie = st.selectbox("Catégorie", categories)
montant = st.number_input("Montant (€)", min_value=0.0, step=0.50, format="%.2f")
description = st.text_input("Description")
if st.button("💾 Enregistrer la dépense"):
    db.collection("depenses").add({
        "annee": annee,
        "categorie": categorie,
        "montant": montant,
        "description": description,
        "timestamp": datetime.now()
    })
    st.success("✅ Dépense ajoutée")
    st.cache_data.clear()

# Récupérer les dépenses groupées par année
@st.cache_data(ttl=600)
def get_depenses_par_annee():
    docs = db.collection("depenses").stream()
    data = {}
    for doc in docs:
        d = doc.to_dict()
        annee = d["annee"]
        if annee not in data:
            data[annee] = []
        data[annee].append(d)
    return data

st.subheader("📊 Dépenses par année")
depenses_data = get_depenses_par_annee()

for annee, depenses in sorted(depenses_data.items()):
    st.markdown(f"### 📅 {annee}")
    categories_totales = {}
    for dep in depenses:
        cat = dep["categorie"]
        categories_totales[cat] = categories_totales.get(cat, 0) + dep["montant"]

    col1, col2 = st.columns([2, 1])
    with col1:
        for cat, total in categories_totales.items():
            st.markdown(f"- **{cat}** : {total:.2f} €")
    with col2:
        st.write("")

    with st.expander("📋 Voir les détails"):
        for dep in depenses:
            st.markdown(f"- {dep['description']} ({dep['categorie']}) : {dep['montant']} €")
