import pandas as pd

df1 = pd.read_csv("data/raw/companies_links.csv")

print(df1.columns)
print(df1["reviews"])
print(df1["title_reviews"])
