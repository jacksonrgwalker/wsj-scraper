# Wall Street Journal Scraper

This code can be used to scrape article metadata from the Wall Street Journal. For now, consider it a work in progress. 

The article metadata, which includes items such as the headline, summaries, leading paragraph, author, date, and time, can be used for a variety of purposes. For example, it can be used to analyze the sentiment of the article, and how the article might have affected the stock market.

This code was originally written for a research project to use language models and text data to predict stock market movements.

# Set Up

## Install Dependencies
I use `conda` as a package manager. To learn more about these, see my [post about it](https://jwalk.io/projects/how-to-run-my-code).

To install the dependencies for this project, run the following command from the root directory of this project:

```bash
conda env create -f environment.yml
```