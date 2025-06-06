import streamlit as st
from datetime import datetime, timedelta
from utils.firebase import db

st.set_page_config(page_title="Disponibilités", layout="centered")
st.title("📅 Disponibilités des week-ends")

participants = ["Aiham", "Arthur", "Pierre", "Guillaume", "François", "Nicolas", "Hendrik", "Olivier"]

# Choix prénom et année
prenom = st.selectbox("👤 Choisis ton prénom", participants)
current_year = datetime.now().year
year = st.selectbox("📆 Année", list(range(current_year, current_year + 3)), index=0)

# Mois au choix
mois_dict = {
    "Janvier": 1, "Février": 2, "Mars": 3, "Avril": 4,
    "Mai": 5, "Juin": 6, "Juillet": 7, "Août": 8,
    "Septembre": 9, "Octobre": 10, "Novembre": 11, "Décembre": 12
}
mois = st.selectbox("🗓️ Mois", list(mois_dict.keys()))

# Génère tous les samedis-dimanches du mois choisi
def get_weekends(year, month):
    first_day = datetime(year, month, 1)
    weekends = []
    while first_day.month == month:
        if first_day.weekday() == 5:  # samedi
            sunday = first_day + timedelta(days=1)
            if sunday.month == month:
                weekends.append((first_day.strftime("%d/%m/%Y"), sunday.strftime("%d/%m/%Y")))
        first_day += timedelta(days=1)
    return weekends

@st.cache_data(ttl=300)
def get_dispos(prenom):
    doc_ref = db.collection("disponibilites").document(prenom)
    doc = doc_ref.get()
    return doc.to_dict() if doc.exists else {}

@st.cache_data(ttl=300)
def get_all_dispos():
    docs = db.collection("disponibilites").stream()
    return {doc.id: doc.to_dict() for doc in docs}

weekends = get_weekends(year, mois_dict[mois])
dispos = get_dispos(prenom)
dispos_set = set(dispos.get(str(year), []))

st.subheader("✅ Coche les week-ends où tu es disponible")
checked = {}
for samedi, dimanche in weekends:
    label = f"{samedi} - {dimanche}"
    checked[label] = st.checkbox(label, value=label in dispos_set)

if st.button("💾 Valider mes disponibilités"):
    selected = [k for k, v in checked.items() if v]
    db.collection("disponibilites").document(prenom).set({str(year): selected}, merge=True)
    st.success("Disponibilités enregistrées !")
    st.cache_data.clear()

# Affichage des dispos par week-end
st.divider()
st.subheader("📊 Disponibilités par week-end")

all_dispos = get_all_dispos()
weekend_counts = {f"{s} - {d}": 0 for s, d in weekends}
for p, data in all_dispos.items():
    for w in data.get(str(year), []):
        if w in weekend_counts:
            weekend_counts[w] += 1

for w, count in weekend_counts.items():
    st.write(f"**{w}** : {count}/8 disponibles")
