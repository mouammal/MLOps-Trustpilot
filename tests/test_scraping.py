from src.data import scraping
import pandas as pd
import os

COMPANIES_FILE = "data/raw/companies_links.csv"

# Créer le dossier si nécessaire
os.makedirs(os.path.dirname(COMPANIES_FILE), exist_ok=True)

# Créer un CSV bidon si le fichier n'existe pas
if not os.path.exists(COMPANIES_FILE):
    df_mock = pd.DataFrame(
        {"company": ["TestCompany"], "href_company": ["http://example.com"]}
    )
    df_mock.to_csv(COMPANIES_FILE, index=False)


def test_parse_reviews_live():
    # On ne prend qu'une seule entreprise pour limiter le temps
    df_companies = pd.read_csv(COMPANIES_FILE).head(1)
    company_name = df_companies.iloc[0]["company"]
    company_url = df_companies.iloc[0]["href_company"]

    # Mock du driver pour éviter le vrai scraping
    class DummyDriver:
        def quit(self):
            pass

    driver = DummyDriver()

    # Mock de la fonction scrape_company_reviews pour retourner une liste bidon
    def mock_scrape_company_reviews(driver, company_name, company_url):
        return [
            {
                "company": company_name,
                "Id_reviews": "John Doe",
                "title_reviews": "Super produit",
                "reviews": "J'adore ce produit !",
                "score_reviews": "4",
                "published_date": "2025-08-12",
            }
        ]

    reviews = mock_scrape_company_reviews(driver, company_name, company_url)

    driver.quit()

    # Vérifications basiques
    assert isinstance(reviews, list)
    assert len(reviews) > 0, "Aucune review extraite : vérifier le sélecteur HTML"

    # Vérifications sur la première review
    first_review = reviews[0]
    assert "company" in first_review
    assert first_review["company"] == company_name
    assert "Id_reviews" in first_review
    assert "title_reviews" in first_review
    assert "reviews" in first_review
    assert "score_reviews" in first_review
    assert "published_date" in first_review


def test_save_reviews_to_csv_creates_filename(tmp_path):
    df = pd.DataFrame({"company": ["A"], "review": ["good"]})
    date_str = "2025-08-12"
    saved_filename = scraping.save_reviews_to_csv(df, date_str)
    assert saved_filename == f"data/raw/trustpilot_data_raw_{date_str}.csv"


def test_parse_reviews_empty():
    html = "<html><body>No reviews here</body></html>"
    company = "EmptyCo"
    reviews = scraping.parse_reviews(html, company)
    assert isinstance(reviews, list)
    assert len(reviews) == 0
