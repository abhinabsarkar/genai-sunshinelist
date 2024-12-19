from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
import logging

# Set up logging
logging.basicConfig(filename='download_log.txt', level=logging.INFO, format='%(asctime)s - %(message)s')

# url = "https://www.ontario.ca/public-sector-salary-disclosure/2021/all-sectors-and-seconded-employees/"
# url = "https://data.ontario.ca/en/dataset/public-sector-salary-disclosure-2020/resource/23172a73-7b85-49bd-9064-d600d2b21d37"
url = "https://www.ontario.ca/page/public-sector-salary-disclosure"

def list_and_download_csv_links(url):
    # Create a directory to save the files
    download_dir = os.path.join(os.getcwd(), 'csv_files')
    os.makedirs(download_dir, exist_ok=True)  

    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all links to CSV files
    links = soup.find_all('a', href=True)
    csv_page_links = [link['href'] for link in links if 'all sectors and seconded employees' in link.text.lower()]

    # Debugging: Print found links
    print(f"Found {len(csv_page_links)} links to CSV pages")
    logging.info(f"Found {len(csv_page_links)} links to CSV pages")

    page_urls = []
    for link in csv_page_links:
        if not link.startswith('https'):
            page_url = urljoin(url, link)
            # print(f"Processing {page_url}")
        else:
            page_url = link
            # print(f"Processing {link}")
        page_urls.append(page_url)

    # Debugging: Print page URLs
    logging.info(f"Page URLs: {page_urls}")    

    # Set up the WebDriver
    try:
        # Set up the WebDriver
        service = Service(ChromeDriverManager().install())
        options = webdriver.ChromeOptions()
        # options.add_argument('--headless')  # Run in headless mode fails to download files
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920x1080')
        options.add_argument('--start-maximized')
        prefs = {
            "download.default_directory": download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        options.add_experimental_option("prefs", prefs)
        driver = webdriver.Chrome(service=service, options=options)
    except Exception as e:
        print(f"Error setting up WebDriver: {e}")
        logging.error(f"Error setting up WebDriver: {e}")
        return

    for page_url in page_urls:
        print(f"Processing {page_url}")
        logging.info(f"Processing {page_url}")
        try:
                
            driver.get(page_url)

            # Wait for the page to load and a specific element to be present
            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, 'a')))

            # Find all <a> tags with href attribute containing .csv
            csv_links = set(link.get_attribute('href') for link in driver.find_elements(By.TAG_NAME, 'a') if '.csv' in link.get_attribute('href').lower())

            if csv_links:
                # # Create a directory to save the files
                # os.makedirs('csv_files', exist_ok=True)

                for csv_url in csv_links:
                    logging.info(f"Processing {csv_url}")

                    # Using selenium to download the file as requests was not working returning 403 error                
                    driver.get(csv_url)
                    time.sleep(5)  # Wait for the download to complete
                    print(f"Downloaded {csv_url}")   
                    logging.info(f"Downloaded {csv_url}")

                    # Add a delay between requests to avoid overwhelming the server
                    time.sleep(25)                
            else:
                print("No CSV links found")
                logging.info("No CSV links found")
        except Exception as e:
            print(f"Error processing {page_url}: {e}")
            logging.error(f"Error processing {page_url}: {e}")

    # Close the WebDriver
    driver.quit()

if __name__ == "__main__":
    # find_csv_links(url)
    list_and_download_csv_links(url)