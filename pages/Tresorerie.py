import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# Init Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_key.json")
    firebase_admin.initialize_app(cred)
db = firestore.client()

st.title("💰 Trésorerie")

# Affichage du solde
solde_doc = db.collection("tresorerie").document("solde").get()
solde = solde_doc.to_dict().get("valeur", 0.0) if solde_doc.exists else 0.0
st.metric("💼 Solde actuel de l'association", f"{solde:.2f} €")

# Ajout de dépense
st.subheader("➕ Ajouter une dépense")
col1, col2 = st.columns(2)
with col1:
    titre = st.text_input("Titre")
    montant = st.number_input("Montant", min_value=0.01, step=0.01)
with col2:
    categorie = st.selectbox("Catégorie", ["Courses", "Goodies", "Activités", "Maison", "Autres"])
    annee = st.selectbox("Année", list(range(datetime.now().year, datetime.now().year - 10, -1)))

if st.button("✅ Ajouter cette dépense") and titre:
    db.collection("tresorerie").document("depenses").collection(str(annee)).add({
        "titre": titre,
        "montant": montant,
        "categorie": categorie,
        "date": datetime.now()
    })
    solde -= montant
    db.collection("tresorerie").document("solde").set({"valeur": solde})
    st.success("Dépense ajoutée !")

# Affichage dépenses
st.subheader("📊 Historique des dépenses")
for y in sorted([d.id for d in db.collection("tresorerie").document("depenses").collections()], reverse=True):
    st.markdown(f"### 📅 {y}")
    docs = db.collection("tresorerie").document("depenses").collection(y).stream()
    data = [{"titre": d.get("titre"), "montant": d.get("montant"), "categorie": d.get("categorie")} for d in docs]
    if data:
        st.table(data)
