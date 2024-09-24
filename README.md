# Real State Web Scraper

This project is a Zillow web scraper designed to search properties by ZIP code and extract key data from each listing, exporting the information into a CSV file. The result is a detailed dataset that can be leveraged for analysis or predictions. The scraper retrieves the following information:

- Full property address;
- Number of bedrooms, bathrooms, and total square footage;
- Property type and subtype;
- Year the property was built;
- Listing price;
- Agent and broker details;
- Estimated monthly payments;
- Latitude and Longitude of the property;
- MLS number and listing URL.

## Tools and Modules

- **undetected-chromedriver**: Used alongside **Selenium** to scrape pages from the Zillow website, bypassing detection measures.
- **Pandas**: Utilized to organize the scraped data into a DataFrame, which is then exported to CSV file.
- **Time**: Measures the time taken to scrape all the pages.
- **re**: Employed for string manipulation, such as splitting words based on digits.

## How it works

1. Stealth Webdriver Initialization: The project begins by initializing a stealth WebDriver with undetected-chromedriver. It sets up a reliable user agent, disables detection features like AutomationControlled, and runs in headless mode. Additionally, it clears cookies and cache using Chrome DevTools Protocol (CDP) and hides the webdriver property from the browser’s navigator object to avoid detection.

2. ZIP Code Input and Page Navigation: Once the WebDriver is ready, the user is prompted to input a ZIP code, which is then used to search for properties in that location on Zillow. The script employs custom functions to wait for page elements to load, move the cursor, and click or type in a human-like manner, all powered by ActionChains to mimic realistic user behavior.

3. Scraping Process: After accessing the search results, the scraper visits each property listed on the page, ensuring all content is fully loaded before extracting essential details. The scraper handles various exceptions, such as different page layouts or missing information, ensuring consistent data extraction across all listings

4. Pagination: After collecting data from the current page, the scraper checks whether more pages of results are available. If the next page button is enabled and not disabled, the scraper continues to the next page. This loop runs until all pages are processed.

5. Data Export: Once all listings have been scraped, the collected data is stored in a Pandas DataFrame and exported to a CSV file for further use or analysis.

## How to use

To use this project, you will need to follow these steps:

1. Clone this repository using the following command:

```
    git clone https://github.com/luisgstv/airbnb-webscraper.git
```

2. Install the required dependencies using the following command:

```
    pip install -r requirements.txt
```

3. Once you run the script, you will be prompted to enter the ZIP code for the location you want to scrape. The data scraping process may take between 40 to 50 minutes, depending on the number of pages and listings available.
