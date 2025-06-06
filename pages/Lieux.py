# pages/Lieux.py

import streamlit as st
from utils.firebase import db

st.set_page_config(page_title="Lieux", layout="wide")
st.title("Lieux des week-ends")

# 1) Premier bouton pour afficher le formulaire
if "lieux_page_loaded" not in st.session_state:
    st.session_state["lieux_page_loaded"] = False

def load_lieux_page():
    st.session_state["lieux_page_loaded"] = True

st.button("Charger les lieux", on_click=load_lieux_page)

if not st.session_state["lieux_page_loaded"]:
    st.info("Cliquez sur Charger les lieux pour afficher le formulaire.")
    st.stop()

# 2) Imports et logique apres clic
import urllib.parse
from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="weekend-app")

@st.cache_data(ttl=3600)
def geocode(adresse):
    loc = geolocator.geocode(adresse)
    if loc:
        return loc.latitude, loc.longitude
    return None, None

@st.cache_data(ttl=600)
def get_lieux():
    docs = db.collection("lieux").stream()
    return {doc.id: doc.to_dict() for doc in docs}

# Formulaire d'ajout
st.subheader("Ajouter un nouveau lieu")
with st.form("ajout_lieu"):
    nom = st.text_input("Nom du lieu")
    adresse = st.text_input("Adresse (rue, ville...)")

    if st.form_submit_button("Ajouter"):
        if nom and adresse:
            lat, lon = geocode(adresse)
            if lat is not None:
                db.collection("lieux").document(nom).set({
                    "adresse": adresse,
                    "latitude": lat,
                    "longitude": lon
                })
                st.success("Lieu ajoute")
                st.cache_data.clear()
            else:
                st.error("Adresse introuvable.")
        else:
            st.warning("Merci de remplir tous les champs.")

# Lecture des lieux avec spinner
with st.spinner("Recuperation des lieux en cours..."):
    lieux = get_lieux()

if lieux:
    import pydeck as pdk

    st.subheader("Carte des lieux")
    coords = [
        {"position": [info["longitude"], info["latitude"]]}
        for info in lieux.values()
    ]
    view_state = pdk.ViewState(
        latitude=list(lieux.values())[0]["latitude"],
        longitude=list(lieux.values())[0]["longitude"],
        zoom=5,
        pitch=0
    )
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=coords,
        get_position="position",
        get_radius=100,
        get_color=[255, 0, 0],
        pickable=True
    )
    st.pydeck_chart(pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9",
        initial_view_state=view_state,
        layers=[layer]
    ))

    st.subheader("Detail des lieux")
    for nom, info in lieux.items():
        col1, col2, col3, col4 = st.columns([4, 1, 1, 1])
        with col1:
            st.markdown(f"**{nom}** — {info['adresse']}")
        query = urllib.parse.quote_plus(info["adresse"])
        with col2:
            st.markdown(f"[Google Maps](https://www.google.com/maps/search/?api=1&query={query})")
        with col3:
            st.markdown(f"[Apple Maps](https://maps.apple.com/?q={query})")
        with col4:
            st.markdown(f"[Waze](https://waze.com/ul?q={query})")

        if st.button(f"Supprimer {nom}", key=nom):
            db.collection("lieux").document(nom).delete()
            st.warning(f"{nom} supprime")
            st.cache_data.clear()
            st.experimental_rerun()
else:
    st.info("Aucun lieu enregistre pour l’instant.")
