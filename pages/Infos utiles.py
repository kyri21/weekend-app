import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

# Initialisation Firebase (une seule fois)
if "firebase_initialized" not in st.session_state:
    cred = credentials.Certificate("firebase_key.json")
    if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)
    st.session_state.firebase_initialized = True

db = firestore.client()
st.title("🔐 Infos utiles")

# ---- Chargement depuis Firestore ----
doc_ref = db.collection("infos_utiles").document("identifiants")
doc = doc_ref.get()
data = doc.to_dict() if doc.exists else {}

# Structure par défaut
if not data:
    data = {
        "leclercdrive": {
            "site": "Leclerc Drive",
            "url": "https://leclercdrive.fr",
            "login": "kyriazis@outlook.fr",
            "mot_de_passe": "Waf1991x8!"
        },
        "sumeria": {
            "site": "RIB SUMERIA",
            "url": "",
            "login": "IBAN : FR7617598000010000671413458",
            "mot_de_passe": "BIC : LYDIFRP2XXX"
        },
        "cb_secret": {
            "numero": "4785 5430 2324 2672",
            "expiration": "12/26",
            "cvv": "808",
            "titulaire": "Arthur KYRIAZIS"
        }
    }
    doc_ref.set(data)

# ---- Affichage infos classiques (copiables) ----
st.markdown("### 🔍 Données enregistrées :")

for cle, item in data.items():
    if cle != "cb_secret":
        st.markdown(f"#### 🔗 {item['site']}")
        if item["url"]:
            st.markdown(f"- 🔗 [Lien vers le site]({item['url']})")
        st.markdown("📧 Identifiant / Email")
        st.code(item["login"], language="text")
        st.markdown("🔑 Mot de passe / Info")
        st.code(item["mot_de_passe"], language="text")
        st.markdown("---")

# ---- Carte bancaire protégée ----
st.markdown("### 💳 Accès protégé — Carte bancaire")

if "carte_visible" not in st.session_state:
    st.session_state.carte_visible = False

if not st.session_state.carte_visible:
    reponse = st.text_input("❓ Quel est le surnom de Peplum d'Andrik ?")
    if st.button("🔓 Vérifier la réponse") and reponse.lower().strip() == "commode":
        st.session_state.carte_visible = True
        st.success("✔️ Accès autorisé.")
    elif reponse:
        st.error("❌ Mauvaise réponse.")

if st.session_state.carte_visible:
    cb = data.get("cb_secret", {})
    st.markdown("#### 💳 Carte de paiement")
    st.markdown("💳 Numéro de carte")
    st.code(cb.get("numero", "-"), language="text")
    st.markdown("📅 Expiration")
    st.code(cb.get("expiration", "-"), language="text")
    st.markdown("🔒 CVV")
    st.code(cb.get("cvv", "-"), language="text")
    st.markdown("👤 Titulaire")
    st.code(cb.get("titulaire", "-"), language="text")
