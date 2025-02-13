import os
import time
import json
from selenium import webdriver
from config import setting_the_driver, BASE_URL
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, TimeoutException

import logging
driver=setting_the_driver()
logging.basicConfig(filename="scraper.log", level=logging.INFO, filemode="a",
                    format="%(asctime)s - %(levelname)s - %(message)s")

def extract_next_page_links(driver):
    extracted_links = {}

   
    all_links  =  driver.find_elements( By.XPATH , "//body//a[not(ancestor::header) and not(ancestor::footer)]")

    for link in all_links:
            text = link.text.strip()
            href = link.get_attribute("href")

            
            if href and not href.startswith("http"):
                href = BASE_URL + href  

          
            if text and href:
                extracted_links[text] = href


    return extracted_links

def scrape_accounts_glance():
    logging.info("starting Accounts at a Glance scraping...")
    
    driver =setting_the_driver()
    driver.get(BASE_URL)
    wait = WebDriverWait(driver, 5)

   
    
    year_dropdown = Select(wait.until(EC.presence_of_element_located((By.ID, "ctl00_ContentPlaceHolder1_Mddle_ddlGlance"))))
    go_button = wait.until(EC.element_to_be_clickable((By.ID, "ctl00_ContentPlaceHolder1_Mddle_btnSubmt")))
   
    available_years = [option.text.strip() for option in year_dropdown.options[:2]]
    extracted_data = {}

    for year in available_years:
        driver.get(BASE_URL)
        try:
            year_dropdown = Select(wait.until(EC.presence_of_element_located((By.ID, "ctl00_ContentPlaceHolder1_Mddle_ddlGlance"))))
            
            go_button = wait.until(EC.element_to_be_clickable((By.ID, "ctl00_ContentPlaceHolder1_Mddle_btnSubmt")))

            year_dropdown.select_by_visible_text(year)
            
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", go_button)

            try:
                go_button.click()
                
            except ElementClickInterceptedException:
                driver.execute_script("arguments[0].click();", go_button)

            WebDriverWait(driver, 3).until(lambda d: d.current_url != BASE_URL)

            report_url=driver.current_url
            logging.info(f" Extracted Accounts at a Glance Report for {year}: {report_url}")

          
            report_links = extract_next_page_links(driver)

            extracted_data[year] = { "url": report_url, "info": report_links}

            driver.get(BASE_URL)  

        except TimeoutException:
            
            logging.warning(f" Timeout for Accounts at a Glance Report {year}. Skipping...")
            
        except NoSuchElementException:
            
            logging.warning(f" Element missing for Accounts at a Glance Report {year}. Skipping...")
            
        except Exception as e:
            logging.error(f" Error processing Accounts at a Glance Report {year}: {e}")

    driver.quit()

    

    
    with open("account_at_glance.json", "w") as file:
        
        json.dump(extracted_data, file, indent=4)

    logging.info(" Final data saved to account_at_glance.json")

    
    return extracted_data

# scrape_accounts_glance()
