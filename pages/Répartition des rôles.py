import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

# Initialisation Firebase
if "firebase_initialized" not in st.session_state:
    cred = credentials.Certificate("firebase_key.json")
    if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)
    st.session_state.firebase_initialized = True

db = firestore.client()

st.title("🧑‍🤝‍🧑 Répartition des rôles annuels")

membres = ["Aiham", "Arthur", "Pierre", "Guillaume", "François", "Nicolas", "Hendrik", "Olivier"]
departements = ["Courses", "Logement", "Goodies", "Activités"]

# ---- Sélection d'année pour modification ----
annee = st.selectbox("📅 Année à modifier", list(range(2020, 2031)), index=list(range(2020, 2031)).index(2025))

roles_ref = db.collection("roles_annuels").document(str(annee))
roles_doc = roles_ref.get()
roles_data = roles_doc.to_dict() if roles_doc.exists else {}

st.markdown("### ✏️ Répartition de l’année sélectionnée")

form = st.form("repartition_roles")
selections = {}

for dpt in departements:
    col1, col2 = form.columns(2)
    with col1:
        p1 = form.selectbox(f"{dpt} - 1er membre", membres, 
                            index=membres.index(roles_data[dpt][0]) if roles_data and dpt in roles_data else 0, 
                            key=f"{dpt}_1")
    with col2:
        p2 = form.selectbox(f"{dpt} - 2e membre", membres, 
                            index=membres.index(roles_data[dpt][1]) if roles_data and dpt in roles_data else 1, 
                            key=f"{dpt}_2")
    selections[dpt] = [p1, p2]

if form.form_submit_button("✅ Enregistrer cette répartition"):
    roles_ref.set(selections)
    st.success(f"✔️ Répartition {annee} enregistrée avec succès !")
    st.rerun()

# ---- 📜 Historique filtrable par année ----
st.markdown("---")
st.markdown("### 🔍 Historique par année")

# Récupérer toutes les années disponibles
all_docs = db.collection("roles_annuels").stream()
historique = {doc.id: doc.to_dict() for doc in all_docs}
annees_dispo = sorted(historique.keys(), reverse=True)

annee_sel = st.selectbox("🔎 Choisir une année à afficher :", annees_dispo)

if annee_sel:
    st.markdown(f"#### 📅 Répartition {annee_sel}")
    for dpt, noms in historique[annee_sel].items():
        st.markdown(f"- **{dpt}** : {noms[0]} & {noms[1]}")
    st.markdown("---")

# ---- 🗂️ Vue par personne ----
st.markdown("### 🗂️ Vue regroupée par personne")

vue_personnelle = {}
for an, data in historique.items():
    for dpt, noms in data.items():
        for nom in noms:
            if nom not in vue_personnelle:
                vue_personnelle[nom] = []
            vue_personnelle[nom].append((an, dpt))

# Tri par année
for nom in sorted(vue_personnelle.keys()):
    st.markdown(f"#### 👤 {nom}")
    for an, dpt in sorted(vue_personnelle[nom]):
        st.markdown(f"- {an} : **{dpt}**")
    st.markdown("---")
