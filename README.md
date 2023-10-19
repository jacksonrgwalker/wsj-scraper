# Wall Street Journal Scraper

This code can be used to scrape article metadata from the Wall Street Journal. For now, consider it a work in progress.
This scraper was written in vanilla python with requests and is meant to be run locally with a single thread due to banning/rate limiting concerns. One could easily extend the scraping strategy with proxies or distributed clients to speed up the process. 

This is for educational purposes only. Please do not use this code to scrape the Wall Street Journal.

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

# Disclaimer
This code repository contains code that has been developed for educational and research purposes only. The code is designed to scrape content from the Wall Street Journal's website. The intention behind sharing this code is to facilitate learning and knowledge-sharing among the developer community.

**Important Notices**

Respect Copyright and Terms of Service: Users of this code must respect the Wall Street Journal's terms of service, copyright, and any other applicable laws and regulations. Unauthorized copying or distribution of the Wall Street Journal’s content or violating its terms of service is strictly prohibited.

**No Commercial Use**

This code is not intended for commercial use. It is shared for personal, educational, and research purposes only.

**Liability**

The creator and contributors to this repository are not responsible for any actions taken by others using this code. Any individual or entity choosing to use this code assumes all legal and ethical responsibility for its usage.

**Updates and Changes**

The Wall Street Journal may change its website structure, content accessibility, or terms of service at any time. As such, there is no guarantee that this code will function perpetually or as originally intended.

Before using this code, please ensure you have understood and agreed to comply with these terms and the Wall Street Journal's terms of service. Usage of the code in violation of these terms or for any unethical or unlawful purpose is strictly prohibited.

Please make sure to adjust the text as necessary based on your understanding and requirements. You may also consider consulting with a legal expert to tailor the disclaimer to your specific circumstances and to ensure that it offers the protection you seek.