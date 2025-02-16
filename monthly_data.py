
import json
import time
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, NoAlertPresentException, ElementClickInterceptedException
from bs4 import BeautifulSoup
from config import BASE_URL, setting_the_driver
from page_data import extract_links_from_page
from urllib.parse import urljoin, urlparse
import os
logging.basicConfig(
    filename="scraper.log", level=logging.INFO, filemode="a",
    format="%(asctime)s- %(levelname)s - %(message)s"
)



def extract_links_from_table(url):
    """ Visits the given URL and extracts all absolute
    links from the tables using BeautifulSoup """

    
    logging.info(f" visiting {url} to extract links...")

    driver = setting_the_driver()
    
    driver.get(url)
    time.sleep(2)

    extracted_links = {}

    try:
      
        soup = BeautifulSoup(driver.page_source, "html.parser")

        
        tables = soup.find_all("table")
        iframe= soup.find("iframe")
        iframe_directory = BASE_URL 
        if iframe and "src" in iframe.attrs:
            relative_iframe_src = iframe["src"]
        absolute_iframe_src = urljoin(BASE_URL, relative_iframe_src)

        # Parse and extract directory path
        parsed_url = urlparse(absolute_iframe_src)
        iframe_directory = os.path.dirname(parsed_url.path) + "/" 
        iframe_directory = urljoin(BASE_URL, iframe_directory)
       

        for table in tables:
          
            for link in table.find_all("a", href=True):
                text = link.get_text(strip=True)
                href = link["href"]

             
                if not href.startswith("http"):
                    href = iframe_directory+href.lstrip("/")

                if text:
                    extracted_links[text] = href

    except Exception as e:
        logging.warning(f"Error extracting links from {url}: {e}")

    finally:
        driver.quit()

    return extracted_links

# def extract_links_from_table(url):
    
#     logging.info(f"Visiting {url} to extract links...")

#     driver = setting_the_driver()
#     driver.get(url)
#     time.sleep(2)
#     extracted_links={}
#     table_links = driver.find_elements(By.XPATH, "//table[@class='MsNormalTable']//tr//td//a")
#     for link in table_links:
#         href = link.get_attribute("href") 
        
       
#         text_element = link.find_element(By.XPATH, ".//b/span")
#         text = text_element.text.strip() if text_element else link.text.strip() 

      
#         if text and href:
#             extracted_links[text] = href
    
    
   

#     driver.quit()
    
#     return extracted_links


def extract_monthly_reports():
    """extracts URLs for each available month and visits them to scrape more links."""
    logging.info("Starting monthly Accounts scraping")
    
    driver = setting_the_driver()

    
    extracted_data = {}
    
    wait=WebDriverWait(driver , 5) 

    try:
        
        # opening  the website
        driver.get(BASE_URL)
        # wait for page to get loaded 
        time.sleep(3)  
        
       

        # dropdown elements
        month_dropdown =Select(wait.until(EC.presence_of_element_located((By.ID, "ctl00_ContentPlaceHolder1_Mddle_ddlMonth"))))
        
        year_dropdown=  Select(wait.until(EC.presence_of_element_located(( By.ID, "ctl00_ContentPlaceHolder1_Mddle_ddlYear" ))))
        
        go_button =wait.until(EC.element_to_be_clickable(( By.ID, "ctl00_ContentPlaceHolder1_Mddle_btnSubmit")))

       
        months = [option.text for option in month_dropdown.options[:5]]
        
        latest_year= [option.text.strip() for option in year_dropdown.options[:1]]  

     
        
        for year in latest_year:
             for month in months:
                driver.get(BASE_URL)  # Reload the base page to reset dropdowns
                time.sleep(2)  # Give time for the page to reload

                try:
                     
                    # fetching elements after page reload
                    month_dropdown =Select(wait.until(EC.presence_of_element_located((By.ID, "ctl00_ContentPlaceHolder1_Mddle_ddlMonth"))))
        
                    year_dropdown=Select(wait.until(EC.presence_of_element_located(( By.ID,"ctl00_ContentPlaceHolder1_Mddle_ddlYear"))))
        
                    go_button =wait.until(EC.element_to_be_clickable(( By.ID, "ctl00_ContentPlaceHolder1_Mddle_btnSubmit")))
     
                    # select month and year
                    month_dropdown.select_by_visible_text(month)
                    year_dropdown.select_by_visible_text(year)

                   # ensure button is in view and click
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", go_button)

                    try:
                        go_button.click()
                    except ElementClickInterceptedException:
                        driver.execute_script("arguments[0].click();", go_button)

                    time.sleep(2)

                  # Check for alert bcz initially some url show "No Data Available"
                    try:
                        alert = driver.switch_to.alert
                        logging.warning(f"No data available for {month} {year}. Skipping...")
                        alert.dismiss()
                        continue
                    except NoAlertPresentException:
                        pass

                    # Wait until the page loads a new URL
                    wait.until(lambda d: d.current_url != BASE_URL)
                    generated_url = driver.current_url
                    logging.info(f"Extracted URL for {month} {year}: {generated_url}")

                     # extract links from the generated report page
                    extracted_links = extract_links_from_table(generated_url)

                   # store  data
                    if year not in extracted_data:
                        extracted_data[year] = {}
                    extracted_data[year][month]= {"url":  generated_url , "info": extracted_links}

                except NoSuchElementException as e:
                    logging.warning(f"Element not found for {month} {year}: {e}")

                except Exception as e:
                    logging.error(f"Error processing {month} {year}: {e}")

      
    finally:
        driver.quit()

    # Save extracted data to JSON file
    with open("monthly_data.json", "w") as json_file:
        json.dump(extracted_data, json_file, indent=4)

    logging.info("Scraping completed. Data saved in monthly_data.json")
    return extracted_data

# extract_monthly_reports()

