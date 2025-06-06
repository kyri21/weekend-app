import streamlit as st
import pandas as pd
from datetime import datetime
from utils.firebase import db

st.set_page_config(page_title="Trésorerie", layout="centered")
st.title("💰 Trésorerie de l'association")

categories = ["Courses", "Goodies", "Activités", "Maison", "Autres"]
current_year = datetime.now().year
annee = st.selectbox("📅 Année", list(range(current_year, current_year - 11, -1)), index=0)

@st.cache_data(ttl=600)
def get_depenses_par_annee(annee_arg):
    docs = db.collection("tresorerie").where("annee", "==", annee_arg).stream()
    data = []
    for doc in docs:
        d = doc.to_dict()
        data.append(d)
    return pd.DataFrame(data)

@st.cache_data(ttl=600)
def get_solde_actuel():
    doc = db.collection("tresorerie").document("solde").get()
    return doc.to_dict().get("montant", 0.0) if doc.exists else 0.0

# Affichage du solde
solde = get_solde_actuel()
st.metric("💼 Solde actuel", f"{solde:.2f} €")

# Formulaire pour ajouter une dépense
st.subheader("➕ Ajouter une dépense")
with st.form("ajout_depense"):
    datedep = st.date_input("📅 Date", value=datetime.today())
    montant = st.number_input("💶 Montant (€)", min_value=0.0, step=0.01)
    categorie = st.selectbox("📂 Catégorie", categories)
    description = st.text_input("📝 Description")
    submit = st.form_submit_button("✅ Ajouter")

    if submit and montant > 0 and description.strip():
        db.collection("tresorerie").add({
            "annee": annee,
            "date": datedep.strftime("%Y-%m-%d"),
            "montant": float(montant),
            "categorie": categorie,
            "description": description
        })
        # Optionnel : mettre à jour solde (si tu veux décrémenter)
        new_solde = solde - float(montant)
        db.collection("tresorerie").document("solde").set({"montant": new_solde})
        st.success("Dépense ajoutée ✅")
        st.cache_data.clear()

# Visualisation des dépenses
st.subheader("📊 Dépenses pour l'année " + str(annee))
df = get_depenses_par_annee(annee)

if df.empty:
    st.warning("Aucune dépense pour cette année.")
else:
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date", ascending=False)
    st.dataframe(df[["date", "montant", "categorie", "description"]], use_container_width=True)

    total_cat = df.groupby("categorie")["montant"].sum().reset_index()
    st.markdown("### Répartition par catégorie")
    st.dataframe(total_cat)
    st.markdown(f"**Total annuel :** {df['montant'].sum():.2f} €")
