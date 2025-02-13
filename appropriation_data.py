import os
import time
import json
import concurrent.futures
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, TimeoutException
from page_data import extract_links_from_page 

import logging
from config import BASE_URL , setting_the_driver



logging.basicConfig(filename="scraper.log", level=logging.INFO, filemode="a",
                    format="%(asctime)s - %(levelname)s - %(message)s")

def scrape_appropriation_accounts():
    
    logging.info("Starting appropriation Accounts scraping...")
    
    driver = setting_the_driver()
    driver.get(BASE_URL)
    
    wait = WebDriverWait(driver, 5)

   
    try:
        year_dropdown = Select(wait.until(EC.presence_of_element_located((By.ID, "ctl00_ContentPlaceHolder1_Mddle_ddlAppropriate"))))


        
        go_button = wait.until(EC.element_to_be_clickable((By.ID, "ctl00_ContentPlaceHolder1_Mddle_btnSbmit")))
    except NoSuchElementException:
        logging.warning(" Elements not found. Exiting...")
        driver.quit()
        return

    available_years = [option.text.strip() for option in year_dropdown.options[:2]]
    extracted_data = {}

    for year in available_years:
        try:
            year_dropdown = Select(wait.until(EC.presence_of_element_located((By.ID, "ctl00_ContentPlaceHolder1_Mddle_ddlAppropriate"))))
            
            go_button = wait.until(EC.element_to_be_clickable((By.ID, "ctl00_ContentPlaceHolder1_Mddle_btnSbmit")))

            year_dropdown.select_by_visible_text(year)
            
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", go_button)

            try:
                go_button.click()
            except ElementClickInterceptedException:
                
                driver.execute_script("arguments[0].click();", go_button)

            WebDriverWait(driver, 3).until(lambda d: d.current_url != BASE_URL)

            report_url = driver.current_url
            logging.info(f"Extracted appropriation data for {year}: {report_url}")

           
            report_links = extract_links_from_page(report_url)

            extracted_data[year] = {
                "url": report_url,
                "info": report_links
            }

            driver.get(BASE_URL)

        except TimeoutException:
            
            logging.warning(f" Timeout for Finance Report {year}. Skipping...")
        except NoSuchElementException:
            
            logging.warning(f"Element missing for Finance Report {year}. Skipping...")
            
        except Exception as e:
            
            logging.error(f"Error processing Finance Report {year}: {e}")

    driver.quit()

    

    with open("appropriation_data.json", "w") as file:
        json.dump(extracted_data, file, indent=4)

    logging.info(f" Final data saved to appropriation_data.json")
    return extracted_data

# scrape_appropriation_accounts()
