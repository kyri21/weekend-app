import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

# Initialise Firebase une seule fois à partir du secret
if not firebase_admin._apps:
    # Ici st.secrets["FIREBASE_KEY"] renvoie directement un dict Python
    firebase_key_dict = st.secrets["FIREBASE_KEY"]
    cred = credentials.Certificate(firebase_key_dict)
    firebase_admin.initialize_app(cred)

db = firestore.client()
