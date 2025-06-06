import streamlit as st
from utils.firebase import db
import urllib.parse
import pydeck as pdk

st.set_page_config(page_title="Lieux", layout="wide")
st.title("🗺️ Lieux visités")

# Formulaire pour ajouter un nouveau lieu
st.subheader("➕ Ajouter un lieu")
adresse = st.text_input("Adresse complète")
latitude = st.number_input("Latitude", format="%.6f")
longitude = st.number_input("Longitude", format="%.6f")

if st.button("📍 Enregistrer le lieu"):
    if adresse and latitude and longitude:
        db.collection("lieux").add({
            "adresse": adresse,
            "latitude": latitude,
            "longitude": longitude
        })
        st.success("✅ Lieu ajouté")
        st.cache_data.clear()
    else:
        st.warning("Merci de remplir tous les champs")

# Récupérer les lieux
@st.cache_data(ttl=600)
def get_lieux():
    docs = db.collection("lieux").stream()
    lieux = []
    for doc in docs:
        d = doc.to_dict()
        d["id"] = doc.id
        lieux.append(d)
    return lieux

st.subheader("📌 Lieux enregistrés")
lieux = get_lieux()

# Afficher les lieux avec liens
for lieu in lieux:
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown(f"**{lieu['adresse']}**")
        query = urllib.parse.quote_plus(lieu['adresse'])
        st.markdown(
            f"[Google Maps](https://www.google.com/maps/search/?api=1&query={query})  | "
            f"[Apple Maps](https://maps.apple.com/?q={query})  | "
            f"[Waze](https://waze.com/ul?ll={lieu['latitude']},{lieu['longitude']})"
        )
    with col2:
        if st.button(f"🗑️ Supprimer", key=lieu["id"]):
            db.collection("lieux").document(lieu["id"]).delete()
            st.success(f"❌ Supprimé : {lieu['adresse']}")
            st.cache_data.clear()
            st.experimental_rerun()

# Carte interactive
if lieux:
    st.subheader("🗺️ Carte des lieux")
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=lieux,
        get_position='[longitude, latitude]',
        get_radius=100,
        get_color=[255, 0, 0],
        pickable=True
    )
    view_state = pdk.ViewState(
        latitude=lieux[0]['latitude'],
        longitude=lieux[0]['longitude'],
        zoom=5,
        pitch=0
    )
    st.pydeck_chart(pdk.Deck(map_style='mapbox://styles/mapbox/light-v9', initial_view_state=view_state, layers=[layer]))
