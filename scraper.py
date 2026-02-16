import feedparser

def get_news():
    url = "https://techcrunch.com/feed/"
    feed = feedparser.parse(url)

    news = []

    for entry in feed.entries[:30]:
        news.append(entry.title)

    return news
