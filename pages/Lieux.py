import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import urllib.parse
from geopy.geocoders import Nominatim
import folium
from streamlit_folium import st_folium

# Initialisation Firebase
if "firebase_initialized" not in st.session_state:
    cred = credentials.Certificate("firebase_key.json")
    if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)
    st.session_state.firebase_initialized = True

db = firestore.client()
geolocator = Nominatim(user_agent="weekend-app")
st.title("📍 Lieux")

# Référence Firestore
lieux_ref = db.collection("lieux")
docs = lieux_ref.stream()
lieux = [{"id": doc.id, **doc.to_dict()} for doc in docs]

# ---- Formulaire d’ajout ----
st.subheader("➕ Ajouter un lieu")

with st.form("ajout_lieu"):
    adresse = st.text_input("🏠 Adresse complète")
    nom = st.text_input("📝 Nom ou description (optionnel)")
    submit = st.form_submit_button("✅ Ajouter")

    if submit and adresse.strip():
        lieux_ref.add({"adresse": adresse.strip(), "nom": nom.strip()})
        st.success("✔️ Lieu ajouté avec succès !")
        st.rerun()


# ---- Carte interactive ----
if lieux:
    st.subheader("🗺️ Carte des lieux")

    m = folium.Map(location=[46.5, 2.5], zoom_start=5)

    for lieu in lieux:
        try:
            location = geolocator.geocode(lieu["adresse"])
            if location:
                folium.Marker(
                    location=[location.latitude, location.longitude],
                    popup=lieu.get("nom", lieu["adresse"]),
                    tooltip=lieu.get("nom", lieu["adresse"])
                ).add_to(m)
        except Exception as e:
            pass  # ignore errors

    st_folium(m, width=700, height=400)

# ---- Affichage des lieux enregistrés ----
st.subheader("📌 Liste des lieux")

if not lieux:
    st.info("Aucun lieu enregistré pour le moment.")
else:
    for lieu in lieux:
        adresse = lieu["adresse"]
        nom = lieu.get("nom", "").strip()
        enc_adresse = urllib.parse.quote_plus(adresse)

        google_url = f"https://www.google.com/maps/search/?api=1&query={enc_adresse}"
        apple_url = f"http://maps.apple.com/?daddr={enc_adresse}"
        waze_url = f"https://waze.com/ul?ll=&q={enc_adresse}"

        st.markdown(f"#### 📍 {nom if nom else adresse}")
        if nom:
            st.markdown(f"- **Adresse :** {adresse}")
        st.markdown(f"[🗺️ Google Maps]({google_url}) | [🍎 Apple Maps]({apple_url}) | [🚗 Waze]({waze_url})")

        # Bouton de suppression
        if st.button(f"🗑️ Supprimer ce lieu", key=f"suppr_{lieu['id']}"):
            lieux_ref.document(lieu["id"]).delete()
            st.success(f"❌ Lieu supprimé : {nom or adresse}")
            st.rerun()

        st.markdown("---")
