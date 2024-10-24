# Real State Web Scraper

This project is a Zillow web scraper designed to search properties by ZIP code(s) or via a .txt file containing ZIP codes. It extracts key data from each listing and exports the information into a CSV file. The result is a detailed dataset that can be leveraged for analysis or predictions. The scraper retrieves the following information:

- Full property address (street, city, state, ZIP code);
- Property type;
- Number of bedrooms, bathrooms, and total square footage;
- Latitude and longitude;
- Listing price;
- Cover image and all carousel photos;
- Listing URL.

## Tools and Modules

- **requests**: Used for sending HTTP requests to Zillow and retrieving the page content.
- **BeautifulSoup**: Parses the HTML and locates necessary information within a script tag containing JSON data.
- **json**: Loads the extracted JSON for processing and scraping relevant details.
- **pandas**: Organizes the scraped data into a DataFrame and exports it to a CSV file.
- **time**: Used to add delays when needed.
- **os**: Manages file input for loading ZIP codes from text files.

## How it works

1. **User Input**: The script starts by prompting the user for input:

   - A single ZIP code,
   - Multiple ZIP codes separated by commas,
   - Or the name of a .txt file containing ZIP codes located in the same directory or a subdirectory.

2. **Scraping Process**:

   - The script uses requests to fetch the HTML content from Zillow.
   - BeautifulSoup then finds a specific script tag that contains all the property data in JSON format.
   - The JSON is loaded, and the script iterates through the listings, extracting essential details like address, property type, number of bedrooms/bathrooms, price, photos, and geographical coordinates.

3. **Pagination**:

   - The script checks within the JSON data for the next page URL. If available, it continues scraping until all pages are processed.

4. **Data Export**:
   - All collected data from each page is exported individually.
   - Additionally, all the data from multiple ZIP codes (if provided) is concatenated and exported as a single CSV file for further use or analysis.

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

3. Run the script and enter either:
   - A single ZIP code,
   - Multiple ZIP codes separated by commas (e.g., `90210, 94103`),
   - Or the name of a .txt file containing ZIP codes.

The script will then begin the data scraping process. It typically takes less than 30 seconds for searches with 5 pages or fewer, depending on the number of ZIP codes provided.
