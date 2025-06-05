import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import datetime
import pandas as pd

# Initialisation Firebase (une seule fois)
if "firebase_initialized" not in st.session_state:
    cred = credentials.Certificate("firebase_key.json")
    if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)
    st.session_state.firebase_initialized = True

db = firestore.client()

# Catégories de dépenses
categories = ["Courses", "Goodies", "Activités", "Maison", "Autres"]

st.title("💰 Trésorerie de l'association")

# ---- SOLDE LYDIA ----
solde_doc = db.collection("Tresorerie").document("solde_total")
solde_data = solde_doc.get().to_dict()
solde = solde_data["montant"] if solde_data else 0.0

nouveau_solde = st.number_input("💼 Solde actuel Lydia (€)", value=solde, step=1.0)
if st.button("✅ Mettre à jour le solde Lydia"):
    solde_doc.set({"montant": nouveau_solde})
    st.success("✔️ Solde mis à jour !")

st.markdown("---")

# ---- DÉPENSES PAR ANNÉE ----
st.subheader("📆 Dépenses par année")

annees_possibles = list(range(2020, 2031))
annee_actuelle = datetime.date.today().year
annee = st.selectbox("Sélectionne une année :", annees_possibles, index=annees_possibles.index(annee_actuelle))
depenses_ref = db.collection("Tresorerie").document(f"depenses_{annee}")
depenses_data = depenses_ref.get().to_dict()
depenses = depenses_data.get("liste", []) if depenses_data else []

# Résumé par catégorie
if depenses:
    df = pd.DataFrame(depenses)
    df["date"] = pd.to_datetime(df["date"]).dt.strftime("%d/%m/%Y")

    total_par_categorie = df.groupby("categorie")["montant"].sum().to_dict()
    st.markdown("### 📊 Total par catégorie :")
    for cat in categories:
        montant = total_par_categorie.get(cat, 0.0)
        st.markdown(f"- **{cat}** : {montant:.2f} €")

    st.markdown("### 🧾 Dépenses détaillées :")
    st.dataframe(df[["date", "categorie", "description", "montant"]])
else:
    st.info("Aucune dépense enregistrée pour cette année.")

st.markdown("---")

# ---- FORMULAIRE D'AJOUT ----
st.subheader("➕ Ajouter une dépense")

with st.form("ajout_depense"):
    date_dep = st.date_input("📅 Date", value=datetime.date.today())
    description = st.text_input("📝 Description")
    montant = st.number_input("💶 Montant (€)", min_value=0.0, step=1.0)
    categorie = st.selectbox("📂 Catégorie :", categories)
    submit = st.form_submit_button("✅ Ajouter la dépense")

    if submit:
        nouvelle = {
            "date": date_dep.isoformat(),
            "description": description,
            "montant": montant,
            "categorie": categorie,
        }
        depenses.append(nouvelle)
        depenses_ref.set({"liste": depenses})
        st.success("✔️ Dépense ajoutée avec succès !")
