import streamlit as st
from utils.firebase import db

st.set_page_config(page_title="Trésorerie", layout="centered")
st.title("💰 Trésorerie de l'association")

# --- Initialisation du flag lazy-loading --- #
if "trez_loaded" not in st.session_state:
    st.session_state["trez_loaded"] = False

# Bouton unique pour déclencher le chargement des données
def load_tresorerie():
    st.session_state["trez_loaded"] = True

st.button("🔄 Charger les données de trésorerie", on_click=load_tresorerie)

# Si on n'a pas encore cliqué, on affiche une info
if not st.session_state["trez_loaded"]:
    st.info("Clique sur 🔄 Charger les données de trésorerie pour démarrer.")
    st.stop()  # on arrête ici, on ne charge pas les imports et la logique plus bas

# --------- À partir d'ici, trez_loaded == True => on charge vraiment --------- #

# Importer les modules lourds *seulement après* le clic
import pandas as pd
from datetime import datetime

# Fonctions mises en cache
@st.cache_data(ttl=600)
def get_solde():
    """
    Récupère le document 'solde' dans la collection 'tresorerie'.
    Renvoie le montant sous forme de float.
    """
    doc = db.collection("tresorerie").document("solde").get()
    return doc.to_dict().get("montant", 0.0) if doc.exists else 0.0

@st.cache_data(ttl=600)
def get_depenses_par_annee(annee_arg):
    """
    Lit uniquement les documents dont le champ 'annee' == annee_arg.
    Renvoie un DataFrame pandas des dépenses de cette année.
    """
    docs = db.collection("tresorerie").where("annee", "==", annee_arg).stream()
    data = []
    for doc in docs:
        d = doc.to_dict()
        data.append(d)
    # Créer un DataFrame, ou un DataFrame vide si aucun résultat
    if data:
        return pd.DataFrame(data)
    else:
        # DataFrame avec les colonnes attendues, si besoin
        return pd.DataFrame(columns=["date", "montant", "categorie", "description", "annee"])

# Sélection de l'année (une fois qu'on a cliqué)
current_year = datetime.now().year
annee = st.selectbox("📅 Année", list(range(current_year, current_year - 11, -1)), index=0)

# Affichage du solde avec un spinner pendant la requête
with st.spinner("Chargement du solde en cours…"):
    solde = get_solde()
st.metric("💼 Solde actuel de l'association", f"{solde:.2f} €")

# Formulaire pour ajouter une dépense
st.subheader("➕ Ajouter une dépense")
with st.form("ajout_depense"):
    col1, col2 = st.columns(2)
    datedep = col1.date_input("📅 Date", value=datetime.today())
    montant = col2.number_input("💶 Montant (€)", min_value=0.0, step=0.01)
    categorie = st.selectbox("📂 Catégorie", ["Courses", "Goodies", "Activités", "Maison", "Autres"])
    description = st.text_input("📝 Description")
    submit = st.form_submit_button("✅ Ajouter la dépense")

    if submit and montant > 0 and description.strip():
        # On enregistre la dépense dans Firestore
        db.collection("tresorerie").add({
            "annee": annee,
            "date": datedep.strftime("%Y-%m-%d"),
            "montant": float(montant),
            "categorie": categorie,
            "description": description
        })
        # Mettre à jour le solde automatiquement
        nouveau_solde = solde - float(montant)
        db.collection("tresorerie").document("solde").set({"montant": nouveau_solde})
        st.success("✅ Dépense ajoutée et solde mis à jour")
        # On invalide *seulement* le cache des fonctions Firestore
        st.cache_data.clear()

# Affichage des dépenses avec spinner
st.subheader("📊 Dépenses pour l'année " + str(annee))
with st.spinner("Récupération des dépenses…"):
    df = get_depenses_par_annee(annee)

if df.empty:
    st.warning("Aucune dépense pour cette année.")
else:
    # Convertir la colonne 'date' en datetime pour le tri
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date", ascending=False)
    # Afficher le DataFrame dans un tableau interactif
    st.dataframe(
        df[["date", "montant", "categorie", "description"]],
        use_container_width=True
    )

    # Calculer la répartition par catégorie
    repartition = df.groupby("categorie")["montant"].sum().reset_index()
    st.markdown("### Répartition par catégorie")
    st.dataframe(repartition, use_container_width=True)

    total_annee = df["montant"].sum()
    st.markdown(f"**Total annuel : {total_annee:.2f} €**")
