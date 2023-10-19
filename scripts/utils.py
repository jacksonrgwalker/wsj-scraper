import json
import logging
import time
from pathlib import Path

import requests

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
    path.parent.mkdir(parents=True, exist_ok=True)
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
