from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time
import platform
import os


# === SETUP DRIVER ===
def setup_driver():
    options = Options()
    options.add_argument(
        "--headless=new"
    )  # Décommente pour exécution sans interface graphique
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")

    system = platform.system()

    if system == "Windows":
        # Sur Windows, utiliser webdriver-manager pour télécharger automatiquement
        driver_path = ChromeDriverManager().install()
    else:
        # Sur Linux/Docker Airflow
        if os.path.exists("/usr/bin/chromedriver"):
            # Utiliser le driver système installé via apt
            driver_path = "/usr/bin/chromedriver"
        else:
            raise FileNotFoundError("Chromedriver introuvable sur le système Linux.")

    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=options)
    return driver


# === INTERACTIONS PAGE ===
def accept_cookies(driver):
    try:
        accept_button = WebDriverWait(driver, 0.2).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(text(), 'Accepter tous les cookies')]")
            )
        )
        accept_button.click()
        time.sleep(0.1)
    except Exception:
        pass


def click_see_all_reviews(driver):
    try:
        see_all_button = WebDriverWait(driver, 0.2).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//span[contains(text(), 'Voir tous les avis')]")
            )
        )
        driver.execute_script("arguments[0].click();", see_all_button)
        time.sleep(0.1)
    except Exception as e:
        print(f"Le bouton 'Voir tous les avis' n'a pas été trouvé : {e}")


# === PARSING ===
def parse_reviews(html, company):
    soup = BeautifulSoup(html, "html.parser")
    reviews = []
    cards = soup.find_all("div", class_="styles_cardWrapper__g8amG styles_show__Z8n7u")

    for card in cards[:5]:  # Limite à 5 avis par entreprise
        try:
            review = {
                "company": company,
                "Id_reviews": (
                    card.find(
                        "span", {"data-consumer-name-typography": True}
                    ).text.strip()
                    if card.find("span", {"data-consumer-name-typography": True})
                    else None
                ),
                "title_reviews": (
                    card.find(
                        "h2",
                        class_="CDS_Typography_appearance-default__dd9b51 CDS_Typography_prettyStyle__dd9b51 CDS_Typography_heading-xs__dd9b51",
                    ).text.strip()
                    if card.find(
                        "h2",
                        class_="CDS_Typography_appearance-default__dd9b51 CDS_Typography_prettyStyle__dd9b51 CDS_Typography_heading-xs__dd9b51",
                    )
                    else None
                ),
                # CDS_Typography_appearance-default__dd9b51 CDS_Typography_prettyStyle__dd9b51 CDS_Typography_heading-xs__dd9b51
                "reviews": (
                    card.find(
                        "p",
                        class_="CDS_Typography_appearance-default__dd9b51 CDS_Typography_prettyStyle__dd9b51 CDS_Typography_body-l__dd9b51",
                    ).text.strip()
                    if card.find(
                        "p",
                        class_="CDS_Typography_appearance-default__dd9b51 CDS_Typography_prettyStyle__dd9b51 CDS_Typography_body-l__dd9b51",
                    )
                    else None
                ),
                "score_reviews": (
                    card.find("div", {"data-service-review-rating": True}).get(
                        "data-service-review-rating"
                    )
                    if card.find("div", {"data-service-review-rating": True})
                    else None
                ),
                "published_date": (
                    card.find("time").get("datetime") if card.find("time") else None
                ),
            }
            reviews.append(review)
        except Exception as e:
            print(f"Erreur lors de l'extraction d'un avis: {e}")
            continue

    return reviews


# === SCRAPE COMPANY ===
def scrape_company_reviews(driver, company, url):
    try:
        driver.get(url)
        accept_cookies(driver)

        if "404" in driver.title or "Page non trouvée" in driver.page_source:
            print(f"Page non trouvée pour {url}")
            return []

        click_see_all_reviews(driver)
        html = driver.page_source
        return parse_reviews(html, company)

    except Exception as e:
        print(f"Erreur pour {company} : {e}")
        return []


# === ENREGISTRER LE CSV ===
def save_reviews_to_csv(df, date_str):
    filename = f"data/raw/trustpilot_data_raw_{date_str}.csv"
    df.to_csv(filename, index=False)
    return filename


# === PIPELINE PRINCIPAL ===
def run_scraping_pipeline(df_companies):
    all_reviews = []
    driver = setup_driver()
    print("\n[PIPELINE SCRAPING] Démarrage du scraping des avis Trustpilot")

    for _, row in df_companies.iterrows():
        company = row["company"]
        url = row["href_company"]
        print(f"Scraping de {company} ({url})")

        reviews = scrape_company_reviews(driver, company, url)

        if reviews:
            print(f"{len(reviews)} avis récupérés pour {company}")
            all_reviews.extend(reviews)
        else:
            print(f"Aucun avis récupéré pour {company}")

    driver.quit()

    df_reviews = pd.DataFrame(all_reviews)
    trustpilot_raw_df = pd.merge(df_companies, df_reviews, on="company", how="inner")
    trustpilot_raw_df = trustpilot_raw_df.drop(
        columns=["href_company", "sub_category", "website"], errors="ignore"
    )

    today = datetime.now().strftime("%Y-%m-%d")
    filename = save_reviews_to_csv(trustpilot_raw_df, today)

    total_reviews = len(df_reviews)
    total_companies = len(df_companies)
    error_rate = 1 - (total_reviews / (5 * total_companies)) if total_companies else 0

    print(f"\n[PIPELINE SCRAPING] Terminé : {total_reviews} avis extraits.")
    return trustpilot_raw_df, filename, total_reviews, error_rate


# === LANCEMENT DU SCRIPT ===
if __name__ == "__main__":

    nb_company = 5
    df = pd.read_csv("data/raw/companies_links.csv").head(nb_company)
    print(f"Taille de Companies_links.csv : {df.shape}")

    raw_df, raw_filename, total_reviews, error_rate = run_scraping_pipeline(
        df_companies=df
    )
    print(raw_df["title_reviews"])
