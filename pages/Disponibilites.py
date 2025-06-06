import streamlit as st
import calendar
from datetime import datetime, timedelta
from utils.firebase import db

st.set_page_config(page_title="Disponibilités", layout="centered")
st.title("📅 Disponibilités des week-ends")

participants = ["Aiham", "Arthur", "Pierre", "Guillaume", "François", "Nicolas", "Hendrik", "Olivier"]

prenom = st.selectbox("👤 Qui êtes-vous ?", participants)
current_year = datetime.now().year
year = st.selectbox("📆 Année", list(range(current_year, current_year + 3)), index=0)
month = st.selectbox(
    "🗓️ Mois",
    ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
     "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"],
    index=datetime.now().month - 1
)
mois_dict = {
    "Janvier": 1, "Février": 2, "Mars": 3, "Avril": 4,
    "Mai": 5, "Juin": 6, "Juillet": 7, "Août": 8,
    "Septembre": 9, "Octobre": 10, "Novembre": 11, "Décembre": 12
}

@st.cache_data(ttl=3600)
def get_weekends(y, m):
    weekends = []
    date = datetime(y, m, 1)
    while date.month == m:
        if date.weekday() == 5:  # Samedi
            sunday = date + timedelta(days=1)
            if sunday.month == m:
                weekends.append((date.strftime("%d/%m/%Y"), sunday.strftime("%d/%m/%Y")))
        date += timedelta(days=1)
    return weekends

@st.cache_data(ttl=600)
def get_user_dispos(prenom, annee_arg, mois_arg):
    # On stocke par document `<prenom>` → collection `year-month`
    doc_ref = db.collection("disponibilites").document(prenom)
    doc = doc_ref.get()
    if not doc.exists:
        return []
    data = doc.to_dict()
    key = f"{annee_arg}-{mois_arg}"
    return data.get(key, [])

# **Lazy load** : on ne lit que si l’utilisateur clique
if st.button("🔄 Charger mes disponibilités"):
    dispos_set = set(get_user_dispos(prenom, year, mois_dict[month]))
else:
    dispos_set = set()

weekends = get_weekends(year, mois_dict[month])
st.subheader("✅ Cochez les week-ends où vous êtes disponible")

checked = {}
for samedi, dimanche in weekends:
    label = f"{samedi} - {dimanche}"
    is_checked = label in dispos_set
    checked[label] = st.checkbox(label, value=is_checked, key=label)

if st.button("💾 Valider mes disponibilités"):
    # On stocke dans un seul document par utilisateur
    doc_ref = db.collection("disponibilites").document(prenom)
    doc = doc_ref.get()
    old = doc.to_dict() if doc.exists else {}
    key = f"{year}-{mois_dict[month]}"
    selected = [k for k, v in checked.items() if v]
    old[key] = selected
    doc_ref.set(old)
    st.success("Disponibilités enregistrées ✅")
    st.cache_data.clear()

# Affichage agrégé (facultatif)
st.divider()
st.subheader("📊 Statistiques des disponibilités pour ce mois")
if dispos_set:
    # Compte combien de personnes par week-end
    @st.cache_data(ttl=600)
    def get_all_dispos(annee_arg, mois_arg):
        docs = db.collection("disponibilites").stream()
        counts = {}
        key = f"{annee_arg}-{mois_arg}"
        for doc in docs:
            data = doc.to_dict().get(key, [])
            for w in data:
                counts[w] = counts.get(w, 0) + 1
        return counts

    counts = get_all_dispos(year, mois_dict[month])
    for samedi, dimanche in weekends:
        label = f"{samedi} - {dimanche}"
        c = counts.get(label, 0)
        st.write(f"**{label}** : {c}/{len(participants)} disponibles")
