# there are a few stubborn issues with the WSJ archive
# for now, we'll just skip over them as we catch them

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
