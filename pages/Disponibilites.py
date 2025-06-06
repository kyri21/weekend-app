# pages/Disponibilites.py

import streamlit as st
from utils.firebase import db

st.set_page_config(page_title="Disponibilités", layout="centered")
st.title("📅 Disponibilités des week-ends")

# ----
/// 1️⃣ PREMIER BOUTON POUR AFFICHER LES SÉLECTEURS ///

if "dispo_page_loaded" not in st.session_state:
    st.session_state["dispo_page_loaded"] = False

def load_dispo_page():
    st.session_state["dispo_page_loaded"] = True

st.button("🔄 Charger mes disponibilités", on_click=load_dispo_page)

if not st.session_state["dispo_page_loaded"]:
    st.info("Cliquez sur 🔄 Charger mes disponibilités pour afficher le formulaire.")
    st.stop()  # Arrête toute exécution tant qu’on n’a pas cliqué.

# À partir d’ici, dispo_page_loaded == True => on affiche le formulaire de sélection

participants = ["Aiham", "Arthur", "Pierre", "Guillaume", "François", "Nicolas", "Hendrik", "Olivier"]
prenom = st.selectbox("👤 Qui es-tu ?", participants)

# Import des modules seulement ici, après le clic
import calendar
from datetime import datetime, timedelta

current_year = datetime.now().year
year = st.selectbox("📆 Année", list(range(current_year, current_year + 3)), index=0)

mois_dict = {
    "Janvier": 1, "Février": 2, "Mars": 3, "Avril": 4,
    "Mai": 5, "Juin": 6, "Juillet": 7, "Août": 8,
    "Septembre": 9, "Octobre": 10, "Novembre": 11, "Décembre": 12
}
month_name = st.selectbox("🗓️ Mois", list(mois_dict.keys()), index=datetime.now().month - 1)
month = mois_dict[month_name]

# ----
/// 2️⃣ SECOND BOUTON POUR RÉELLEMENT CHERCHER EN BASE ///

if "dispo_data_loaded" not in st.session_state:
    st.session_state["dispo_data_loaded"] = False

def load_dispo_data():
    st.session_state["dispo_data_loaded"] = True

st.button("💠 Afficher mes disponibilités", on_click=load_dispo_data)

if not st.session_state["dispo_data_loaded"]:
    st.info("Une fois ton prénom, année et mois choisis, clique sur 💠 Afficher mes disponibilités.")
    st.stop()  # Arrête l’exécution tant qu’on n’a pas cliqué sur le second bouton.

# À partir d’ici, dispo_data_loaded == True => on appelle Firestore et génère le calendrier

# 1) Génération des week-ends (mise en cache 1 h)
@st.cache_data(ttl=3600)
def get_weekends(annee_arg, mois_arg):
    weekends = []
    date = datetime(annee_arg, mois_arg, 1)
    while date.month == mois_arg:
        if date.weekday() == 5:  # Samedi
            sunday = date + timedelta(days=1)
            if sunday.month == mois_arg:
                weekends.append((date.strftime("%d/%m/%Y"), sunday.strftime("%d/%m/%Y")))
        date += timedelta(days=1)
    return weekends

# 2) Lecture des dispos existantes pour cet utilisateur+mois (mise en cache 10 min)
@st.cache_data(ttl=600)
def get_user_dispos(prenom_arg, annee_arg, mois_arg):
    doc = db.collection("disponibilites").document(prenom_arg).get()
    if not doc.exists:
        return []
    data = doc.to_dict()
    key = f"{annee_arg}-{mois_arg}"
    return data.get(key, [])

# 3) On “spinner” pendant la requête Firestore
with st.spinner("Chargement de tes disponibilités…"):
    dispo_set = set(get_user_dispos(prenom, year, month))

with st.spinner("Génération du calendrier…"):
    weekends = get_weekends(year, month)

# 4) Affichage des checkboxes
st.subheader("✅ Coche les week-ends où tu es disponible")
checked = {}
for samedi, dimanche in weekends:
    label = f"{samedi} – {dimanche}"
    is_checked = label in dispo_set
    checked[label] = st.checkbox(label, value=is_checked, key=label)

# 5) Bouton pour enregistrer en base
if st.button("💾 Valider mes disponibilités"):
    doc_ref = db.collection("disponibilites").document(prenom)
    doc = doc_ref.get()
    old_data = doc.to_dict() if doc.exists else {}
    clef = f"{year}-{month}"
    selected = [w for w, v in checked.items() if v]
    old_data[clef] = selected
    doc_ref.set(old_data)
    st.success("Disponibilités enregistrées ✅")
    st.cache_data.clear()  # Invalide seulement les caches Firestore

# 6) Affichage du nombre de personnes dispo par week-end (facultatif)
@st.cache_data(ttl=600)
def get_all_dispos_counts(annee_arg, mois_arg):
    key = f"{annee_arg}-{mois_arg}"
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
st.subheader("📊 Qui est disponible pour chaque week-end ?")
for samedi, dimanche in weekends:
    label = f"{samedi} – {dimanche}"
    c = counts.get(label, 0)
    st.write(f"**{label}** : {c}/{len(participants)} disponibles")
