import streamlit as st
import pydeck as pdk
from utils.firebase import db
from geopy.geocoders import Nominatim

st.set_page_config(page_title="Lieux", layout="wide")
st.title("📍 Lieux des week-ends")

geolocator = Nominatim(user_agent="weekend-app")

@st.cache_data(ttl=3600)
def geocode(address):
    location = geolocator.geocode(address)
    if location:
        return location.latitude, location.longitude
    return None, None

@st.cache_data(ttl=600)
def get_lieux():
    docs = db.collection("lieux").stream()
    return {doc.id: doc.to_dict() for doc in docs}

# Ajouter un lieu
st.subheader("➕ Ajouter un nouveau lieu")
with st.form("ajout_lieu"):
    nom = st.text_input("🏡 Nom du lieu (ex: Gîte à Arles)")
    adresse = st.text_input("📍 Adresse")
    submit = st.form_submit_button("✅ Ajouter")
    if submit and nom and adresse:
        lat, lon = geocode(adresse)
        if lat:
            db.collection("lieux").document(nom).set({
                "adresse": adresse,
                "latitude": lat,
                "longitude": lon
            })
            st.success("Lieu ajouté !")
            st.cache_data.clear()
        else:
            st.error("Adresse introuvable.")

# Afficher les lieux
st.divider()
st.subheader("🗺️ Carte des lieux enregistrés")

lieux = get_lieux()
if lieux:
    data = [{"name": k, "lat": v["latitude"], "lon": v["longitude"]} for k, v in lieux.items()]
    st.map(data)

    st.subheader("📌 Détails et itinéraires")
    for nom, info in lieux.items():
        st.markdown(f"**{nom}** — {info['adresse']}")
        google_maps = f"https://www.google.com/maps/search/?api=1&query={info['adresse'].replace(' ', '+')}"
        apple_maps = f"https://maps.apple.com/?q={info['adresse'].replace(' ', '+')}"
        waze = f"https://waze.com/ul?q={info['adresse'].replace(' ', '+')}"
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
        col1.write("")
        col2.markdown(f"[🗺️ Google Maps]({google_maps})")
        col3.markdown(f"[🍎 Apple Maps]({apple_maps})")
        col4.markdown(f"[🚗 Waze]({waze})")
        if st.button(f"🗑️ Supprimer {nom}", key=nom):
            db.collection("lieux").document(nom).delete()
            st.warning(f"{nom} supprimé.")
            st.cache_data.clear()
            st.experimental_rerun()
else:
    st.info("Aucun lieu enregistré pour l’instant.")
