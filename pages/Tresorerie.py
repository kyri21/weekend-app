import streamlit as st
from utils.firebase import db

st.set_page_config(page_title="Trésorerie", layout="centered")
st.title("💰 Trésorerie de l'association")

# 1️⃣ Premier bouton
if "trez_page_loaded" not in st.session_state:
    st.session_state["trez_page_loaded"] = False

def load_trez_page():
    st.session_state["trez_page_loaded"] = True

st.button("🔄 Charger les données de trésorerie", on_click=load_trez_page)

if not st.session_state["trez_page_loaded"]:
    st.info("Cliquez sur 🔄 Charger les données de trésorerie pour afficher le tableau.")
    st.stop()

# 2️⃣ Imports & logique après clic
import pandas as pd
from datetime import datetime

@st.cache_data(ttl=600)
def get_solde():
    doc = db.collection("tresorerie").document("solde").get()
    return doc.to_dict().get("montant", 0.0) if doc.exists else 0.0

@st.cache_data(ttl=600)
def get_depenses_par_annee(annee_arg):
    docs = db.collection("tresorerie").where("annee", "==", annee_arg).stream()
    data = []
    for doc in docs:
        d = doc.to_dict()
        data.append(d)
    if data:
        return pd.DataFrame(data)
    else:
        return pd.DataFrame(columns=["date", "montant", "categorie", "description", "annee"])

current_year = datetime.now().year
annee = st.selectbox("📅 Année", list(range(current_year, current_year - 11, -1)), index=0)

with st.spinner("Chargement du solde…"):
    solde = get_solde()
st.metric("💼 Solde actuel de l'association", f"{solde:.2f} €")

st.subheader("➕ Ajouter une dépense")
with st.form("ajout_depense"):
    datedep = st.date_input("📅 Date", value=datetime.today())
    montant = st.number_input("💶 Montant (€)", min_value=0.0, step=0.01)
    categorie = st.selectbox("📂 Catégorie", ["Courses", "Goodies", "Activités", "Maison", "Autres"])
    description = st.text_input("📝 Description")
    if st.form_submit_button("✅ Ajouter"):
        if montant > 0 and description.strip():
            db.collection("tresorerie").add({
                "annee": annee,
                "date": datedep.strftime("%Y-%m-%d"),
                "montant": float(montant),
                "categorie": categorie,
                "description": description
            })
            nouveau_solde = solde - float(montant)
            db.collection("tresorerie").document("solde").set({"montant": nouveau_solde})
            st.success("Dépense ajoutée et solde mis à jour")
            st.cache_data.clear()
        else:
            st.error("Veuillez entrer un montant > 0 et une description.")

st.subheader("📊 Dépenses pour l'année " + str(annee))
with st.spinner("Chargement des dépenses…"):
    df = get_depenses_par_annee(annee)

if df.empty:
    st.warning("Aucune dépense pour cette année.")
else:
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date", ascending=False)
    st.dataframe(df[["date", "montant", "categorie", "description"]], use_container_width=True)
    repartition = df.groupby("categorie")["montant"].sum().reset_index()
    st.markdown("### Répartition par catégorie")
    st.dataframe(repartition, use_container_width=True)
    total_annee = df["montant"].sum()
    st.markdown(f"**Total annuel : {total_annee:.2f} €**")
