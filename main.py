from scraper import get_news
from ai import summarize
import pandas as pd

print("Scraping tech news...")

news = get_news()

data = []

for n in news[:10]:
    s = summarize(n)

    print("\nTITLE:", n)
    print("SUMMARY:", s)

    data.append({
        "title": n,
        "summary": s
    })

df = pd.DataFrame(data)
df.to_csv("tech_news.csv", index=False)

print("\nSaved to tech_news.csv")
