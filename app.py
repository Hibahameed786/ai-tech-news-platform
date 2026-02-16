import streamlit as st
from live_news import get_live_news, semantic_search
from ai import summarize

# Custom CSS for modern news dashboard
st.markdown("""
    <style>
    body { background-color: #f8f9fa; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    .nav-bar { background-color: #ffeb3b; padding: 10px; display: flex; justify-content: space-between; align-items: center; border-radius: 5px; margin-bottom: 20px; }
    .nav-categories { display: flex; gap: 15px; }
    .nav-category { color: #333; font-weight: bold; text-decoration: none; padding: 5px 10px; border-radius: 5px; transition: background-color 0.3s; }
    .nav-category:hover { background-color: #fff176; }
    .search-bar { width: 300px; }
    .news-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
    .news-card { background-color: #fff; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); overflow: hidden; transition: transform 0.3s; }
    .news-card:hover { transform: translateY(-5px); }
    .card-image { width: 100%; height: 200px; object-fit: cover; }
    .card-content { padding: 15px; }
    .card-title { font-size: 1.2em; font-weight: bold; margin-bottom: 10px; color: #333; }
    .card-source { color: #f44336; font-size: 0.9em; font-weight: bold; }
    .card-timestamp { color: #666; font-size: 0.8em; margin-bottom: 10px; }
    .card-description { color: #555; font-size: 0.9em; line-height: 1.4; }
    .footer { text-align: center; margin-top: 50px; color: #666; font-size: 0.9em; }
    @media (max-width: 768px) { .news-grid { grid-template-columns: 1fr; } .nav-bar { flex-direction: column; gap: 10px; } }
    </style>
    """, unsafe_allow_html=True)

# Navigation Bar
st.markdown("""
<div class="nav-bar">
    <div class="nav-categories">
        <a href="#" class="nav-category">🏏 IPL</a>
        <a href="#" class="nav-category">💰 Finance</a>
        <a href="#" class="nav-category">🏛️ Politics</a>
        <a href="#" class="nav-category">🖥️ Technology</a>
        <a href="#" class="nav-category">🤖 AI</a>
        <a href="#" class="nav-category">🟦 Microsoft</a>
        <a href="#" class="nav-category">🔍 Google</a>
    </div>
    <div class="search-bar">
""", unsafe_allow_html=True)

# Search Input (integrated into nav)
query = st.text_input("", placeholder="Search news...", label_visibility="collapsed")

st.markdown("""
    </div>
</div>
""", unsafe_allow_html=True)

# Main Content
st.markdown("### 📰 Latest News Dashboard")
st.write("**AI-powered real-time news with intelligent filtering. Explore categories or search anything!**")

# Buttons
col1, col2 = st.columns([1, 1])
with col1:
    search_button = st.button("🔎 Search", use_container_width=True)
with col2:
    refresh_button = st.button("🔄 Refresh", use_container_width=True)

if search_button or refresh_button:
    with st.spinner("Fetching and analyzing news..."):
        news_data = get_live_news()
        results = semantic_search(news_data, query)

    if results:
        st.success(f"✅ Found {len(results)} related news items!")
        
        # Display in grid (3 per row)
        cols = st.columns(3)
        for i, news in enumerate(results):
            with cols[i % 3]:
                st.markdown(f"""
                <div class="news-card">
                    <img src="{news['image']}" alt="News Image" class="card-image">
                    <div class="card-content">
                        <div class="card-title"><a href="{news['url']}" target="_blank">{news['title']}</a></div>
                        <div class="card-source">{news['source']}</div>
                        <div class="card-timestamp">{news['date']}</div>
                        <div class="card-description">{summarize(news['summary'])}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.warning("⚠️ No directly related news found. Showing top general news.")
        news_data = get_live_news()
        fallback_results = [enrich_with_ai(n, query) for n in news_data[:6]]  # 6 for 2 rows
        cols = st.columns(3)
        for i, news in enumerate(fallback_results):
            with cols[i % 3]:
                st.markdown(f"""
                <div class="news-card">
                    <img src="{news['image']}" alt="News Image" class="card-image">
                    <div class="card-content">
                        <div class="card-title"><a href="{news['url']}" target="_blank">{news['title']}</a></div>
                        <div class="card-source">{news['source']}</div>
                        <div class="card-timestamp">{news['date']}</div>
                        <div class="card-description">{summarize(news['summary'])}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

# Footer
st.markdown("""
<div class="footer">
    <p>Built with ❤️ using Streamlit. Data from public RSS feeds. <a href="https://github.com/yourusername/ai-tech-news-platform" target="_blank">View Source</a></p>
</div>
""", unsafe_allow_html=True)