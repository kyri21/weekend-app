import streamlit as st
from utils.firebase import db

st.set_page_config(page_title="Disponibilités", layout="centered")
st.title("📅 Disponibilités des week-ends")

# Flag lazy-loading
if "dispo_loaded" not in st.session_state:
    st.session_state["dispo_loaded"] = False

def load_dispos():
    st.session_state["dispo_loaded"] = True

st.button("🔄 Charger mes disponibilités", on_click=load_dispos)

if not st.session_state["dispo_loaded"]:
    st.info("Clique sur 🔄 Charger mes disponibilités pour démarrer.")
    st.stop()

# ――― Imports et logique à exécuter *après* avoir cliqué ――― #
import calendar
from datetime import datetime, timedelta

participants = ["Aiham", "Arthur", "Pierre", "Guillaume", "François", "Nicolas", "Hendrik", "Olivier"]
prenom = st.selectbox("👤 Qui es-tu ?", participants)

current_year = datetime.now().year
year = st.selectbox("📆 Année", list(range(current_year, current_year + 3)), index=0)

mois_dict = {
    "Janvier": 1, "Février": 2, "Mars": 3, "Avril": 4,
    "Mai": 5, "Juin": 6, "Juillet": 7, "Août": 8,
    "Septembre": 9, "Octobre": 10, "Novembre": 11, "Décembre": 12
}
month_name = st.selectbox("🗓️ Mois", list(mois_dict.keys()), index=datetime.now().month - 1)
month = mois_dict[month_name]

@st.cache_data(ttl=3600)
def get_weekends(y, m):
    """
    Renvoie la liste des week-ends (samedi, dimanche) pour l’année y et le mois m.
    """
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
def get_user_dispos(prenom_arg, year_arg, month_arg):
    """
    Va lire dans Firestore le document 'disponibilites/<prenom_arg>',
    puis renvoyer la liste des week-ends déjà cochés pour clef 'year-month'.
    """
    doc_ref = db.collection("disponibilites").document(prenom_arg)
    doc = doc_ref.get()
    if not doc.exists:
        return []
    data = doc.to_dict()
    key = f"{year_arg}-{month_arg}"
    return data.get(key, [])

# Pendant qu’on récupère les dispos, on affiche un spinner
with st.spinner("Chargement de tes disponibilités…"):
    dispo_set = set(get_user_dispos(prenom, year, month))

# Pendant qu’on calcule les week-ends, on affiche un spinner
with st.spinner("Génération du calendrier…"):
    weekends = get_weekends(year, month)

st.subheader("✅ Coche les week-ends où tu es disponible")
checked = {}
for samedi, dimanche in weekends:
    label = f"{samedi} – {dimanche}"
    is_checked = label in dispo_set
    checked[label] = st.checkbox(label, value=is_checked, key=label)

if st.button("💾 Valider mes disponibilités"):
    doc_ref = db.collection("disponibilites").document(prenom)
    doc = doc_ref.get()
    old_data = doc.to_dict() if doc.exists else {}
    key = f"{year}-{month}"
    selected = [w for w, v in checked.items() if v]
    old_data[key] = selected
    doc_ref.set(old_data)
    st.success("Disponibilités enregistrées ✅")
    st.cache_data.clear()

# Affichage du nombre de personnes dispo par week-end
@st.cache_data(ttl=600)
def get_all_dispos_counts(year_arg, month_arg):
    key = f"{year_arg}-{month_arg}"
    docs = db.collection("disponibilites").stream()
    counts = {}
    for d in docs:
        data = d.to_dict().get(key, [])
        for w in data:
            counts[w] = counts.get(w, 0) + 1
    return counts

with st.spinner("Calcul des statistiques…"):
    counts = get_all_dispos_counts(year, month)

st.divider()
st.subheader("📊 Combien sont disponibles pour chaque week-end ?")
for samedi, dimanche in weekends:
    label = f"{samedi} – {dimanche}"
    c = counts.get(label, 0)
    st.write(f"**{label}** : {c}/{len(participants)} disponibles")
