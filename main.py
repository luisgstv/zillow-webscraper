import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
import time
import os

def fetch_data(url: str) -> bytes | None:
    '''Send a HTTP request to the url using appropriate headers.'''
    headers = {
        "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }

    try:
        r = requests.get(url, headers=headers)
        return r.content
    except requests.RequestException as e:
        print(f'Error fetching data from {url}: {e}')
        return None

def parse_and_scrape_data(content: bytes, data: list) -> str | None:
    '''Parse the content of a response and extract the json to scrape the information. Returns the next url of the search if exists.'''
    try:
        soup = BeautifulSoup(content, 'html.parser')
        json_response = soup.find('script', id='__NEXT_DATA__').string
        json_response = json.loads(json_response)

        scrape_from_json(json_response, data)

        next_url = json_response['props']['pageProps']['searchPageState']['cat1']['searchList']['pagination'].get('nextUrl', None)
        return f'https://www.zillow.com{next_url}' if next_url else None
    except Exception as e:
        print(f'Error: {e}')
        return None

def scrape_from_json(response: dict, data: list) -> None:
    '''Scrape all relevant data of results within the json file from the content and append to the data list.'''
    all_results = response['props']['pageProps']['searchPageState']['cat1']['searchResults']['listResults']

    for result in all_results:
        address_street = result['addressStreet']
        address_city = result['addressCity']
        address_state = result['addressState']
        address_zipcode = result['addressZipcode']

        home_type = result['hdpData']['homeInfo']['homeType']
        home_type = home_type.capitalize().replace('_', ' ')
        
        beds = result.get('beds', 0)
        baths = result.get('baths', 0)
        area = result.get('area', 0)

        lat_long = result['latLong']
        lat = lat_long.get('latitude', None)
        long = lat_long.get('longitude', None)

        price = result['unformattedPrice']

        image = result['imgSrc']
        url = result['detailUrl']

        home_photos = result.get('carouselPhotos', None)
        if home_photos:
            home_photos = [photo['url'] for photo in home_photos]

        result_data = [
            address_street,
            address_city,
            address_state,
            address_zipcode,
            home_type,
            beds,
            baths,
            area,
            lat,
            long,
            price,
            image,
            url,
            home_photos
        ]

        data.append(result_data)

def export_data(data: list, zip_code: str) -> None:
    '''Export the data in CSV file.'''
    df = pd.DataFrame(data, columns=[
        'Address_street',
        'Address_city',
        'Address_state',
        'Address_zipcode',
        'Home_type',
        'Bedrooms',
        'Bathrooms',
        'Area_sqft',
        'Latitude',
        'Longitude',
        'Price',
        'Image',
        'URL',
        'Home_photos'
    ])
    df.to_csv(f'./output/{zip_code}.csv', index=False)

def main() -> None:
    '''Ask user input, run scraper and export the data.'''
    user_input = input('Type ZIP Code(s) or txt file name: ')

    if user_input.endswith('.txt'):
        for root, _, files in os.walk(os.getcwd()):
            file_path = os.path.join(root, user_input) if user_input in files else None
            break

        if file_path: 
            with open(file_path, 'r') as f:
                zip_code_list = [line.strip() for line in f.readlines()]
        else:
            print('File not found.')
    else:
        zip_code_list = [zip_code.strip() for zip_code in user_input.split(',')]
    
    full_data = []
    for zip_code in zip_code_list:
        print(f'Scraping zip code: {zip_code}')
        url = f'https://www.zillow.com/homes/{zip_code}_rb/'
        data = []
        page_number = 1

        while True:
            content = fetch_data(url)
            url = parse_and_scrape_data(content, data)
            print(f'Page {page_number} scraped.')
            if not url:
                break
        
            page_number += 1
            time.sleep(5)
        
        print('Zip code scraped. Exporting data.')
        export_data(data, zip_code)
        full_data += data
        time.sleep(15)
    
    print('All zip codes scraped, exporting full data.')
    export_data(full_data, user_input.replace('.txt', '').replace(', ', '_'))

if __name__ == '__main__':
    main()