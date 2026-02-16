import feedparser
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from transformers import pipeline
import re
from datetime import datetime, timedelta

# Load models once
model = SentenceTransformer('all-mpnet-base-v2')
sentiment_model = pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment")
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

event_labels = [
    "layoffs", "funding", "product launch", "acquisition", "partnership", "regulation", "ai innovation",
    "cybersecurity", "startup news", "tech mergers", "policy changes", "breakthroughs", "market trends",
    "microsoft news", "general tech updates", "google news"
]

# 🧠 Intelligence Layer (Enhanced with Relevance and Latest Indicator)
def enrich_with_ai(news_item, query=""):
    text = news_item["title"] + " " + news_item["summary"]
    text = text[:512]

    sentiment = sentiment_model(text)[0]
    sentiment_label = sentiment["label"]
    sentiment_score = round(sentiment["score"], 2)

    classification = classifier(text, candidate_labels=event_labels)
    top_event = classification["labels"][0]
    event_score = round(classification["scores"][0], 2)

    relevance = calculate_relevance(news_item, query)
    is_latest = check_if_latest(news_item)

    news_item["sentiment"] = f"{sentiment_label} ({sentiment_score})"
    news_item["event_type"] = f"{top_event} ({event_score})"
    news_item["relevance"] = round(relevance, 2)
    news_item["is_latest"] = is_latest

    return news_item

# New: Calculate Relevance with Balanced Boost
def calculate_relevance(news_item, query):
    if not query:
        return 0.0
    text = (news_item["title"] + " " + news_item["summary"]).lower()
    query_words = set(re.findall(r'\b\w+\b', query.lower()))
    keyword_matches = sum(1 for word in query_words if word in text)
    # Balanced boost for title matches or key terms like "google"
    boost = 1.5 if any(word in news_item["title"].lower() for word in query_words) else 1.0
    if "google" in query.lower() and "google" in text:
        boost *= 1.5  # Moderate boost for "google"
    if "latest" in query.lower() or "news" in query.lower():
        try:
            pub_date = datetime.strptime(news_item["date"], "%a, %d %b %Y %H:%M:%S %z")
            if pub_date > datetime.now() - timedelta(days=1):  # Boost very recent
                boost *= 1.2
        except:
            pass
    return keyword_matches * boost

# New: Check if Latest (within 24 hours)
def check_if_latest(news_item):
    try:
        pub_date = datetime.strptime(news_item["date"], "%a, %d %b %Y %H:%M:%S %z")
        return pub_date > datetime.now() - timedelta(hours=24)
    except:
        return False

# 🔴 Fetch Live News (Expanded with Google Feeds and Safe Image/Source Handling)
def get_live_news():
    feeds = [
        "https://techcrunch.com/feed/",
        "https://www.theverge.com/rss/index.xml",
        "https://www.wired.com/feed/rss",
        "https://feeds.arstechnica.com/arstechnica/index",
        "https://www.reuters.com/rssfeeds/technologyNews",
        "https://feeds.feedburner.com/venturebeat/SZYF",
        "https://www.bloomberg.com/feeds/technology.rss",
        "https://rss.cnn.com/rss/edition_technology.rss",
        "https://feeds.feedburner.com/MicrosoftResearch",
        "https://www.zdnet.com/news/rss.xml",
        "https://news.microsoft.com/feed/",
        "https://news.google.com/rss",  # General Google News
        "https://www.androidpolice.com/feed/",  # Google/Android focus
        "https://searchengineland.com/feed/"  # Google search focus
    ]

    news_list = []
    seen_titles = set()

    for feed_url in feeds:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:20]:
                title = getattr(entry, 'title', 'No Title')
                if title not in seen_titles and title != 'No Title':
                    seen_titles.add(title)
                    # Safe image extraction
                    image_url = None
                    if hasattr(entry, 'media_content') and entry.media_content:
                        image_url = entry.media_content[0].get('url')
                    elif hasattr(entry, 'enclosures') and entry.enclosures:
                        for enc in entry.enclosures:
                            if enc.get('type', '').startswith('image'):
                                image_url = enc.get('url')
                                break
                    if not image_url:
                        image_url = "https://via.placeholder.com/300x200?text=No+Image"
                    
                    news_list.append({
                        "title": title,
                        "summary": getattr(entry, 'summary', ''),
                        "date": getattr(entry, 'published', 'No date'),
                        "url": getattr(entry, 'link', ''),
                        "image": image_url,
                        "source": feed_url.split('/')[2] if '/' in feed_url else 'Unknown'
                    })
        except Exception as e:
            print(f"Error fetching {feed_url}: {e}")

    return news_list

# 🔴 Semantic Search (Enhanced with Strict Filtering)
def semantic_search(news_data, query):
    query = query.strip()
    if not query or len(query) < 2:
        results = news_data[:10]
    else:
        texts = [n["title"] + " " + n["summary"] for n in news_data]
        news_embeddings = model.encode(texts)
        query_embedding = model.encode([query])
        scores = cosine_similarity(query_embedding, news_embeddings)[0]

        combined_scores = []
        for i, item in enumerate(news_data):
            rel = calculate_relevance(item, query)
            combined = scores[i] + rel * 0.4  # Reduced weight for balance
            combined_scores.append((item, combined))

        combined_scores.sort(key=lambda x: x[1], reverse=True)
        results = [item for item, _ in combined_scores[:10]]

        # Strict filter: Only keep items with key term in title or prominent in summary
        key_term = extract_key_term(query)
        if key_term:
            results = [item for item in results if key_term.lower() in item["title"].lower() or (key_term.lower() in item["summary"].lower() and item["summary"].lower().count(key_term.lower()) > 1)]
            if not results:
                results = [item for item in news_data if key_term.lower() in item["title"].lower()][:5]  # Fallback to title matches only

    final_results = [enrich_with_ai(r, query) for r in results]
    final_results.sort(key=lambda x: (x["relevance"], x["is_latest"]), reverse=True)
    return final_results

# New: Extract Key Term (e.g., "google" from "google news")
def extract_key_term(query):
    words = re.findall(r'\b\w+\b', query.lower())
    # Simple heuristic: Skip common words like "what", "is", "the", "latest", "news", "about"
    stop_words = {"what", "is", "the", "latest", "news", "about", "on", "for"}
    key_words = [w for w in words if w not in stop_words]
    return key_words[0] if key_words else None

# Enhanced: Keyword Fallback
def keyword_fallback(news_data, query):
    query_words = set(re.findall(r'\b\w+\b', query.lower()))
    scored = []
    for item in news_data:
        text = (item["title"] + " " + item["summary"]).lower()
        matches = sum(1 for word in query_words if word in text)
        boost = 2 if "google" in query.lower() and "google" in text else 1
        total_score = matches * boost
        scored.append((item, total_score))
    scored.sort(key=lambda x: x[1], reverse=True)
    return [item for item, _ in scored if item]