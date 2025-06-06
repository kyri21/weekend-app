import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import json

# Initialise Firebase **UNE SEULE FOIS** en lisant st.secrets
if not firebase_admin._apps:
    firebase_key_dict = json.loads(st.secrets["FIREBASE_KEY"])
    cred = credentials.Certificate(firebase_key_dict)
    firebase_admin.initialize_app(cred)

db = firestore.client()
