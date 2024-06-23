from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import warnings; warnings.filterwarnings("ignore")

def init_driver():

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-extensions")
    options.add_argument("--remote-debugging-pipe")

    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)

    return driver

    