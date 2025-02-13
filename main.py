import json
import logging
import concurrent.futures
from finance_data import scrape_finance_accounts
from gfsm_data import extract_gfsm_reports
from monthly_data import extract_monthly_reports
from accounts_at_Glance import scrape_accounts_glance
from appropriation_data import scrape_appropriation_accounts

logging.basicConfig(filename="scraper.log", level=logging.INFO, filemode="a",
                    format="%(asctime)s - %(levelname)s - %(message)s")

scrapers= {"finance_data": scrape_finance_accounts,  "appropriation_data": scrape_appropriation_accounts, 
    "accounts_at_Glance": scrape_accounts_glance, "gfsm_data": extract_gfsm_reports,
       "monthly_data": extract_monthly_reports,}

def main():
    logging.info(" running all the scrapers...")
    
    scraped_data={}

   
    for name, imported_function in scrapers.items():
       
        scraped_data[name]=imported_function()
        

   
    with open("all_reports.json", "w") as file:
        
        json.dump(scraped_data, file, indent=4)

    logging.info(" Scraping is completed and sata saved in all_reports.json")

if __name__ == "__main__":
    main()
