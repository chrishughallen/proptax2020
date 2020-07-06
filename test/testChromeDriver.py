import PyPDF2
import re
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
driver = webdriver.Chrome(ChromeDriverManager().install())

def testChromeDriver():
    try:
        driver.get('https://bexar.acttax.com/act_webdev/bexar')
        print("Chromedriver is up to date")
    except:
        print("Chromedriver is not set up correctly")

testChromeDriver()
