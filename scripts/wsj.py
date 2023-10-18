import json
import logging
import time
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests
from requests.exceptions import MissingSchema
from tqdm import tqdm


def set_up_logger():
    # Create a logger with the name of the file
    logger = logging.getLogger(__name__)

    # Set the logging level to INFO
    logger.setLevel(logging.INFO)

    # Create a file handler that logs to a file named wsj_scraper.log
    file_handler = logging.FileHandler("wsj_scraper.log")

    # Create a formatter that formats the log messages
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    # Set the formatter for the file handler
    file_handler.setFormatter(formatter)

    # Add the file handler to the logger
    logger.addHandler(file_handler)

    return logger


def save_jsonlines(path, data):
    """
    data is a dictionary
    """
    with open(path, "w") as f:
        for key, value in data.items():
            f.write(json.dumps({key: value}))
            f.write("\n")


def append_jsonlines(path, data):
    """
    data is a dictionary
    """
    path = Path(path)
    if not path.exists():
        save_jsonlines(path, data)
        return

    with open(path, "a") as f:
        for key, value in data.items():
            f.write(json.dumps({key: value}))
            f.write("\n")


def read_jsonlines(path):
    """
    data is a dictionary
    """
    data = {}
    with open(path, "r") as f:
        for line in f.readlines():
            data.update(json.loads(line))
    return data

def save_textfile(path, text_lines):
    with open(path, "w") as f:
        for line in text_lines:
            f.write(line)
            f.write("\n")

def append_textfile(path, text_line):
    path = Path(path)
    if not path.exists():
        save_textfile(path, [text_line])
        return
    else:
        with open(path, "a") as f:
            f.write(text_line)


def read_textfile(path):
    with open(path, "r") as f:
        data = f.readlines()
    return data


def wait_to_run(min_wait_time):
    """
    Decorator to wait a minimum amount of time between function calls.
    """
    last_run_time = 0

    def decorator(func):
        def wrapper(*args, **kwargs):
            nonlocal last_run_time
            elapsed_time = time.time() - last_run_time
            if elapsed_time < min_wait_time:
                time.sleep(min_wait_time - elapsed_time)
            result = func(*args, **kwargs)
            last_run_time = time.time()
            return result

        return wrapper

    return decorator


def try_until_200(allowed_codes=[500], max_attempts=10):
    """
    Method decorator to try a method until it does not raise a non-200 status code.
    """

    def decorator(method):
        def inner(ref, *args, **kwargs):
            attempts = dict.fromkeys(allowed_codes, 0)
            while True:
                codes_recieved_str = ", ".join(
                    [f"{k}: {v: 2,}" for k, v in attempts.items()]
                )
                try:
                    result = method(ref, *args, **kwargs)
                    if sum(attempts.values()) > 1:
                        ref.logger.info(
                            f"Success - Recieved {len(attempts)} non-200 status codes: {codes_recieved_str}"
                        )
                    return result

                except requests.exceptions.HTTPError as e:
                    if e.response.status_code in allowed_codes:
                        ref.logger.info(
                            f"Recieved status code {e.response.status_code} - Attempt {attempts[e.response.status_code] + 1}"
                        )
                        attempts[e.response.status_code] += 1
                        if attempts[e.response.status_code] > max_attempts:
                            ref.logger.info(
                                f"Failed - Recieved {len(attempts)} non-200 status codes: {codes_recieved_str}"
                            )
                            raise e
                        sleep_time = {500: 11, 403: 121, 503: 121}
                        time.sleep(sleep_time[e.response.status_code])
                    else:
                        # ref.logger.info(
                        #     f"Failed - Recieved {len(attempts)} non-200 status codes: {codes_recieved_str}"
                        # )
                        # raise e

                        ref.logger.info(
                            f"Failed BUT CONTINUEING - Recieved {len(attempts)} non-200 status codes: {codes_recieved_str}"
                        )
                        ref.failed_urls.append((e.response.status_code, e.response.url))
                        time.sleep(60 * 1)  # sleep for 1 minute

        return inner

    return decorator


def skip_if_params_match(param_list):
    """
    Decorator to skip function execution if the input parameters match a set of input parameters from a list.
    """

    def decorator(method):
        def wrapper(ref, *args, **kwargs):
            for param in param_list:
                if args == param or kwargs == param:
                    ref.logger.info(
                        f"Skipping function {method.__name__} because parameters match {param}"
                    )
                    return {}
            return method(ref, *args, **kwargs)

        return wrapper

    return decorator


PROBLEM_DATE_PAGES = [
    # https://www.wsj.com/news/archive/2009/06/19?page=3 -> 500
    (2009, 6, 19, 3),
    # https://www.wsj.com/news/archive/2009/05/22?page=2 -> 500
    (2009, 5, 22, 2),
]


PROBLEM_URLS = [
    (
        "https://www.wsj.com/articles/materiality-assessments-what-businesses-need-to-know-be994aa9",
    ),
    (
        "https://www.wsj.com/articles/scope-3-emissions-what-businesses-need-to-know-b8444011",
    ),
    ("https://www.wsj.com/articles/fraport-steps-up-2030-carbon-target-17b6b82",),
    (
        "https://www.wsj.com/Tech/your-share-of-the-725m-facebook-settlement-will-be-tiny-93265db0",
    ),
]


class WsjScraper:
    headers = {
        "authority": "www.wsj.com",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-language": "en-US,en;q=0.9",
        "cache-control": "no-cache",
        "pragma": "no-cache",
        "sec-ch-ua": '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "same-origin",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
    }

    def __init__(self, logger=None):
        self.shallow_article_data = {}
        self.full_article_data = {}
        self.logger = logger or set_up_logger()
        self.failed_urls = []

    @skip_if_params_match(PROBLEM_DATE_PAGES)
    @try_until_200(allowed_codes=[500], max_attempts=10)
    def _get_single_day_archive_page(self, year, month, day, page_num):
        """
        Gets one page of a single day's archive

        Parameters
        ----------
        year : int
            Year of archive
        month : int
            Month of archive
        day : int
            Day of archive
        page : int
            Page number to get. Use 1-indexing
        """

        response = requests.get(
            f"https://www.wsj.com/news/archive/{year:04}/{month:02}/{day:02}",
            headers=self.headers,
            params={"page": page_num},
        )

        response.raise_for_status()

        json_content = (
            response.text.split("window.__STATE__ =")[1]
            .split("</script>")[0]
            .strip()
            .strip(";")
        )
        json_dict = json.loads(json_content)
        return json_dict

    def _is_archive_page_exhausted(self, json_dict):
        """
        Checks if the archive pagination is exhausted
        """

        if "data" not in json_dict:
            return True

        id_list_key = [
            k
            for k in list(json_dict["data"].keys())
            if k.startswith("allesseh_content_full_")
        ][0]
        pagination_links = json_dict["data"][id_list_key]["data"]["data"][
            "linksForPagination"
        ]
        curr_page_num = int(pagination_links["self"].split("page=")[1])
        last_page_num = int(pagination_links["last"].split("page=")[1])
        return curr_page_num == last_page_num

    def _yield_single_day_archive(self, year, month, day):
        """
        Gets all pages of a single day's archive. Uses get_single_day_archive_page() to get each page.
        This is a generator function.

        Parameters
        ----------
        year : int
            Year of archive
        month : int
            Month of archive
        day : int
            Day of archive
        """

        page_num = 1
        while True:
            json_dict = self._get_single_day_archive_page(year, month, day, page_num)
            yield json_dict
            page_num += 1

            if self._is_archive_page_exhausted(json_dict):
                break

    def _extract_article_data_from_archive_page(self, archive_day_page_json):
        """ """

        id_list_key = [
            k
            for k in list(archive_day_page_json["data"].keys())
            if k.startswith("allesseh_content_full_")
        ][0]
        page_article_list = archive_day_page_json["data"][id_list_key]["data"][
            "collection"
        ]
        article_ids = [d["id"] for d in page_article_list]

        for article_id in article_ids:
            article = archive_day_page_json["data"]["article|capi_" + article_id][
                "data"
            ]["data"]
            if "image" in article:
                del article["image"]
            yield article

    def _extract_shallow_article_data(self, year, month, day):
        """ """
        shallow_article_data = []
        pages = list(self._yield_single_day_archive(year, month, day))
        for page in pages:
            if page == {}:
                continue
            articles = list(self._extract_article_data_from_archive_page(page))
            shallow_article_data.extend(articles)
        return shallow_article_data

    @skip_if_params_match(PROBLEM_URLS)
    @wait_to_run(0.012)
    @try_until_200(allowed_codes=[500, 403, 503], max_attempts=10)
    def _get_full_article_data(self, url):
        try:
            response = requests.get(
                url=url,
                headers=self.headers,
            )
        except MissingSchema as e:
            self.logger.info(f"MissingSchema Error - {url}")
            return {}

        if response.status_code == 404:
            self.logger.info(f"404 Error - {url}")
            return {}
        else:
            response.raise_for_status()

        html_content = response.text
        splitter = '<script id="__NEXT_DATA__" type="application/json">'

        if splitter not in html_content:
            self.logger.info(f"Could not find data in {url}")
            return {}

        json_content = response.text.split(splitter)[1].split("</script>")[0].strip()
        json_dict = json.loads(json_content)
        return json_dict

    def pull_all_shallow_article_data(self, start_date=datetime(2000, 1, 1)):
        date_range = pd.date_range(start=start_date, end=datetime.today())
        # reverse the date range so that we start with the newest dates
        date_range = date_range[::-1]

        self.logger.info(f"Pulling shallow article data for {len(date_range):,} days")

        progress_bar = tqdm(date_range)
        for day in progress_bar:
            key = day.strftime("%Y-%m-%d")

            if key in self.shallow_article_data:
                continue

            progress_bar.set_description(key)

            new_shallow_data = self._extract_shallow_article_data(
                day.year, day.month, day.day
            )
            self.shallow_article_data[key] = new_shallow_data
            self.logger.info(f"Pulled {len(new_shallow_data):,} articles for {key}")

            append_jsonlines("data/shallow_article_data.jsonl", {key: new_shallow_data})

    def pull_all_full_article_data(self):
        shallow_data_urls = [
            article["url"]
            for shallow_data in self.shallow_article_data.values()
            for article in shallow_data
        ]
        urls_to_scrape = list(
            set(shallow_data_urls) - set(self.full_article_data.keys())
        )
        progress_bar = tqdm(urls_to_scrape)
        for url in progress_bar:
            article_data = self._get_full_article_data(url)
            append_jsonlines("data/full_article_data.jsonl", {url: article_data})
            self.full_article_data[url] = article_data

    def load_shallow_article_data(self, path="data/shallow_article_data.jsonl"):
        path = Path(path)
        if not path.exists():
            return

        self.shallow_article_data = read_jsonlines(path)

    def load_full_article_data(self, path="data/full_article_data.jsonl"):
        path = Path(path)
        if not path.exists():
            return

        self.full_article_data = read_jsonlines(path)

    def persist_urls_to_scrape(self):
        shallow_data_urls = [
            article["url"]
            for shallow_data in self.shallow_article_data.values()
            for article in shallow_data
        ]

        shallow_data_urls = list(set(shallow_data_urls))


if __name__ == "__main__":
    logger = set_up_logger()
    scraper = WsjScraper(logger=logger)
    scraper.load_shallow_article_data()
    scraper.load_full_article_data()
    scraper.pull_all_shallow_article_data()
    scraper.pull_all_full_article_data()
    print(f"Failed urls:\n{scraper.failed_urls}")
