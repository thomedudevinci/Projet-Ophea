import streamlit as st
import pandas as pd
import plotly.express as px
import requests  # Pour télécharger les images à partir des URLs
from PIL import Image
import io

# Fonction pour charger les données
@st.cache_resource
def load_data():
    data_controls = pd.read_excel('Export.xlsx')
    data_patrimoine = pd.read_excel('Patrimoine des entrées collectives OPHEA (1) (1).xlsx')
    data_scraped=pd.read_excel("resultats_scraping.xlsx")
    return data_controls, data_patrimoine, data_scraped

# Charger les données
original_data_controls, original_data_patrimoine, original_data_scraped = load_data()

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
    ["Accueil","Détail","Diagrammes interactifs","Conclusion"]
)

if analysis_type == "Accueil": 

    # Image principale
    st.image("Blue and White Modern Innovation in Renewable Energy Presentation.jpg")

    # Titre principal
    st.header("Contexte et chiffres clés")
    st.markdown("""
    Les inspections ont été initiées en réponse aux enquêtes de satisfaction des locataires et aux doléances émises par leurs représentants.  
    La direction et la gouvernance ont souhaité obtenir des données objectives et détaillées pour guider leurs décisions d’amélioration.  
    Ces inspections se sont concentrées sur plusieurs aspects essentiels à la qualité de vie des locataires.
    """)

    # Sous-titre méthodologie
    st.subheader("Méthodologie")
    st.markdown("""
    Les inspections ont été menées de manière méthodique sur un large échantillon de bâtiments. Chaque inspection a couvert les axes suivants :

    - **Sécurité** : Présence de plans d’évacuation, registres de sécurité, et bon fonctionnement des équipements de sécurité (extincteurs, BAES).
    - **Propreté et vétusté** : État des halls d’entrée, paliers, ascenseurs, caves, locaux poubelles, et extérieurs des bâtiments.
    - **Fonctionnalité des équipements** : Portes d’entrée, ascenseurs, éclairage et autres infrastructures critiques.

    Les résultats ont été recueillis avec **ImmoQRcode**, permettant un reporting précis avec des statistiques exploitables et des photos à l’appui.  
    Développé par QSBail, **ImmoQRcode** est un logiciel innovant permettant un contrôle efficace et rapide du patrimoine, avec la possibilité de prendre des photos comme preuve des interventions réalisées.  
    **Lien vers le formulaire** : [ImmoQRcode](https://immoqrcodes.org/form/1)
    """)

    # Chiffres clés
    st.subheader("Chiffres clés")
    st.markdown("""
    - **1319 entrées contrôlées**.
    - **8 contrôleurs** mobilisés.
    - **21 jours de contrôles**.
    - **212 heures au total** (hors trajets d’un site à l’autre).
    - **Nombre de fissures détectées** : 112.
    - **Nombre de risques de chute détectés** : 157.
    - **Nombre de traces de squat** : 65.
    - **Balcons nécessitant une attention particulière** : 207 problèmes visibles.
    - **Ampoules hors service signalées** : 102.

    ### Encombrants signalés :
    - **Bourse** : 77.
    - **Centre Ville** : 13.
    - **Forêt Noire** : 43.
    - **Neudorf** : 6.
    - **Orphelinat-Polygone** : 56.
    - **Port du Rhin** : 51.
    - **Quartier Suisse** : 8.

    ### Secteurs les plus problématiques :
    - **Bourse** : 45 fissures, 48 risques de chute, et 207 problèmes aux balcons.
    - **Forêt Noire** : 145 problèmes aux balcons et 38 risques de chute.

    Ces chiffres montrent que la distinction entre **vétusté** et **propreté** est essentielle pour analyser précisément les besoins d’entretien et répondre aux attentes des locataires.
    """)

    # Distinguer propreté et vétusté
    st.subheader("Distinction entre propreté et vétusté")
    st.markdown("""
    - **Propreté** : Problèmes liés à l’entretien courant (saleté, encombrants, dégradations récentes).
    - **Vétusté** : Usure due au temps (peinture défraîchie, fissures, éclairages obsolètes).

    Cette confusion entre propreté et vétusté contribue parfois à une perception négative, car les locataires attendent des parties communes impeccables, d’autant plus qu’ils paient des charges pour leur entretien.
    """)


elif analysis_type == "Diagrammes interactifs":
    st.header("Diagrammes interactifs")

    # Sélection d'une colonne pour l'analyse
    response_column = st.selectbox("Choisissez une colonne pour l'analyse", available_columns)
    if response_column in ["Préconisations :\nAvis global","Que faudrait-il faire pour améliorer cette entrée ?\nAvis global","Préconisations :\nAvis global","Prenez une photo de l'extérieur du bâtiment et veuillez confirmer\nAvis global"]+[col for col in data_controls.columns if "nombre d’ampoule hs ?" in col.lower()]:
        st.table(data_controls[response_column].value_counts()) 
    elif len(data_controls[response_column]>6 :
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


        document_column = f"{response_column}\nDocuments"
        # Vérifier s'il existe une colonne "Document" pour la colonne sélectionnée
        if response_column.split("\n")[0] in original_data_scraped["Question"].unique():
            df_question=original_data_scraped[original_data_scraped["Question"]==response_column.split("\n")[0]]
            for i in range(0,len(df_question),4):
                cols = st.columns(4)
                for j, clean_file_path in enumerate(df_question["Image"][i:i + 4]):
                    try:
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
                        row = df_question[df_question["Image"] == clean_file_path]
                        cols[j].write(f"**Adresse** : {row['Adresse'].iloc[0]}")
                    except Exception as e:
                        pass

        elif document_column in data_controls.columns:
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

elif analysis_type == "Détail":
    
    # Titre principal
    st.title("Détail")
    st.image("Détail.png")

    # Introduction
    st.write("")
    st.markdown("""
    **Indiquer si le temps était sec ou pluvieux lors des contrôles est crucial pour plusieurs raisons pratiques et analytiques :**
    """)

    # Première section
    st.subheader("1. Impact direct sur les observations")
    st.markdown("""
    - **État des sols et des abords** : La pluie peut accentuer la saleté visible, rendre les sols glissants ou montrer des problèmes de drainage (flaques d’eau, infiltrations).
    - **Encombrants** : Les objets laissés à l’extérieur peuvent paraître plus dégradés ou encombrants sous la pluie.
    - **Façades et plafonds** : Des fissures ou des infiltrations ne sont parfois visibles qu’en cas de pluie, révélant des problèmes structurels.
    """)

    st.subheader("2. Justification des anomalies observées")
    st.markdown("""
    - **Conditions météorologiques** : Si un contrôle est réalisé après une période de pluie, certaines observations (déchets mouillés, boue) pourraient être temporaires et dues à la météo.
    - **Accusations injustes** : Cela permet d’éviter que les équipes soient accusées de négligence pour des problèmes directement liés aux conditions climatiques.
    """)

    st.subheader("3. Perception des locataires")
    st.markdown("""
    - Les locataires sont plus susceptibles de remarquer les problèmes de propreté ou de vétusté immédiatement après des conditions pluvieuses.
    - En indiquant les conditions lors des contrôles, cela peut contextualiser les observations et éviter des interprétations biaisées.
    """)

    st.write("---")

    # Section supplémentaire
    st.subheader("Explication du mécontentement des locataires")
    st.markdown("""
    - **Impact psychologique** : Les espaces mal entretenus ou encombrés donnent une impression de négligence, nuisant au sentiment d'appartenance.
    - **Insécurité perçue** : Le manque de propreté, combiné à un éclairage insuffisant, alimente le sentiment d’insécurité.
    - **Manque de confiance envers la gestion** : Les anomalies perçues comme un désintérêt fragilisent la satisfaction.
    """)

    # Grille de contrôle
    st.subheader("Définition et grille de contrôle : distinguer propreté et vétusté")
    st.markdown("""
    Pour clarifier, voici une grille par organe à contrôler, distinguant **propreté** et **vétusté** :
    - **Propreté** : État observable (déchets, saleté, etc.).
    - **Vétusté** : Usure due au temps ou à l’absence de rénovation.
    """)

    st.write("---")

    # Partie psychologique
    st.subheader("Perception psychologique et satisfaction des locataires")
    st.markdown("""
    - **Théorie des "vitres brisées"** : Les signes visibles de négligence favorisent un sentiment d’impunité et encouragent d’autres dégradations.
    - **Mémoire sélective** : Les locataires se rappellent davantage des moments où l’environnement est négligé, amplifiant leur insatisfaction.
    """)

    # Efforts des équipes
    st.subheader("Impact sur les équipes")
    st.markdown("""
    - Les agents de proximité subissent frustration et usure morale face à des efforts souvent invisibles pour les locataires.
    - Importance de reconnaître et valoriser leur travail.
    """)

    # Actions recommandées
    st.subheader("Sensibilisation et actions structurelles")
    st.markdown("""
    - **Sensibiliser les locataires** : Éducation aux coûts liés aux incivilités et à l’entretien des parties communes.
    - **Renforcer la surveillance** : Caméras, médiateurs de quartier.
    - **Impliquer les locataires** : Chantiers participatifs, projets de rénovation collective.
    - **Réaliser un audit externe** : Un regard extérieur pour identifier les problèmes invisibles au quotidien.
    """)

elif analysis_type=="Conclusion":
    # Titre de la section
    st.title("Conclusion : Agir avec conviction, sans sur-réagir")

    # Contenu principal
    st.markdown("""
    ### Ne pas sur-réagir :
    - Les incivilités et dégradations sont le symptôme d’une problématique sociale plus large.

    ### Agir durablement :
    - Continuer les efforts de sensibilisation.
    - Rénover les infrastructures et valoriser le travail des équipes.
    - Soutenir les équipes face à une tâche souvent ingrate.

    ### Objectif :
    Avec cette approche, il est possible de :
    - Redonner aux locataires le sentiment d’habiter un lieu digne et sécurisant.
    - Reconstruire une relation de confiance entre les locataires et l’organisme de gestion.
    """)

    # Ligne de séparation
    st.write("---")

    # Accès à l'application
    st.subheader("Consulter les résultats dans le détail")
    st.markdown("""
    - **Accéder à l’application** : [Ophea Analytics](https://projet-ophea-analytics.streamlit.app/)
    - **Identifiants de connexion :**
        - **Adresse e-mail** : `contact@alloecogestes.org`
        - **Mot de passe** : `prJ_e(#_tuo}`
    """)


