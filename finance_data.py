import os
import concurrent.futures
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, TimeoutException

import logging
from config import BASE_URL , setting_the_driver


logging.basicConfig(filename="scraper.log", level=logging.INFO, filemode="a",
                    format="%(asctime)s - %(levelname)s - %(message)s")

import time
import json

from page_data import extract_links_from_page  


def scrape_finance_accounts():

    """
    info: this is thFunction to scrape Finance Reports and extract links dynamically
    this opens the website and finds dropdown options and select the year we want data for and extracts the links and saves to json file


    Returns: extracted json data
        
    """
    logging.info("Starting Finance Accounts scraping")


    #starting the broswer
    driver = setting_the_driver()
    #  here opeinf the website
    driver.get(BASE_URL)

    #waiting for elements to get loaded 
    
    wait=WebDriverWait(driver,5)

    #  locating dropdown for finance accounts
   
    year_dropdown=Select(  driver.find_element(By.ID ,  "ctl00_ContentPlaceHolder1_Mddle_ddlFinance"))


    go_button=(driver.find_element(By.ID , "ctl00_ContentPlaceHolder1_Mddle_btngo"))
    
    # want only latest year financial data
    available_years=[option.text.strip() for  option in year_dropdown.options[:1]]

    
    extracted_data = {}

    for year in available_years:
        try:
            # we findinf the dropdown again to avoid the staleellemt exception as old reference gets vanished , when page reloads

            year_dropdown=Select(  driver.find_element(By.ID   , "ctl00_ContentPlaceHolder1_Mddle_ddlFinance"))
            go_button=(driver.find_element(By.ID , "ctl00_ContentPlaceHolder1_Mddle_btngo"))

            # this selects a year from the dropdown menu based on its visible text.
            year_dropdown.select_by_visible_text(year)


            # here  js is being executed inside the browser so that we can click on go button   s
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", go_button)

            try:
                go_button.click()
            # handling the error
            
            except ElementClickInterceptedException:

                
                driver.execute_script("arguments[0].click();", go_button)

            
        #here checking if url has changed 
            WebDriverWait(driver, 3).until(lambda d: d.current_url != BASE_URL)

            report_url = driver.current_url
            logging.info(f" Extracted Finance Report for {year}: {report_url}")

            # calling page_data.py to extract links from this page
            report_links=extract_links_from_page(report_url)

            extracted_data["Finance Data "+year] = {
                "url": report_url,
                "info": report_links
            }

            driver.get(BASE_URL)  

        except TimeoutException:
            logging.warning(f"Timeout for Finance Report {year}. Skipping...")
            
        except NoSuchElementException:
            
            logging.warning(f" Element missing for Finance Report {year}. Skipping...")
            
        except Exception as e:
            logging.error(f"Error processing Finance Report {year}: {e}")

    driver.quit()

    
    with open("finance_data.json", "w") as file:
        
        json.dump(extracted_data, file, indent=4)

    logging.info(f"Final data saved to finance_data.json")
    return  extracted_data


# scrape_finance_accounts()








