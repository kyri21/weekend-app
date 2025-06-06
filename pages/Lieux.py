import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import urllib.parse
import folium
from streamlit_folium import st_folium

# Init Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_key.json")
    firebase_admin.initialize_app(cred)
db = firestore.client()

st.title("📍 Lieux")

col1, col2 = st.columns(2)
with col1:
    nom = st.text_input("Nom du lieu")
with col2:
    adresse = st.text_input("Adresse (rue, ville...)")

# Enregistrement
if st.button("Ajouter le lieu") and nom and adresse:
    db.collection("lieux").add({"nom": nom, "adresse": adresse})
    st.success("Lieu ajouté !")

# Affichage des lieux
docs = db.collection("lieux").stream()
lieux = [{"id": d.id, **d.to_dict()} for d in docs]

for lieu in lieux:
    st.markdown(f"### {lieu['nom']}")
    encoded_address = urllib.parse.quote_plus(lieu['adresse'])
    st.write(f"📍 {lieu['adresse']}")
    st.markdown(f"[🗺️ Google Maps](https://www.google.com/maps/search/?api=1&query={encoded_address})")
    st.markdown(f"[🍏 Apple Maps](http://maps.apple.com/?q={encoded_address})")
    st.markdown(f"[🚗 Waze](https://waze.com/ul?q={encoded_address})")

    if st.button(f"🗑️ Supprimer {lieu['nom']}", key=lieu['id']):
        db.collection("lieux").document(lieu['id']).delete()
        st.success("Lieu supprimé.")
        st.experimental_rerun()

# Carte
if lieux:
    st.subheader("🗺️ Carte interactive")
    carte = folium.Map(location=[48.8566, 2.3522], zoom_start=5)
    for lieu in lieux:
        folium.Marker(location=None, popup=lieu["nom"]).add_to(carte)
    st_folium(carte, width=700, height=400)
