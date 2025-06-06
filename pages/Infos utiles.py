import streamlit as st
from utils.firebase import db

st.set_page_config(page_title="Infos utiles", layout="centered")
st.title("ℹ️ Infos utiles du groupe")

# 1️⃣ Premier bouton
if "infos_page_loaded" not in st.session_state:
    st.session_state["infos_page_loaded"] = False

def load_infos_page():
    st.session_state["infos_page_loaded"] = True

st.button("🔄 Charger les infos partagées", on_click=load_infos_page)

if not st.session_state["infos_page_loaded"]:
    st.info("Cliquez sur 🔄 Charger les infos partagées pour afficher les textes.")
    st.stop()

# 2️⃣ Imports & logique après clic
from datetime import datetime

@st.cache_data(ttl=600)
def load_infos():
    doc = db.collection("infos").document("shared").get()
    return doc.to_dict().get("contenu", "") if doc.exists else ""

contenu = load_infos()
st.text_area("📝 Notes importantes (login, RIB…)", value=contenu, height=300, key="infos_text")

if st.button("💾 Enregistrer les modifications"):
    db.collection("infos").document("shared").set({
        "contenu": st.session_state["infos_text"],
        "modifié_le": datetime.now().isoformat()
    })
    st.success("Infos mises à jour ✅")
    st.cache_data.clear()
