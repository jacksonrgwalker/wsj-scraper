import datetime
import streamlit as st
from scripts.wsj import WsjScraper
import json
import sys


def get_string_size_in_megabytes(string):
    return sys.getsizeof(string) / 1024**2


@st.cache_data(show_spinner=False)
def pull_article_list(date):
    articles = scraper._extract_shallow_article_data(
        year=date.year, month=date.month, day=date.day
    )
    return articles


@st.cache_data(show_spinner=False)
def pull_article_data(url):
    return scraper._get_full_article_data(article["url"])


def clear_data():
    st.session_state["article_list"] = None
    st.session_state["article_data"] = None


st.title("WSJ Article Scraper Demo")
st.markdown(
    """This is a demo of a scraper for the WSJ. It will pull article metadata from the archive.
    This demo will only let you download one day's worth of data at a time. If you want to pull
    more data, you can clone the repo and run it locally.
    [Github Repo](https://github.com/jacksonrgwalker/wsj-scraper)"""
)

chosen_date = st.date_input(
    "What day do you want to scrape",
    value=datetime.datetime.today() - datetime.timedelta(days=1),
    min_value=datetime.date(2000, 1, 1),
    max_value=datetime.datetime.today(),
    on_change=clear_data,
)

scraper = WsjScraper()


find_articles = st.button("Find Articles", key="find_articles")

if st.session_state.get("find_articles") or st.session_state.get("article_list"):
    with st.spinner("Grabbing article URLs from archive..."):
        article_list = pull_article_list(chosen_date)
        st.session_state["article_list"] = article_list

    num_articles = len(article_list)
    st.markdown(f"Found {num_articles} articles on {chosen_date}")

    pull_data = st.button("Pull Metadata", key="pull_data")

    if st.session_state.get("pull_data"):
        progress_text = "Pulling full article metadata..."
        p_bar = st.progress(0, text=progress_text)
        st.session_state["article_data"] = []
        for i, article in enumerate(article_list):
            p_bar.progress(i / num_articles, text=progress_text)
            data = pull_article_data(article["url"])
            st.session_state["article_data"].append(data)
        p_bar.empty()
        st.write(f"Pulled all metadata!")
        article_data_str = json.dumps(st.session_state["article_data"])
        download_size = get_string_size_in_megabytes(article_data_str)
        st.download_button(
            f"Download Metadata ({download_size:.1f} Mb)", article_data_str, "data.json"
        )

    with st.expander("Showing First 5 Articles", expanded=True):
        for i, article in enumerate(article_list):
            st.markdown(f"[{article['headline']}]({article['url']})")
            if st.session_state.get("article_data"):
                st.json(st.session_state["article_data"][i], expanded=False)
            if i == 4:
                break
            st.markdown("---")
