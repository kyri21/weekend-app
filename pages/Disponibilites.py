import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import datetime
import calendar

# Initialisation Firebase (une seule fois)
if "firebase_initialized" not in st.session_state:
    cred = credentials.Certificate("firebase_key.json")
    if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)
    st.session_state.firebase_initialized = True

db = firestore.client()

# Membres du groupe
membres = ["Aiham", "Arthur", "Pierre", "Guillaume", "François", "Nicolas", "Hendrik", "Olivier"]
mois_noms = {
    1: "Janvier", 2: "Février", 3: "Mars", 4: "Avril",
    5: "Mai", 6: "Juin", 7: "Juillet", 8: "Août",
    9: "Septembre", 10: "Octobre", 11: "Novembre", 12: "Décembre"
}

st.title("📅 Disponibilités des week-ends")

# Sélection du prénom
prenom = st.selectbox("Je suis :", membres)

# Sélection de l'année et du mois
annee_selectionnee = st.selectbox("Choisis une année :", list(range(2025, 2031)))
mois_selectionne = st.selectbox("Choisis un mois :", list(mois_noms.values()))
mois_num = [k for k, v in mois_noms.items() if v == mois_selectionne][0]

# Récupération des dispos déjà enregistrées
doc_ref = db.collection("disponibilites").document(prenom)
doc = doc_ref.get()
dispo_existantes = doc.to_dict()["dates"] if doc.exists else []

# Fonction : week-ends d’une année donnée
@st.cache_data
def get_weekends(year):
    weekends = []
    date = datetime.date(year, 1, 1)
    end = datetime.date(year, 12, 31)
    while date <= end:
        if date.weekday() == 5:  # samedi
            dimanche = date + datetime.timedelta(days=1)
            weekends.append((date, dimanche))
        date += datetime.timedelta(days=1)
    return weekends

weekends = get_weekends(annee_selectionnee)
weekends_du_mois = [(s, d) for (s, d) in weekends if s.month == mois_num]

# Interface de sélection
st.markdown("### ✅ Coche les week-ends où tu es disponible :")
dates_cochees = []

for samedi, dimanche in weekends_du_mois:
    date_id = f"{samedi.isoformat()}_{dimanche.isoformat()}"
    label = f"{samedi.strftime('%d %b %Y')} - {dimanche.strftime('%d %b %Y')}"
    checked = date_id in dispo_existantes
    if st.checkbox(label, value=checked, key=date_id):
        dates_cochees.append(date_id)

# Valider
if st.button("✅ Valider mes choix"):
    nouvelles = set(dates_cochees)
    anciennes = set(dispo_existantes)
    toutes = list(nouvelles.union(anciennes))
    doc_ref.set({"dates": toutes})
    st.success("✔️ Disponibilités mises à jour avec succès !")

# Affichage des week-ends communs
st.markdown("---")
st.markdown("### 🟢 Week-ends disponibles pour tout le monde :")

all_dispos = db.collection("disponibilites").stream()
dispos_dict = {}
for d in all_dispos:
    data = d.to_dict()
    dispos_dict[d.id] = set(data.get("dates", []))

if len(dispos_dict) == len(membres):
    communs = set.intersection(*dispos_dict.values())
    if communs:
        for d in sorted(communs):
            samedi, dimanche = d.split("_")
            s = datetime.date.fromisoformat(samedi)
            d = datetime.date.fromisoformat(dimanche)
            st.markdown(f"- **{s.strftime('%d %b %Y')} - {d.strftime('%d %b %Y')}**")
    else:
        st.warning("❌ Aucun week-end commun pour l’instant.")
else:
    st.info("🕐 En attente que tout le monde ait rempli ses dispos.")
