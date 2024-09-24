import undetected_chromedriver as uc
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
import selenium.webdriver.support.expected_conditions as EC
import pandas as pd
import random
import time
import re

def move_to_element_with_offset(actions: ActionChains, element: uc.WebElement) -> None:
    '''Move to an element with offset with the exact size of it.'''
    actions.move_to_element_with_offset(element, 
        random.uniform(element.size['width']/2, -element.size['width']/2), 
        random.uniform(element.size['height']/2, -element.size['height']/2)
    ).perform()

def move_and_click(actions: ActionChains, element: uc.WebElement, random_sleep: tuple[int, int] = (0.2, 0.3)) -> None:
    '''Move to an element with offset and clicks on it.'''
    move_to_element_with_offset(actions, element)
    time.sleep(random.uniform(0.2, 0.3))
    actions.click().perform()
    time.sleep(random.uniform(random_sleep[0], random_sleep[1]))

def human_like_typing(actions: ActionChains, text: str) -> None:
    '''Write a text letter by letter in element focused by actions.'''
    for letter in text:
        actions.send_keys(letter).perform()
        time.sleep(random.uniform(0.1, 0.35))

def wait_element(driver: uc.Chrome, n_elements: str, locator: str, wait_time: int = 4) -> uc.WebElement|list[uc.WebElement]:
    '''Wait one or all elements and return it.'''
    if n_elements == 'one':
        element = WebDriverWait(driver, wait_time).until(
            EC.presence_of_element_located(locator)
        )

    elif n_elements == 'all':
        element = WebDriverWait(driver, wait_time).until(
            EC.presence_of_all_elements_located(locator)
        )

    return element

def setup_driver() -> uc.Chrome:
    '''Creates a stealth Chrome WebDriver.'''
    options = uc.ChromeOptions()
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
    options.add_argument('--headless')
    options.add_argument(f'--user-agent={user_agent}')
    options.add_argument('--disable-blink-features=AutomationControlled')
    
    driver = uc.Chrome(options=options)
    driver.execute_cdp_cmd('Network.clearBrowserCookies', {})
    driver.execute_cdp_cmd('Network.clearBrowserCache', {})
    driver.execute_script('Object.defineProperty(navigator, "webdriver", {get: () => undefined})')

    return driver

def search_location(driver: uc.Chrome, search: str) -> None:
    '''Goes to www.zillow.com and searches some location.'''
    driver.get('https://www.zillow.com/')
    actions = ActionChains(driver)

    search_bar = wait_element(driver, 'one', (By.CSS_SELECTOR, 'div[data-testid="search-bar-container"] input'), wait_time=10)
    move_and_click(actions, search_bar)
    human_like_typing(actions, search + Keys.ENTER)
    time.sleep(random.uniform(0.7, 1.2))

    for_sale_button = wait_element(driver, 'one', (By.CSS_SELECTOR, 'div[role="group"] button'), wait_time=10)
    move_and_click(actions, for_sale_button, random_sleep=(3.5, 5))

def scrape_results(driver: uc.Chrome, data: list) -> None:
    '''Click on all results and scrape each one.'''
    results = wait_element(driver, 'all', (By.XPATH, '//li[contains(@class, "ListItem") and not(contains(@data-test, "search-list-first-ad"))]'), wait_time=10)
    actions = ActionChains(driver)

    for i, result in enumerate(results):
        start = time.perf_counter()

        result_link = wait_element(result, 'one', (By.TAG_NAME, 'a'))
        move_and_click(actions, result_link, random_sleep=(2, 3))
        
        # Collecting data (Two types of page layout)
        try:
            # Full Address
            full_address = wait_element(driver, 'one', (By.CSS_SELECTOR, 'div[data-cy="chip-first-column-content"] h1')).text

            # Number of Bedrooms and Bathrooms, and Area in sqft
            bed_bath_sqft = wait_element(driver, 'all', (By.CSS_SELECTOR, 'div[data-testid="bed-bath-sqft-fact-container"]'))
            bed_bath_sqft = [info.find_element(By.TAG_NAME, 'span').text.replace(',', '') for info in bed_bath_sqft]
            bed, bath, sqft = [info if info.isnumeric() else 0 for info in bed_bath_sqft]

            # Info about the agent
            agent_info = wait_element(driver, 'all', (By.CSS_SELECTOR, 'p[data-testid="attribution-LISTING_AGENT"] span'))
            if len(agent_info) == 3:
                agent_name, agent_dre, agent_phone = [info.text.replace(',', '').strip() for info in agent_info]
            elif len(agent_info) == 2:
                agent_name, agent_dre = [info.text.replace(',', '') for info in agent_info]
                agent_phone = None
            else:
                agent_name = driver.find_element(By.CSS_SELECTOR, 'button[data-testid="listing-agent-contact-link"]').text
                agent_dre = agent_info[0].text.replace(',', '')
                agent_phone = None
            agent_dre = agent_dre.split('#')[-1]

            # Info about the broker
            broker_name = wait_element(driver, 'one', (By.CSS_SELECTOR, 'p[data-testid="attribution-BROKER"] span')).text

            # Show more button
            show_more_button = wait_element(driver, 'one', (By.CSS_SELECTOR, 'div[data-testid="facts-and-features-wrapper-footer"] button'))

        except Exception:
            # Full Address
            full_address = wait_element(driver, 'one', (By.CSS_SELECTOR, 'div.summary-container h1')).text

            # Number of Bedrooms and Bathrooms, and Area in sqft
            bed_bath_sqft = wait_element(driver, 'all', (By.CSS_SELECTOR, 'span[data-testid="bed-bath-beyond"] strong'))
            bed, bath, sqft = [info.text.replace('.', '') if info.text.isnumeric() else 0 for info in bed_bath_sqft]

            # Info about the agent
            agent_info = wait_element(driver, 'one', (By.CSS_SELECTOR, 'div[data-test-id="nc-listed-by-agent"]')).text
            agent_name, agent_dre = agent_info.split(' DRE #')
            try:
                agent_dre, agent_phone = agent_dre.split(' ')
            except Exception:
                agent_phone = None

            # Info about the broker
            broker_info = wait_element(driver, 'one', (By.CSS_SELECTOR, 'div[data-test-id="nc-listed-by-broker"]')).text
            broker_name = re.split(r'\d', broker_info)[0].strip()

            # Show more button
            show_more_button = wait_element(driver, 'one', (By.XPATH, '//div[@id="Facts-and-features"]/following-sibling::div//button'))

        move_and_click(actions, show_more_button)

        # Info about home
        try:
            # Home Type
            home_type = wait_element(driver, 'one', (By.XPATH, '//span[contains(text(), "Home type")]')).text
            home_type = home_type.split(': ')[-1]
            # Home Subtype
            home_subtype = wait_element(driver, 'one', (By.XPATH, '//span[contains(text(), "Property subtype")]')).text
            home_subtype = home_subtype.split(': ')[-1]
            if home_subtype.endswith(','):
                home_subtype = home_subtype.replace(',', '')
            # Year Built
            year_built = wait_element(driver, 'one', (By.XPATH, '//span[contains(text(), "Year built")]')).text
            year_built = year_built.split(': ')[-1]
            if not year_built.isnumeric():
                year_built = wait_element(driver, 'one', (By.XPATH, '//span[contains(text(), "Year built")]/following-sibling::span')).text
        except Exception:
            home_type = 'Lot'
            home_subtype = 'Land'
            year_built = 0

        # Latitude and Longitude
        wait_element(driver, 'one', (By.XPATH, '//*[text()="Neighborhood"]')).click()
        time.sleep(1)
        actions.send_keys(Keys.ARROW_DOWN * 3).perform()
        lat, long = wait_element(driver, 'one', (By.XPATH, '//*[contains(@href, "?ll=")]')).get_attribute('href').split('?ll=')[-1].split('&')[0].split(',')

        # Monthly payment
        try:
            est_monthly_payment = wait_element(driver, 'one', (By.XPATH, '//span[contains(@class, "PersonalizedPaymentChip")]')).text.strip()
        except Exception:
            try:
                est_monthly_payment = wait_element(driver, 'one', (By.XPATH, '//div[contains(@class, "EstimatedPayment")]//span[contains(text(), "$")]')).text.strip()
            except Exception:
                est_monthly_payment = wait_element(driver, 'one', (By.XPATH, '//span[contains(text(), "/mo") and not(contains(text(), "HOA"))]')).text.strip()

        est_monthly_payment = est_monthly_payment.split('$')[-1].replace('/mo', '').replace(',', '')

        # MLS
        mls = wait_element(driver, 'one', (By.XPATH, '//span[contains(text(), "MLS#")]')).text
        mls = mls.split(' ')[-1]

        # Price
        price = wait_element(driver, 'one', (By.CSS_SELECTOR, 'span[data-testid="price"]')).text
        price = price.replace('$', '').replace(',', '')

        # URL
        url = driver.current_url

        # Appending data and leaving the page
        result_data = [
            full_address,
            bed,
            bath,
            sqft,
            home_type,
            home_subtype,
            year_built,
            price,
            agent_name,
            agent_dre,
            agent_phone,
            broker_name,
            est_monthly_payment,
            lat,
            long,
            mls,
            url
        ]
        data.append(result_data)

        close_button = driver.find_element(By.XPATH, '//*[@aria-label="close" and not(@data-testid)]')
        move_and_click(actions, close_button, (2.5, 3.2))

        stop = time.perf_counter()
        print(f'Scraped result {i + 1} in {stop - start:.2f} seconds.')

def go_to_next_page(driver: uc.Chrome) -> bool:
    '''Find the next page button and check if it's disabled, if not goes to the next page.'''
    pagination_items = driver.find_elements(By.CSS_SELECTOR, 'div.search-pagination li')
    next_button = pagination_items[-1].find_element(By.TAG_NAME, 'a')
    actions = ActionChains(driver)
    if not next_button.get_attribute('disabled'):
        move_and_click(actions, next_button, random_sleep=(3.5, 5))
        return True
    else:
        return False

def export_data(data: list, search: str) -> None:
    '''Export the data in CSV file.'''
    df = pd.DataFrame(data, columns=[
        'Full Address',
        'Bedrooms',
        'Bathrooms',
        'Area (sqft)',
        'Home Type',
        'Home Subtype',
        'Year Built',
        'Price',
        'Agent Name',
        'Agent DRE',
        'Agent Phone',
        'Broker Name',
        'Monthly Payment',
        'Latitude',
        'Longitude',
        'MLS',
        'URL'
    ])
    df.to_csv(f'{search}.csv', index=False)

def main() -> None:
    '''Ask ZIP Code, run scraper and export the data.'''
    driver = setup_driver()
    zip_code = input('Type ZIP Code: ')
    search_location(driver, zip_code)

    start = time.perf_counter()

    data = []
    page_counter = 1
    while True:
        print(f'Scraping page {page_counter}')
        scrape_results(driver, data)
        has_next_page = go_to_next_page(driver)
        if not has_next_page:
            break
        page_counter += 1

    stop = time.perf_counter()
    print(f'Scraped {page_counter} pages in {stop - start:.2f} seconds.')

    export_data(data, zip_code)

if __name__ == '__main__':
    main()