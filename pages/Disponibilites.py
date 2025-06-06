import streamlit as st
import calendar
from datetime import datetime, timedelta
from utils.firebase import db

st.set_page_config(page_title="Disponibilités", layout="wide")
st.title("📅 Disponibilités week-ends")

participants = ["Aiham", "Arthur", "Pierre", "Guillaume", "François", "Nicolas", "Hendrik", "Olivier"]

prenom = st.selectbox("👤 Qui êtes-vous ?", participants)

col1, col2 = st.columns(2)
with col1:
    month = st.selectbox("📆 Mois :", list(calendar.month_name)[1:], index=datetime.now().month - 1)
with col2:
    year = st.selectbox("🗓️ Année :", list(range(datetime.now().year, datetime.now().year + 5)), index=0)

@st.cache_data(ttl=3600)
def get_weekends(y, m):
    weekends = []
    cal = calendar.Calendar(firstweekday=0)
    for week in cal.monthdatescalendar(y, m):
        saturday = week[5]
        sunday = week[6]
        if saturday.month == m and sunday.month == m:
            weekends.append((saturday, sunday))
    return weekends

weekends = get_weekends(year, list(calendar.month_name).index(month))

doc_ref = db.collection("disponibilites").document(prenom)
doc = doc_ref.get()
data = doc.to_dict() if doc.exists else {}

dispos = data.get(f"{year}-{month}", [])

st.markdown("### ✅ Cochez vos week-ends disponibles")

with st.form("dispos_form"):
    new_dispos = []
    for samedi, dimanche in weekends:
        label = f"🗓️ {samedi.strftime('%d/%m')} et {dimanche.strftime('%d/%m')}"
        is_checked = label in dispos
        if st.checkbox(label, value=is_checked, key=label):
            new_dispos.append(label)

    if st.form_submit_button("💾 Valider mes disponibilités"):
        updated = data
        updated[f"{year}-{month}"] = new_dispos
        doc_ref.set(updated)
        st.success("Vos disponibilités ont bien été enregistrées ✅")
        st.cache_data.clear()
