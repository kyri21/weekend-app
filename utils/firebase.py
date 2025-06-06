import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import json

# Initialise Firebase une seule fois
if not firebase_admin._apps:
    # Récupère le secret défini dans Streamlit Cloud
    secret = st.secrets.get("FIREBASE_KEY")

    # Si le secret est une chaîne (JSON brut), on la convertit en dict
    if isinstance(secret, str):
        try:
            firebase_key_dict = json.loads(secret)
        except json.JSONDecodeError as e:
            st.error("Erreur JSON dans le secret FIREBASE_KEY : " + str(e))
            st.stop()
    # Si le secret est déjà un dict (format TOML table), on l’utilise directement
    elif isinstance(secret, dict):
        firebase_key_dict = secret
    else:
        st.error(f"Type inattendu pour st.secrets['FIREBASE_KEY'] : {type(secret)}")
        st.stop()

    # Initialise l’app Firebase avec ce dict
    cred = credentials.Certificate(firebase_key_dict)
    firebase_admin.initialize_app(cred)

# Obtient le client Firestore
db = firestore.client()
