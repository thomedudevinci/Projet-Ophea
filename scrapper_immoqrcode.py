from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time

# Initialisation du navigateur
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# URL de la page à scraper
url = "https://immoqrcodes.org/admin-panel/"  # Remplacez par votre URL
driver.get(url)

# Pause pour laisser le contenu se charger
time.sleep(5)

# Étape 1 : Authentification
try:
    driver.find_element(By.NAME, "mail").send_keys("contact@qsbail.com")  # Email
    driver.find_element(By.NAME, "mdp").send_keys("Nicoines54!?")  # Mot de passe
    driver.find_element(By.NAME, "connexion").click()  # Bouton de connexion
    time.sleep(5)  # Pause pour laisser la page se charger
    print("Connexion réussie.")
except Exception as e:
    print("Erreur lors de la connexion :", e)
    driver.quit()
    exit()

# Étape 2 : Accéder à "Formulaires existants"
try:
    driver.find_element(By.XPATH, "//a[@href='formulaire.crees.php']").click()
    time.sleep(3)
except Exception as e:
    print("Erreur lors du clic sur 'Formulaires existants' :", e)
    driver.quit()
    exit()

# Étape 3 : Accéder à "Photos des questions répondues"
try:
    driver.find_element(By.XPATH, "//a[contains(@href, 'formulaire.photos.php') and contains(@title, 'Photos des questions répondues')]").click()
    time.sleep(3)
except Exception as e:
    print("Erreur lors du clic sur 'Photos' :", e)
    driver.quit()
    exit()

# Étape 4 : Traitement des divs pour collecter toutes les photos
results = []  # Liste pour stocker les résultats

try:
    div_index = 0  # Initialiser l'index
    while True:
        # Rechercher les divs dynamiquement à chaque itération
        divs = driver.find_elements(By.CLASS_NAME, "image_gallery.cadre.flex.flex_center.align_items_center.flex_column.width300")
        if div_index >= len(divs):  # Si l'index dépasse la liste actuelle, terminer la boucle
            break

        try:
            div = divs[div_index]  # Sélectionner la div actuelle

            # Rechercher le bouton "btn" et cliquer dessus
            link = div.find_element(By.CLASS_NAME, "btn")
            href = link.get_attribute("href")
            print(f"Traitement de l'élément {div_index + 1} : {href}")
            link.click()

            # Pause pour laisser la page se charger
            time.sleep(3)

            # Rechercher et récupérer le texte du <h2> (question)
            try:
                h2_text = driver.find_element(By.CSS_SELECTOR, "#contenu h2").text
            except Exception:
                h2_text = "Non spécifié"

            # Rechercher toutes les photos sur cette page
            try:
                photo_divs = driver.find_elements(By.CLASS_NAME, "image_gallery.cadre.flex.flex_center.align_items_center.flex_column.width300")
                for photo_div in photo_divs:
                    # Récupérer le lien href de chaque photo
                    try:
                        photo_link = photo_div.find_element(By.TAG_NAME, "a").get_attribute("href")
                    except Exception:
                        photo_link = "Non spécifié"

                    # Récupérer l'adresse associée à chaque photo
                    try:
                        badge_text = photo_div.find_element(By.CLASS_NAME, "badge.margintop10").text
                    except Exception:
                        badge_text = "Non spécifié"

                    # Ajouter les informations dans les résultats
                    results.append({
                        "Question": h2_text,
                        "Image": photo_link,
                        "Adresse": badge_text
                    })

            except Exception as e:
                print(f"Erreur lors de la récupération des photos sur la page pour l'élément {div_index + 1} :", e)

            # Revenir en arrière après avoir collecté toutes les photos
            driver.back()
            time.sleep(3)

        except Exception as e:
            print(f"Erreur avec la div {div_index + 1} :", e)

        # Incrémenter l'index pour passer à la prochaine div
        div_index += 1

except Exception as e:
    print("Erreur générale lors de la récupération des divs :", e)

# Étape 5 : Fermer le navigateur
driver.quit()

# Étape 6 : Sauvegarder les résultats dans un fichier Excel
df = pd.DataFrame(results)
df.to_excel("resultats_scraping.xlsx", index=False)
print("Les résultats ont été enregistrés dans 'resultats_scraping.xlsx'")
