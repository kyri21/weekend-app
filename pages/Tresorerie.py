import streamlit as st
import pandas as pd
from datetime import datetime
from utils.firebase import db

st.set_page_config(page_title="Trésorerie", layout="centered")
st.title("💰 Trésorerie de l'association")

categories = ["Courses", "Goodies", "Activités", "Maison", "Autres"]
annee_courante = datetime.now().year
annee = st.selectbox("📅 Année", list(range(annee_courante, annee_courante - 10, -1)), index=0)

@st.cache_data(ttl=600)
def get_depenses():
    docs = db.collection("tresorerie").stream()
    data = []
    for doc in docs:
        item = doc.to_dict()
        item["id"] = doc.id
        data.append(item)
    return pd.DataFrame(data)

def ajouter_depense(date, montant, categorie, description):
    db.collection("tresorerie").add({
        "date": date.strftime("%Y-%m-%d"),
        "montant": float(montant),
        "categorie": categorie,
        "description": description
    })
    st.success("✅ Dépense ajoutée avec succès")
    st.cache_data.clear()

st.subheader("➕ Ajouter une dépense")
with st.form("ajout_depense"):
    col1, col2 = st.columns(2)
    date = col1.date_input("Date", value=datetime.today())
    montant = col2.number_input("Montant (€)", min_value=0.0, step=0.01)
    categorie = st.selectbox("Catégorie", categories)
    description = st.text_input("Description")
    submit = st.form_submit_button("✅ Ajouter")
    if submit:
        ajouter_depense(date, montant, categorie, description)

df = get_depenses()
df["date"] = pd.to_datetime(df["date"])
df = df[df["date"].dt.year == annee]

if df.empty:
    st.warning("Aucune dépense enregistrée pour cette année.")
else:
    st.subheader(f"📊 Dépenses pour l'année {annee}")
    df = df.sort_values("date", ascending=False)
    st.dataframe(df[["date", "montant", "categorie", "description"]])

    total = df["montant"].sum()
    st.markdown(f"### 💵 Total des dépenses : **{total:.2f} €**")

    st.markdown("### Répartition par catégorie")
    repartition = df.groupby("categorie")["montant"].sum().reset_index()
    st.dataframe(repartition)
