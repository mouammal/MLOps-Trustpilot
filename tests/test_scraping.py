from src.data import scraping
import pandas as pd 

""" def test_parse_reviews_simple():
    # HTML minimal simulé avec 1 avis
    html = '''
    <div class="styles_cardWrapper__g8amG styles_show__Z8n7u">
        <span data-consumer-name-typography="true">John Doe</span>
        <h2 class="typography_heading-xs__osRhC typography_appearance-default__t8iAq">Super produit</h2>
        <p class="typography_body-l__v5JLj typography_appearance-default__t8iAq">J'adore ce produit !</p>
        <div data-service-review-rating="4"></div>
        <time datetime="2025-08-12"></time>
    </div>
    '''
    company = "TestCompany"
    reviews = scraping.parse_reviews(html, company)

    assert isinstance(reviews, list)
    assert len(reviews) == 1
    review = reviews[0]
    assert review['company'] == company
    assert review['Id_reviews'] == "John Doe"
    assert review['title_reviews'] == "Super produit"
    assert review['reviews'] == "J'adore ce produit !"
    assert review['score_reviews'] == "4"
    assert review['published_date'] == "2025-08-12" """


def test_parse_reviews_live():
    # On ne prend qu'une seule entreprise pour limiter le temps
    df_companies = pd.read_csv("data/raw/companies_links.csv").head(1)
    company_name = df_companies.iloc[0]["company"]
    company_url = df_companies.iloc[0]["href_company"]

    # Initialisation du driver
    driver = scraping.setup_driver()

    # Scraper les reviews réelles
    reviews = scraping.scrape_company_reviews(driver, company_name, company_url)

    # Fermeture du driver
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
    import pandas as pd
    df = pd.DataFrame({
        'company': ['A'],
        'review': ['good']
    })
    date_str = "2025-08-12"
    saved_filename = scraping.save_reviews_to_csv(df, date_str)
    assert saved_filename == f"data/raw/trustpilot_data_raw_{date_str}.csv"


def test_parse_reviews_empty():
    html = "<html><body>No reviews here</body></html>"
    company = "EmptyCo"
    reviews = scraping.parse_reviews(html, company)
    assert isinstance(reviews, list)
    assert len(reviews) == 0