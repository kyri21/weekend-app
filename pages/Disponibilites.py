import streamlit as st
from utils.firebase import db

st.set_page_config(page_title="Disponibilités", layout="centered")
st.title("📅 Disponibilités des week-ends")

# Sélection du prénom et des paramètres
participants = ["Aiham", "Arthur", "Pierre", "Guillaume", "François", "Nicolas", "Hendrik", "Olivier"]
prenom = st.selectbox("👤 Qui êtes-vous ?", participants)
prenom_loaded = False  # indique si on a déjà chargé les données après clic

# Bouton pour lancer le chargement
if st.button("🔄 Charger mes disponibilités"):
    prenom_loaded = True

if prenom_loaded:
    # Ici, on importe tout ce qui est nécessaire
    import calendar
    from datetime import datetime, timedelta

    # Dictionnaire pour convertir le mois en nombre
    mois_dict = {
        "Janvier": 1, "Février": 2, "Mars": 3, "Avril": 4,
        "Mai": 5, "Juin": 6, "Juillet": 7, "Août": 8,
        "Septembre": 9, "Octobre": 10, "Novembre": 11, "Décembre": 12
    }

    # Sélection de l'année et du mois
    current_year = datetime.now().year
    year = st.selectbox("📆 Année", list(range(current_year, current_year + 3)), index=0)
    month_name = st.selectbox("🗓️ Mois", list(mois_dict.keys()), index=datetime.now().month - 1)
    month = mois_dict[month_name]

    # Fonction mise en cache pour générer les week-ends
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

    # Fonction mise en cache pour récupérer les dispos de l’utilisateur
    @st.cache_data(ttl=600)
    def get_user_dispos(prenom_arg, year_arg, month_arg):
        doc = db.collection("disponibilites").document(prenom_arg).get()
        if not doc.exists:
            return []
        data = doc.to_dict()
        key = f"{year_arg}-{month_arg}"
        return data.get(key, [])

    # Lecture des dispos existantes (cache) et génération du calendrier
    dispo_set = set(get_user_dispos(prenom, year, month))
    weekends = get_weekends(year, month)

    st.subheader("✅ Cochez les week-ends où vous êtes disponible")
    checked = {}
    for samedi, dimanche in weekends:
        label = f"{samedi} – {dimanche}"
        is_checked = label in dispo_set
        checked[label] = st.checkbox(label, value=is_checked, key=label)

    if st.button("💾 Valider mes disponibilités"):
        # Récupère l’ancien document (s’il existe)
        doc_ref = db.collection("disponibilites").document(prenom)
        doc = doc_ref.get()
        old_data = doc.to_dict() if doc.exists else {}
        key = f"{year}-{month}"
        # Conserve uniquement les week-ends cochés
        selected = [w for w, v in checked.items() if v]
        old_data[key] = selected
        doc_ref.set(old_data)
        st.success("Disponibilités enregistrées ✅")
        st.cache_data.clear()

    # Affichage du nombre de personnes dispo par week-end (optionnel)
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

    counts = get_all_dispos_counts(year, month)
    st.divider()
    st.subheader("📊 Combien sont disponibles pour chaque week-end ?")
    for samedi, dimanche in weekends:
        label = f"{samedi} – {dimanche}"
        c = counts.get(label, 0)
        st.write(f"**{label}** : {c}/{len(participants)}")
else:
    st.info("Cliquez sur 🔄 Charger mes disponibilités pour démarrer.")


