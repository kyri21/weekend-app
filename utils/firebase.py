import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import json
from collections.abc import Mapping

# Initialise Firebase une seule fois
if not firebase_admin._apps:
    # Récupère le secret depuis Streamlit Cloud
    secret = st.secrets.get("FIREBASE_KEY")

    # Si le secret est une chaîne JSON, on la convertit en dict
    if isinstance(secret, str):
        try:
            firebase_key_dict = json.loads(secret)
        except json.JSONDecodeError as e:
            st.error("Erreur JSON dans le secret FIREBASE_KEY : " + str(e))
            st.stop()
    # Si c'est déjà un dict ou un AttrDict (Mapping), on le transforme en dict Python
    elif isinstance(secret, Mapping):
        firebase_key_dict = dict(secret)
    else:
        st.error(f"Type inattendu pour st.secrets['FIREBASE_KEY'] : {type(secret)}")
        st.stop()

    # Initialise l'application Firebase
    cred = credentials.Certificate(firebase_key_dict)
    firebase_admin.initialize_app(cred)

# Le client Firestore
db = firestore.client()
