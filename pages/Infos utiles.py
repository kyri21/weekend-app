import streamlit as st
from utils.firebase import db
from datetime import datetime

st.set_page_config(page_title="Infos utiles", layout="centered")
st.title("ℹ️ Infos utiles du groupe")

@st.cache_data(ttl=600)
def load_infos():
    doc = db.collection("infos").document("shared").get()
    return doc.to_dict().get("contenu", "") if doc.exists else ""

contenu = load_infos()

st.text_area("📝 Notes importantes (Login, RIB…)", value=contenu, height=300, key="infos_text")

if st.button("💾 Enregistrer les modifications"):
    db.collection("infos").document("shared").set({
        "contenu": st.session_state["infos_text"],
        "modifié_le": datetime.now().isoformat()
    })
    st.success("Infos mises à jour ✅")
    st.cache_data.clear()
