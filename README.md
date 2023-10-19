# Wall Street Journal Scraper

This code can be used to scrape article metadata from the Wall Street Journal. For now, consider it a work in progress.
This scraper was written in vanilla python with requests and is meant to be run locally with a single thread due to banning/rate limiting concerns. One could easily extend the scraping strategy with proxies or distributed clients to speed up the process. 

## The Data
The article metadata, which includes items such as 
 - headline
 - summary
 - leading paragraph
 - author
 - date and time
 - subjects mentioned
 - company ticker symbols
 - etc.
can be used for a variety of purposes. This code was originally written for a research project to use language models and text data to predict stock market movements.

# Set Up

## Install Dependencies
I use `conda` as a package manager. To learn more about these, see my [post about it](https://jwalk.io/projects/how-to-run-my-code).

To install the dependencies for this project, run the following command from the root directory of this project:

```bash
conda env create -f environment.yml
```

## Running the Code

See `example.ipynb` for an example of how to use run the code from a notebook.