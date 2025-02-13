import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

chrome_driver_path = "/usr/local/bin/chromedriver"
service = Service(chrome_driver_path)
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")
import logging
base_url = "https://cga.nic.in"

def extract_links_from_page(url):
    """  this is the function to  visit a 
    page & extract table links """

    
    logging.info(f"  visiting {url} to extract links")
    
    driver=webdriver.Chrome(service=service, options=options)
    driver.get(url)
    # aloow the page to get loaded 
    time.sleep(2)  

    extracted_links = {}

    index=0
    
    try:
        # get all the tables
        tables = driver.find_elements(By.TAG_NAME, "table") 
        
       
        for  table in ( tables):

            links = table.find_elements(By.TAG_NAME, "a")
            table_links = {}

            for link in links:
                text = link.text.strip()
                href = link.get_attribute("href")

                if href and not href.startswith("http"):
                    href=base_url+  href  

                if text and href:
                    table_links[text]=href  

            if table_links:
                extracted_links[f"Table {index} "] = table_links
                index+=1

    except Exception as e:
        logging.error(f" Error  occured in extracting links from {url}: {e}")

    driver.quit()

    
    return extracted_links
