# pages/Disponibilites.py

import streamlit as st
from utils.firebase import db

st.set_page_config(page_title="Disponibilites", layout="centered")
st.title("Disponibilites des week-ends")

# 1) Premier bouton pour afficher le formulaire de selection
if "dispo_page_loaded" not in st.session_state:
    st.session_state["dispo_page_loaded"] = False

def load_dispo_page():
    st.session_state["dispo_page_loaded"] = True

# Attention : bien fermer la parenthese ici
st.button("Charger mes disponibilites", on_click=load_dispo_page)

if not st.session_state["dispo_page_loaded"]:
    st.info("Cliquez sur Charger mes disponibilites pour afficher le formulaire.")
    st.stop()

# 2) Imports et logique apres clic
import calendar
from datetime import datetime, timedelta

participants = [
    "Aiham", "Arthur", "Pierre", "Guillaume",
    "Francois", "Nicolas", "Hendrik", "Olivier"
]
prenom = st.selectbox("Qui es-tu ?", participants)

current_year = datetime.now().year
year = st.selectbox("Annee", list(range(current_year, current_year + 3)), index=0)

mois_dict = {
    "Janvier": 1, "Fevrier": 2, "Mars": 3, "Avril": 4,
    "Mai": 5, "Juin": 6, "Juillet": 7, "Aout": 8,
    "Septembre": 9, "Octobre": 10, "Novembre": 11, "Decembre": 12
}
month_name = st.selectbox("Mois", list(mois_dict.keys()), index=datetime.now().month - 1)
month = mois_dict[month_name]

# 3) Second bouton pour declencher la recherche en base
if "dispo_data_loaded" not in st.session_state:
    st.session_state["dispo_data_loaded"] = False

def load_dispo_data():
    st.session_state["dispo_data_loaded"] = True

# Encore bien fermer la parenthese
st.button("Afficher mes disponibilites", on_click=load_dispo_data)

if not st.session_state["dispo_data_loaded"]:
    st.info("Une fois prenom, annee et mois choisis, cliquez sur Afficher mes disponibilites.")
    st.stop()

# 4) Fonctions mises en cache et spinners

@st.cache_data(ttl=3600)
def get_weekends(annee_arg, mois_arg):
    """
    Renvoie la liste des week-ends (samedi, dimanche) pour l’annee annee_arg et le mois mois_arg.
    """
    weekends = []
    date = datetime(annee_arg, mois_arg, 1)
    while date.month == mois_arg:
        if date.weekday() == 5:  # samedi
            sunday = date + timedelta(days=1)
            if sunday.month == mois_arg:
                weekends.append((date.strftime("%d/%m/%Y"), sunday.strftime("%d/%m/%Y")))
        date += timedelta(days=1)
    return weekends

@st.cache_data(ttl=600)
def get_user_dispos(prenom_arg, annee_arg, mois_arg):
    """
    Lit le document 'disponibilites/<prenom_arg>' dans Firestore,
    puis renvoie la liste des week-ends deja coches pour la cle 'annee-mois'.
    """
    doc = db.collection("disponibilites").document(prenom_arg).get()
    if not doc.exists:
        return []
    data = doc.to_dict()
    key = f"{annee_arg}-{mois_arg}"
    return data.get(key, [])

# Affichage des spinners pendant les appels
with st.spinner("Chargement des disponibilites en cours..."):
    dispo_set = set(get_user_dispos(prenom, year, month))

with st.spinner("Generation du calendrier en cours..."):
    weekends = get_weekends(year, month)

st.subheader("Cochez les week-ends ou vous etes disponible")
checked = {}
for samedi, dimanche in weekends:
    label = f"{samedi} - {dimanche}"
    is_checked = label in dispo_set
    checked[label] = st.checkbox(label, value=is_checked, key=label)

# 5) Enregistrer les disponibilites en base
if st.button("Valider mes disponibilites"):
    doc_ref = db.collection("disponibilites").document(prenom)
    doc = doc_ref.get()
    old_data = doc.to_dict() if doc.exists else {}
    key = f"{year}-{month}"
    selected = [w for w, v in checked.items() if v]
    old_data[key] = selected
    doc_ref.set(old_data)
    st.success("Disponibilites enregistrees")
    st.cache_data.clear()

# 6) Afficher le nombre de personnes disponibles par week-end (optionnel)
@st.cache_data(ttl=600)
def get_all_dispos_counts(annee_arg, mois_arg):
    """
    Compte combien de personnes ont coche chaque week-end pour la cle 'annee-mois'.
    """
    key = f"{annee_arg}-{mois_arg}"
    docs = db.collection("disponibilites").stream()
    counts = {}
    for d in docs:
        data = d.to_dict().get(key, [])
        for w in data:
            counts[w] = counts.get(w, 0) + 1
    return counts

with st.spinner("Calcul des statistiques en cours..."):
    counts = get_all_dispos_counts(year, month)

st.divider()
st.subheader("Qui est disponible pour chaque week-end ?")
for samedi, dimanche in weekends:
    label = f"{samedi} - {dimanche}"
    c = counts.get(label, 0)
    st.write(f"{label} : {c}/{len(participants)} disponibles")
