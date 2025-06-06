import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import json

# Initialise Firebase une seule fois
if not firebase_admin._apps:
    # Récupère le secret
    secret = st.secrets.get("FIREBASE_KEY")

    # Si c'est une chaîne (JSON brut), on décode en dict
    if isinstance(secret, str):
        try:
            firebase_key_dict = json.loads(secret)
        except json.JSONDecodeError as e:
            st.error("Erreur JSON dans ton secret FIREBASE_KEY : " + str(e))
            st.stop()
    # Sinon, s’il s'agit déjà d'un dict (format TOML table), on l'utilise tel quel
    elif isinstance(secret, dict):
        firebase_key_dict = secret
    else:
        st.error(f"Type inattendu pour st.secrets['FIREBASE_KEY'] : {type(secret)}")
        st.stop()

    # Initialisation
    cred = credentials.Certificate(firebase_key_dict)
    firebase_admin.initialize_app(cred)

db = firestore.client()
