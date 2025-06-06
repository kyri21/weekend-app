import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

# Firebase init
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_key.json")
    firebase_admin.initialize_app(cred)
db = firestore.client()

st.title("👥 Répartition des rôles")

participants = ["Aiham", "Arthur", "Pierre", "Guillaume", "François", "Nicolas", "Hendrik", "Olivier"]
departements = ["Courses", "Logement", "Goodies", "Activités"]

annee = st.selectbox("Année", list(range(2023, 2031)))

st.subheader("📝 Affecter 2 personnes par département")
repartition = {}

for dept in departements:
    st.markdown(f"**{dept}**")
    pers = st.multiselect(f"{dept} :", participants, key=dept, max_selections=2)
    if pers:
        repartition[dept] = pers

if st.button("✅ Enregistrer"):
    db.collection("repartition").document(str(annee)).set(repartition)
    st.success("Répartition enregistrée !")

# Vue archive
st.subheader("📚 Archive par année")
annee_archive = st.selectbox("Choisir une année", list(range(2023, 2031)), key="archive")
doc = db.collection("repartition").document(str(annee_archive)).get()
if doc.exists:
    data = doc.to_dict()
    for dept, noms in data.items():
        st.markdown(f"- **{dept}** : {', '.join(noms)}")

# Vue par personne
st.subheader("🔍 Historique par personne")
nom_cherche = st.selectbox("Choisir une personne", participants, key="nom_archive")
for a in range(2023, 2031):
    doc = db.collection("repartition").document(str(a)).get()
    if doc.exists:
        data = doc.to_dict()
        for dept, noms in data.items():
            if nom_cherche in noms:
                st.markdown(f"- **{a}** : {dept}")
