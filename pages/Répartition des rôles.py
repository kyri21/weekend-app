import streamlit as st
from utils.firebase import db

st.set_page_config(page_title="Répartition des rôles", layout="centered")
st.title("🧑‍🤝‍🧑 Répartition des rôles annuels")

# Bouton pour charger le contenu
if st.button("🔄 Charger la répartition"):
    # Import après clic
    from datetime import datetime

    @st.cache_data(ttl=600)
    def load_repartitions():
        docs = db.collection("repartitions").stream()
        all_data = {}
        for doc in docs:
            all_data[doc.id] = doc.to_dict()
        return all_data

    participants = ["Aiham", "Arthur", "Pierre", "Guillaume", "François", "Nicolas", "Hendrik", "Olivier"]
    roles = ["Courses", "Logement", "Goodies", "Activités"]

    current_year = datetime.now().year
    year = st.selectbox("📆 Année", list(range(current_year, current_year - 11, -1)), index=0)

    st.subheader("✍️ Attribuer les rôles pour l'année")
    with st.form("repartition_form"):
        selections = {}
        for role in roles:
            col1, col2 = st.columns(2)
            selections[role] = (
                col1.selectbox(f"{role} – Membre 1", participants, key=f"{role}_1"),
                col2.selectbox(f"{role} – Membre 2", participants, key=f"{role}_2")
            )
        submitted = st.form_submit_button("✅ Valider la répartition")
        if submitted:
            db.collection("repartitions").document(str(year)).set(selections)
            st.success("Répartition enregistrée ✅")
            st.cache_data.clear()

    st.divider()
    st.subheader("📚 Historique des répartitions")
    repartitions = load_repartitions()

    filtre_mode = st.radio("🔍 Mode d'affichage", ["Par année", "Par personne"], horizontal=True)

    if filtre_mode == "Par année":
        selected_year = st.selectbox("Choisir une année :", sorted(repartitions.keys(), reverse=True))
        if selected_year in repartitions:
            st.write(f"### 📅 Répartition {selected_year}")
            for role, (p1, p2) in repartitions[selected_year].items():
                st.write(f"- **{role}** : {p1} & {p2}")

    else:  # Par personne
        selected_person = st.selectbox("👤 Choisir une personne :", participants)
        st.write(f"### 📌 Rôles de {selected_person}")
        found = False
        for y in sorted(repartitions.keys(), reverse=True):
            for role, (p1, p2) in repartitions[y].items():
                if selected_person in [p1, p2]:
                    st.write(f"📆 {y} : **{role}**")
                    found = True
        if not found:
            st.info("Aucun rôle trouvé pour cette personne.")
else:
    st.info("Cliquez sur 🔄 Charger la répartition pour démarrer.")
