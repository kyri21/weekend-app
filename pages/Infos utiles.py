import streamlit as st
from utils.firebase import db
from datetime import datetime

st.set_page_config(page_title="Infos utiles", layout="centered")
st.title("🧾 Infos importantes (logins, numéros, etc.)")

@st.cache_data(ttl=600)
def load_infos():
    doc = db.collection("infos").document("shared").get()
    return doc.to_dict() if doc.exists else {}

data = load_infos()
default_text = data.get("contenu", "")

st.text_area("📝 Notes importantes", value=default_text, height=300, key="infos_text")

if st.button("✅ Enregistrer les modifications"):
    db.collection("infos").document("shared").set({
        "contenu": st.session_state["infos_text"],
        "modifié_le": datetime.now().isoformat()
    })
    st.success("Infos mises à jour avec succès ✅")
    st.cache_data.clear()
