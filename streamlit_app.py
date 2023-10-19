import datetime
import streamlit as st
from scripts.wsj import WsjScraper

@st.cache_data
def pull_article_list(date):
    articles = scraper._extract_shallow_article_data(
        year=date.year, month=date.month, day=date.day
    )
    return articles

col1, col2 = st.columns(2)

with col1:
    chosen_date = st.date_input(
        "What day do you want to scrape",
        value=datetime.datetime.today() - datetime.timedelta(days=1),
        min_value=datetime.date(2000, 1, 1),
        max_value=datetime.datetime.today(),
    )

with col2:
    st.button("Pull Data", key="pull_data")

scraper = WsjScraper()

if st.session_state["pull_data"]:
    with st.spinner('Grabbing article URLs from archive...'):
        article_list = pull_article_list(chosen_date)
        st.session_state["article_list"] = article_list

    st.markdown(f"Found {len(article_list)} articles on {chosen_date}")

    st.markdown("First 5 articles:")
    for i, article in enumerate(article_list):
        st.markdown(f"[{article['headline']}]({article['url']})")
        st.json(article, expanded=False)
        st.markdown("---")
        if i > 5:
            break










# articles[0]["url"]
# scraper._get_full_article_data(articles[0]["url"])
# st.download_button("Download Data", text_contents, "data.json")
