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
    "Type de contrôle :", "Météo au moment du contrôle :","Date only","Year-Week","Year-Month","Prenez une photo de l'extérieur du bâtiment et veuillez confirmer\nAvis global"
    

] + [
    col for col in data_controls.columns if "commentaire" in col.lower() or "document" in col.lower()
] 
available_columns = [col for col in data_controls.columns if col not in columns_to_exclude]


# Sidebar for navigation
analysis_type = st.sidebar.selectbox(
    "Menu",
    ["Accueil", "Diagrammes interactifs"]
)

if analysis_type == "Accueil": 
    st.image("Blue and White Modern Innovation in Renewable Energy Presentation.jpg")
    st.header("Contexte et chiffres clés") 
    st.write("Les inspections ont été initiées en réponse aux enquêtes de satisfaction des locataires et aux doléances émises par leurs représentants. La direction et la gouvernance ont souhaité obtenir des données objectives et détaillées pour guider leurs décisions d’amélioration. Ces inspections se sont concentrées sur plusieurs aspects essentiels à la qualité de vie des locataires.")
    st.subheader("Méthodologie")
    st.write("""Les inspections ont été menées de manière méthodique sur un large échantillon de bâtiments. Chaque inspection a couvert les axes suivants :
             
**Sécurité** : présence de plans d’évacuation, registres de sécurité, et bon fonctionnement des équipements de sécurité (extincteurs, BAES).
             
**Propreté et vétusté** : état des halls d’entrée, paliers, ascenseurs, caves, locaux poubelles, et extérieurs des bâtiments.
             
**Fonctionnalité des équipements** : portes d’entrée, ascenseurs, éclairage et autres infrastructures critiques.

Les résultats ont été recueillis avec ImmoQRcode, permettant un reporting précis, avec des statistiques exploitables et des photos à l’appui.
Développé par QSBail, ImmoQRcode est un logiciel innovant permettant un contrôle efficace et rapide du patrimoine, avec la possibilité de prendre des photos comme preuve des interventions réalisées.  Lien vers le formulaire : https://immoqrcodes.org/form/1


 	17 861 cas de vétusté ont été relevés, représentant des anomalies structurelles liées à l’usure naturelle du bâti (murs, sols, plafonds, balcons, …)
 	1319 entrées contrôlées 
 	8 contrôleurs 
 	21 jours de contrôles 
 	212 heures au total (hors trajets d’un site à l’autre)
 	Nombre de fissures détectées : 112
 	Nombre de problèmes visibles sur les balcons : 0
 	Nombre de risques de chute détectés : 157
 	Nombre de traces de squat : 65
 	Les balcons nécessitent une attention particulière avec 207 problèmes visibles.
 	Au total, 102 ampoules hors service ont été signalées sur l'ensemble des contrôles.
             
 	Au total, 255 encombrants ont été signalés sur l'ensemble des contrôles, que ce soit aux abords des entrées ou dans les halls :
    •	BOURSE : 77
    •	CENTRE VILLE : 13
    •	FORET NOIRE : 43
    •	NEUDORF ; 6
    •	ORPHELINAT-POLYGONE : 56 
    •	PORT DU RHIN : 51
    •	QUARTIER SUISSE : 8

    Secteurs les plus problématiques :
    •	Bourse  : 45 fissures, 48 risques de chute, et 207 problèmes aux balcons.
    •	Foret Noire : 145 problèmes aux balcons et 38 risques de chute.

Ces chiffres clés montrent que la distinction entre vétusté et propreté est essentielle pour analyser précisément les besoins d’entretien et répondre aux attentes des locataires.

**Propreté** : Problèmes liés à l’entretien courant (saleté, encombrants, dégradations récentes).
             
**Vétusté** : Usure due au temps (peinture défraîchie, fissures, éclairages obsolètes).

Cette confusion entre propreté et vétusté contribue parfois à une perception négative, car les locataires attendent des parties communes impeccables, d’autant plus qu’ils paient des charges pour leur entretien.

             """)

elif analysis_type == "Diagrammes interactifs":
    st.header("Diagrammes interactifs")

    # Sélection d'une colonne pour l'analyse
    response_column = st.selectbox("Choisissez une colonne pour l'analyse", available_columns)
    if response_column in ["Préconisations :\nAvis global","Que faudrait-il faire pour améliorer cette entrée ?\nAvis global","Préconisations :\nAvis global","Prenez une photo de l'extérieur du bâtiment et veuillez confirmer\nAvis global"]+[col for col in data_controls.columns if "nombre d’ampoule hs ?" in col.lower()]:
        st.table(data_controls[response_column].value_counts()) 
    else:

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
        
        #Diagramme par Ensemble
        if 'B' in data_controls.columns:
            interactive_stacked_bar_chart('Secteur', f"Répartition par Secteur ({response_column})")

        # Diagramme par Year-Week
        if 'Year-Week' in data_controls.columns:
            # Convertir en chaîne pour un affichage correct dans les graphiques
            data_controls['Year-Week'] = data_controls['Year-Week'].astype(str)
            interactive_stacked_bar_chart('Year-Week', f"Répartition par Semaine ({response_column})")


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

