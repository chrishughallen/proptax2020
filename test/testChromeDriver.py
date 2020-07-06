import PyPDF2
import re
from selenium import webdriver

def testChromeDriver():
    browser = webdriver.Chrome()
    try:
        browser.get('https://bexar.acttax.com/act_webdev/bexar')
        print("Chromedriver is up to date")
    except:
        print("Chromedriver is not set up correctly")

testChromeDriver()
