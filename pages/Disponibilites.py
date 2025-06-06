import streamlit as st
from datetime import datetime, timedelta
from utils.firebase import db

st.set_page_config(page_title="Disponibilités", layout="wide")
st.title("📆 Disponibilités")

participants = ["Aiham", "Arthur", "Pierre", "Guillaume", "François", "Nicolas", "Hendrik", "Olivier"]

# Sélection utilisateur
user = st.selectbox("Qui êtes-vous ?", participants)

# Génération années + mois
current_year = datetime.today().year
annee = st.selectbox("Choisir une année", list(range(current_year, current_year + 3)), index=0)
mois = st.selectbox("Choisir un mois", list(range(1, 13)))

# Fonction pour obtenir tous les week-ends du mois sélectionné
@st.cache_data(ttl=600)
def get_weekends(year, month):
    weekends = []
    date = datetime(year, month, 1)
    while date.month == month:
        if date.weekday() == 5:  # samedi
            samedi = date.date()
            dimanche = (date + timedelta(days=1)).date()
            if dimanche.month == month:
                weekends.append((samedi, dimanche))
        date += timedelta(days=1)
    return weekends

weekends = get_weekends(annee, mois)

# Récupérer les dispos existantes en cache
@st.cache_data(ttl=600)
def get_user_dispos(user):
    docs = db.collection("disponibilites").where("user", "==", user).stream()
    return [doc.to_dict().get("weekend") for doc in docs]

if "dispos" not in st.session_state:
    st.session_state["dispos"] = get_user_dispos(user)

# Affichage des week-ends
st.subheader(f"Week-ends de {mois:02d}/{annee}")
selected_weekends = []

for samedi, dimanche in weekends:
    label = f"{samedi.strftime('%d/%m')} - {dimanche.strftime('%d/%m')}"
    checked = f"{samedi}_{dimanche}" in st.session_state["dispos"]
    if st.checkbox(label, key=f"{samedi}_{dimanche}", value=checked):
        selected_weekends.append(f"{samedi}_{dimanche}")

# Bouton de validation
if st.button("✅ Valider mes choix"):
    # Supprimer les anciennes dispos de cet utilisateur
    dispos_ref = db.collection("disponibilites").where("user", "==", user).stream()
    for doc in dispos_ref:
        db.collection("disponibilites").document(doc.id).delete()

    # Enregistrer les nouvelles
    for weekend in selected_weekends:
        db.collection("disponibilites").add({
            "user": user,
            "weekend": weekend,
            "timestamp": datetime.now()
        })

    st.success("Disponibilités mises à jour avec succès ✅")
    st.cache_data.clear()
