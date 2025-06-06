import streamlit as st
import pydeck as pdk
from utils.firebase import db
from geopy.geocoders import Nominatim

st.set_page_config(page_title="Lieux", layout="wide")
st.title("📍 Lieux des week-ends")

geolocator = Nominatim(user_agent="weekend-app")

@st.cache_data(ttl=3600)
def geocode(address):
    loc = geolocator.geocode(address)
    if loc:
        return loc.latitude, loc.longitude
    return None, None

@st.cache_data(ttl=600)
def get_lieux():
    docs = db.collection("lieux").stream()
    return {doc.id: doc.to_dict() for doc in docs}

# — Formulaire d'ajout (lazy load)
st.subheader("➕ Ajouter un nouveau lieu")
with st.form("ajout_lieu"):
    nom = st.text_input("🏡 Nom du lieu", key="nom")
    adresse = st.text_input("📍 Adresse complète (rue, ville...)", key="adresse")
    submit = st.form_submit_button("✅ Ajouter")
    if submit:
        if nom and adresse:
            lat, lon = geocode(adresse)
            if lat is not None:
                db.collection("lieux").document(nom).set({
                    "adresse": adresse,
                    "latitude": lat,
                    "longitude": lon
                })
                st.success("Lieu ajouté ✅")
                st.cache_data.clear()
            else:
                st.error("Adresse non trouvée.")
        else:
            st.warning("Merci de remplir tous les champs.")

lieux = get_lieux()

if lieux:
    # Affichage carte
    st.subheader("🗺️ Carte interactive des lieux")
    coords = [{"lat": info["latitude"], "lon": info["longitude"]} for info in lieux.values()]
    df = st.experimental_data_editor(coords, num_rows="never")  # droit de lire un peu
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=[{"position": [info["longitude"], info["latitude"]]} for info in lieux.values()],
        get_position="position",
        get_radius=100,
        get_color=[255, 0, 0],
        pickable=True
    )
    view_state = pdk.ViewState(
        latitude=list(lieux.values())[0]["latitude"],
        longitude=list(lieux.values())[0]["longitude"],
        zoom=5,
        pitch=0
    )
    st.pydeck_chart(pdk.Deck(map_style="mapbox://styles/mapbox/light-v9",
                             initial_view_state=view_state,
                             layers=[layer]))

    # Liste détaillée + suppression
    st.subheader("📌 Détails des lieux")
    for nom, info in lieux.items():
        col1, col2, col3, col4 = st.columns([4, 1, 1, 1])
        with col1:
            st.markdown(f"**{nom}** — {info['adresse']}")
        query = info["adresse"].replace(" ", "+")
        with col2:
            st.markdown(f"[🗺️ Google Maps](https://www.google.com/maps/search/?api=1&query={query})")
        with col3:
            st.markdown(f"[🍎 Apple Maps](https://maps.apple.com/?q={query})")
        with col4:
            st.markdown(f"[🚗 Waze](https://waze.com/ul?q={query})")
        # Bouton suppression
        if st.button(f"🗑️ Supprimer {nom}", key=f"suppr_{nom}"):
            db.collection("lieux").document(nom).delete()
            st.warning(f"{nom} supprimé !")
            st.cache_data.clear()
            st.experimental_rerun()
else:
    st.info("Aucun lieu enregistré pour l'instant.")
