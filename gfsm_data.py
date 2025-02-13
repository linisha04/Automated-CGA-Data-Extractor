import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, NoAlertPresentException, TimeoutException
from selenium.webdriver.chrome.service import Service

import logging
from config import setting_the_driver , BASE_URL

logging.basicConfig(filename="scraper.log", level=logging.INFO, filemode="a",
                    format="%(asctime)s - %(levelname)s - %(message)s")


def extract_gfsm_links_from_page(url):
   
    logging.info(f" extracting GFSM links from {url} ...")
    
    driver = setting_the_driver()
    
    driver.get(url)
    time.sleep(2)

    extracted_links = {}

   
      
    data_div = WebDriverWait(driver, 5).until(EC.presence_of_element_located(( By.ID,  "ctl00_ContentPlaceHolder1_divData"))
        )
        
       
    links = data_div.find_elements(By.TAG_NAME, "a")

    for link in links:
            text = link.text.strip()
            href = link.get_attribute("href")

            
            if href and text:
                extracted_links[text] = href

    
    driver.quit()
    
    return extracted_links


def get_latest_years_and_accounts(driver):
    
    driver.get(BASE_URL)
    time.sleep(2)

  
        
    year_dropdown = Select(driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_Mddle_ddlMQYFinancialyear"))
        
    financial_years = [option.text for option in year_dropdown.options[:1]] 

     
    account_dropdown = Select(driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_Mddle_ddlMQYAccountType"))
    account_types = [option.text for option in account_dropdown.options]

    return financial_years, account_types




def extract_gfsm_reports():
    logging.info("Starting gfsm Accounts scraping")
  
    driver = setting_the_driver()
    financial_years, account_types = get_latest_years_and_accounts(driver)
    
    driver.quit()

    if not financial_years or not account_types:

        
        logging.error(" No  years or account types found. Exiting...")
        return

    extracted_data = {}
    logging.info(f" Scraping GFSM Data for {financial_years}...")

    for financial_year in financial_years:
        for account_type in account_types:
            driver = setting_the_driver()
            
            driver.get(BASE_URL)
            time.sleep(2)

            try:
               
                year_dropdown = Select(driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_Mddle_ddlMQYFinancialyear"))
                
                account_dropdown = Select(driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_Mddle_ddlMQYAccountType"))
                
                go_button = driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_Mddle_btnSubmitMQY")

             
                year_dropdown.select_by_visible_text(financial_year)
                account_dropdown.select_by_visible_text(account_type)

              
                WebDriverWait(driver, 3).until(EC.element_to_be_clickable(go_button))
                
                driver.execute_script("arguments[0].click();", go_button)
                time.sleep(2)

             
                try:
                    alert = driver.switch_to.alert
                    logging.warning(f" No data for {financial_year} - {account_type}. Skipping...")
                    alert.dismiss()
                    
                    driver.quit()
                    continue
                
                except NoAlertPresentException:
                    pass

               
                generated_url=driver.current_url
                
                logging.info(f" Extracted URL for {financial_year} - {account_type}: {generated_url}")

            
                extracted_links = extract_gfsm_links_from_page(generated_url)

                if financial_year not in extracted_data:
                    extracted_data[financial_year] = {}

                extracted_data[financial_year][account_type] = {" url": generated_url, "info": extracted_links}

            except NoSuchElementException as e:
                
                logging.error(f" Element not found for {financial_year} - {account_type}: {e}")
            finally:
                driver.quit()
  
  
    with open("gfsm_data.json", "w") as file:
        json.dump(extracted_data, file, indent=4)

    logging.info(" Scraping completed. Data saved in gfsm_data.json")
    return extracted_data


# extract_gfsm_reports()