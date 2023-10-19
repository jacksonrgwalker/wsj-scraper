import datetime
import streamlit as st
from scripts.wsj import WsjScraper
import json


@st.cache_data(show_spinner=False)
def pull_article_list(date):
    articles = scraper._extract_shallow_article_data(
        year=date.year, month=date.month, day=date.day
    )
    return articles


@st.cache_data(show_spinner=False)
def pull_article_data(url):
    return scraper._get_full_article_data(article["url"])

st.title("WSJ Article Scraper Demo")
st.markdown(
    """This is a demo of a scraper for the WSJ. It will pull article metadata from the archive.
    [Github Repo](https://github.com/jacksonrgwalker/wsj-scraper)"""
)

chosen_date = st.date_input(
    "What day do you want to scrape",
    value=datetime.datetime.today() - datetime.timedelta(days=1),
    min_value=datetime.date(2000, 1, 1),
    max_value=datetime.datetime.today(),
)

st.button("Find Articles", key="find_articles")

scraper = WsjScraper()

if st.session_state["find_articles"] or st.session_state.get("article_list"):
    with st.spinner("Grabbing article URLs from archive..."):
        article_list = pull_article_list(chosen_date)
        st.session_state["article_list"] = article_list

    num_articles = len(article_list)
    st.markdown(f"Found {num_articles} articles on {chosen_date}")

    col1, col2 = st.columns(2)

    with col1:
        pull_data = st.button("Pull Full Metadata", key="pull_data")

    if pull_data:
        progress_text = "Pulling full article metadata..."
        p_bar = st.progress(0, text=progress_text)
        st.session_state['article_data'] = []
        for i, article in enumerate(article_list):
            p_bar.progress(i / num_articles, text=progress_text)
            data = pull_article_data(article["url"])
            st.session_state['article_data'].append(data)
        p_bar.empty()
        with col1:
            st.write(f"Pulled all metadata!")

        article_data_str = json.dumps(st.session_state['article_data'])
        with col2:
            st.download_button("Download Metadata", article_data_str, "data.json")

    with st.expander("Show First 5 Articles", expanded=True):
        for i, article in enumerate(article_list):
            st.markdown(f"[{article['headline']}]({article['url']})")
            if st.session_state.get('article_data'):
                st.json(st.session_state['article_data'][i], expanded=False)
            if i == 4:
                break
            st.markdown("---")


