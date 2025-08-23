from src.data import scraping

def test_parse_reviews_simple():
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
    assert review['published_date'] == "2025-08-12"


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