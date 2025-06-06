import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timedelta
import calendar

# Initialisation Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_key.json")
    firebase_admin.initialize_app(cred)
db = firestore.client()

st.title("📅 Disponibilités")

participants = [
    "Aiham", "Arthur", "Pierre", "Guillaume", "François", "Nicolas", "Hendrik", "Olivier"
]

selected_name = st.selectbox("Qui êtes-vous ?", participants)

# Sélection de l’année
current_year = datetime.now().year
years = list(range(current_year, current_year + 5))
selected_year = st.selectbox("Année", years, index=0)

# Sélection du mois
months = list(calendar.month_name)[1:]
selected_month_name = st.selectbox("Mois", months)
selected_month = months.index(selected_month_name) + 1

# Calcul des week-ends
def get_weekends(year, month):
    weekends = []
    for day in range(1, calendar.monthrange(year, month)[1] + 1):
        date = datetime(year, month, day)
        if date.weekday() == 5:  # Samedi
            sunday = date + timedelta(days=1)
            if sunday.month == month:
                weekends.append((date.strftime("%d/%m/%Y"), sunday.strftime("%d/%m/%Y")))
    return weekends

weekends = get_weekends(selected_year, selected_month)

# Chargement des données existantes
doc_ref = db.collection("disponibilites").document(selected_name)
doc = doc_ref.get()
dispos = doc.to_dict().get("dispos", []) if doc.exists else []

# Affichage des cases à cocher
st.write("Cochez les week-ends où vous êtes disponible :")
new_dispos = []
for samedi, dimanche in weekends:
    label = f"{samedi} - {dimanche}"
    checked = label in dispos
    if st.checkbox(label, value=checked):
        new_dispos.append(label)

# Sauvegarde
if st.button("✅ Valider mes choix"):
    doc_ref.set({"dispos": new_dispos})
    st.success("Disponibilités enregistrées !")
