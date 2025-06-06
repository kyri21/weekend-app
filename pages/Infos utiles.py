import streamlit as st
from utils.firebase import db

st.set_page_config(page_title="Infos utiles", layout="centered")
st.title("ℹ️ Infos utiles")

st.markdown("Note : ces infos sont visibles par tout le groupe. Ne pas inclure d’informations personnelles sensibles.")

@st.cache_data(ttl=600)
def get_infos():
    doc = db.collection("infos").document("partage").get()
    if doc.exists:
        return doc.to_dict().get("contenu", "")
    return ""

def save_infos(text):
    db.collection("infos").document("partage").set({"contenu": text})
    st.success("Informations mises à jour avec succès ✅")
    st.cache_data.clear()

contenu = get_infos()

st.text_area("📝 Bloc de texte partagé", value=contenu, height=400, key="infos_input")

if st.button("💾 Enregistrer"):
    save_infos(st.session_state["infos_input"])
