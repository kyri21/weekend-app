import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

# Initialise Firebase une seule fois en utilisant le secret
if not firebase_admin._apps:
    # st.secrets["FIREBASE_KEY"] est déjà un dict Python, pas besoin de json.loads
    firebase_key_dict = st.secrets["FIREBASE_KEY"]
    cred = credentials.Certificate(firebase_key_dict)
    firebase_admin.initialize_app(cred)

db = firestore.client()
