import streamlit as st
import pandas as pd
import plotly.express as px
import requests  # Pour télécharger les images à partir des URLs
from PIL import Image
import io

# Fonction pour charger les données
@st.cache_resource
def load_data():
    data_controls = pd.read_excel('Export des contrôles (1).xlsx')
    data_patrimoine = pd.read_excel('Patrimoine des entrées collectives OPHEA (1) (1).xlsx')
    return data_controls, data_patrimoine

# Charger les données
original_data_controls, original_data_patrimoine = load_data()

# Créer des copies des données pour éviter les mutations des objets mis en cache
data_controls = original_data_controls.copy()
data_patrimoine = original_data_patrimoine.copy()

# Dictionnaire de correspondance des mois français vers anglais
mois_fr_en = {
    "janvier": "January", "février": "February", "mars": "March",
    "avril": "April", "mai": "May", "juin": "June",
    "juillet": "July", "août": "August", "septembre": "September",
    "octobre": "October", "novembre": "November", "décembre": "December"
}

# Corriger les dates dans les données de contrôle
date_column = 'Date contrôle'
if date_column in data_controls.columns:
    for mois_fr, mois_en in mois_fr_en.items():
        data_controls[date_column] = data_controls[date_column].str.replace(mois_fr, mois_en, case=False, regex=True)
    data_controls[date_column] = pd.to_datetime(data_controls[date_column], errors='coerce')
    data_controls['Date only'] = data_controls[date_column].dt.date
    data_controls['Year-Week'] = data_controls[date_column].dt.to_period('W')
    data_controls['Year-Month'] = data_controls[date_column].dt.to_period('M')

# Exclure les colonnes non pertinentes
columns_to_exclude = [
    "Date contrôle", "Numéro rue", "Rue", "CP", "Ville", "Secteur", "Agence",
    "Nom de résidence", "Gardien ou prestataire", "Responsable de secteur",
    "Type de contrôle :", "Météo au moment du contrôle :"
] + [
    col for col in data_controls.columns if "commentaire" in col.lower() or "document" in col.lower()
]
available_columns = [col for col in data_controls.columns if col not in columns_to_exclude]


# Sidebar for navigation
analysis_type = st.sidebar.selectbox(
    "Choisissez le type d'analyse",
    ["Accueil", "Diagrammes interactifs"]
)

if analysis_type == "Accueil": 
    st.image("Blue and White Modern Innovation in Renewable Energy Presentation.jpg")
    st.header("Contexte") 
    st.write("Les inspections ont été initiées en réponse aux enquêtes de satisfaction des locataires et aux doléances émises par leurs représentants. La direction et la gouvernance ont souhaité obtenir des données objectives et détaillées pour guider leurs décisions d’amélioration. Ces inspections se sont concentrées sur plusieurs aspects essentiels à la qualité de vie des locataires.")
    st.subheader("Méthodologie")
    st.write("""Les inspections ont été menées de manière méthodique sur un large échantillon de bâtiments. Chaque inspection a couvert les axes suivants :
             
**Sécurité** : présence de plans d’évacuation, registres de sécurité, et bon fonctionnement des équipements de sécurité (extincteurs, BAES).
             
**Propreté et vétusté** : état des halls d’entrée, paliers, ascenseurs, caves, locaux poubelles, et extérieurs des bâtiments.
             
**Fonctionnalité des équipements** : portes d’entrée, ascenseurs, éclairage et autres infrastructures critiques.""")

elif analysis_type == "Diagrammes interactifs":
    st.header("Diagrammes interactifs")

    # Sélection d'une colonne pour l'analyse
    response_column = st.selectbox("Choisissez une colonne pour l'analyse", available_columns)

    # Fonction pour afficher le graphique camembert
    def camembert_plot(column):
        data_counts = data_controls[column].value_counts()
        df = pd.DataFrame({'Réponse': data_counts.index, 'Nombre': data_counts.values})
        fig = px.pie(
            df,
            names='Réponse',
            values='Nombre',
            title=f"Répartition des réponses pour {column}",
            hole=0.3
        )
        fig.update_traces(
            textinfo='label+percent+value',
            textposition='outside',
            pull=[0, 0.2]
        )
        st.plotly_chart(fig)

    # Diagramme en camembert
    camembert_plot(response_column)

    # Fonction pour créer des diagrammes en barres empilées interactifs
    def interactive_stacked_bar_chart(group_by_column, title):
        grouped_data = data_controls.groupby([group_by_column, response_column]).size().reset_index(name='Nombre')
        fig = px.bar(
            grouped_data,
            x=group_by_column,
            y='Nombre',
            color=response_column,
            title=title,
            barmode='stack',
            text='Nombre'
        )
        fig.update_traces(texttemplate='%{text}', textposition='outside')
        fig.update_layout(xaxis_title=group_by_column, yaxis_title="Nombre de contrôles", uniformtext_minsize=8)
        st.plotly_chart(fig)

    # Diagramme par Secteur
    if 'Secteur' in data_controls.columns:
        interactive_stacked_bar_chart('Secteur', f"Répartition par Secteur ({response_column})")

    # Diagramme par Date Only
    if 'Date only' in data_controls.columns:
        interactive_stacked_bar_chart('Date only', f"Répartition par Date ({response_column})")
    # Diagramme par Year-Week
    if 'Year-Week' in data_controls.columns:
        # Convertir en chaîne pour un affichage correct dans les graphiques
        data_controls['Year-Week'] = data_controls['Year-Week'].astype(str)
        interactive_stacked_bar_chart('Year-Week', f"Répartition par Semaine ({response_column})")

    # Diagramme par Year-Month
    if 'Year-Month' in data_controls.columns:
        # Convertir en chaîne pour un affichage correct dans les graphiques
        data_controls['Year-Month'] = data_controls['Year-Month'].astype(str)
        interactive_stacked_bar_chart('Year-Month', f"Répartition par Mois ({response_column})")

      # Vérifier s'il existe une colonne "Document" pour la colonne sélectionnée
    
    document_column = f"{response_column}\nDocuments"
    if document_column in data_controls.columns:
        st.write(f"### Images associées à la colonne : {document_column}")

        # Liste des chemins d'images valides (sans valeurs nulles et sans chemins commençant par "-")
        valid_image_paths = [file_path[1:] for file_path in data_controls[document_column].dropna() if file_path[0] != "-"]

        # Parcourir les chemins par groupes de 4 pour l'affichage côte à côte
        for i in range(0, len(valid_image_paths), 4):  # Traiter les chemins 4 par 4
            cols = st.columns(4)  # Créer 4 colonnes côte à côte
            for j, clean_file_path in enumerate(valid_image_paths[i:i + 4]):
                try:
                    # Trouver la ligne correspondante dans le dataframe
                    row = data_controls[data_controls[document_column] == "•"+clean_file_path]

                    # Vérifier si c'est une URL valide
                    if clean_file_path.startswith("http"):
                        # Télécharger l'image depuis l'URL
                        response = requests.get(clean_file_path)
                        response.raise_for_status()  # Vérifier les erreurs HTTP

                        # Charger l'image à partir des données binaires
                        image = Image.open(io.BytesIO(response.content))
                    else:
                        # Si ce n'est pas une URL, charger comme fichier local
                        image = Image.open(clean_file_path)

                    # Afficher l'image dans la colonne correspondante
                    cols[j].image(image, use_column_width=True)

                    # Afficher les informations associées sous l'image
                    cols[j].write(f"**Date contrôle** : {row['Date contrôle'].iloc[0]}")
                    cols[j].write(f"**Numéro rue** : {row['Rue'].iloc[0]}")
                    cols[j].write(f"**CP** : {row['CP'].iloc[0]}")
                    cols[j].write(f"**Ville** : {row['Ville'].iloc[0]}")
                    cols[j].write(f"**Secteur** : {row['Secteur'].iloc[0]}")
                except Exception as e:
                    pass

