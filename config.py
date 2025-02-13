

from selenium import webdriver

from selenium.webdriver.chrome.service import Service

#website base url
BASE_URL="https://cga.nic.in/"

def  setting_the_driver():
    
    """this sets up and returns a Selenium WebDriver
    with headless options  """

    CHROME_DRIVER_PATH = "/usr/local/bin/chromedriver"
    # starting the webdriver service for chrome , CHROME_DRIVER_PATH to tell selenium where to find the chrome driver
    service = Service(CHROME_DRIVER_PATH)

    #configuring the the chrome
    options=webdriver.ChromeOptions()
    # does not open new window 
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    # disable the image from loading to improve the sppeed
    prefs = {"profile.managed_default_content_settings.images": 2}
    options.add_experimental_option("prefs", prefs)
 
    #  applying all the setting and creating chrome instance
    return webdriver.Chrome(  service=service, options=options)
