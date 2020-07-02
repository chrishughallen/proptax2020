import PyPDF2
import re
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

results = []

def getDataFromPdf():
	acctNumberRegex = re.compile(r'\d\d\d\d\d-\d\d\d-\d\d\d\d')
	pdfFile = open('records.pdf', 'rb')
	reader = PyPDF2.PdfFileReader(pdfFile)
	for pageNum in range(reader.numPages):
		page = reader.getPage(pageNum).extractText()
		accounts = acctNumberRegex.findall(page)
		for acct in accounts:
			if acct not in results:
				results.append(acct)
	print(str(len(results)) + " accounts pulled from records.pdf")

def createEmptyCsvTemplate():
	file = open('output.csv', 'w+')
	file.write("Salutation,First Name,Middle,Last Name,Suffix,Title,Company Name,Address Line 1,Address Line 2,City,State,Zip Code\n")
	file.close()

def countRemaining(currentIndex, resultsLength):
	currentIndex += 1
	remainingAccounts = int(resultsLength) - int(currentIndex)
	print(str(remainingAccounts) + " accounts remaining")

def filterListToCSV():
	browser = webdriver.Chrome()
	for acct in results:
		try:
			browser.get('https://bexar.acttax.com/act_webdev/bexar/showdetail2.jsp?can=' + acct.replace('-',''))
			pageContentLeft = browser.find_element_by_xpath('//*[@id="site-content"]/font/div/table[2]/tbody/tr/td[1]').text
			pageContentRight = browser.find_element_by_xpath('//*[@id="site-content"]/font/div/table[2]/tbody/tr/td[2]').text

			if "none" not in pageContentLeft.lower():
				print(acct + " has an active lawsuit #" + str(results.index(acct) +1))
				countRemaining(int(results.index(acct)), len(results))
				continue;

			if "The current year is under the half pay option" in browser.page_source:
				print(acct + " is under the half pay option #" + str(results.index(acct) +1))
				countRemaining(int(results.index(acct)), len(results))
				continue;

			if "OVER 65" in browser.page_source:
				print(acct + " has over 65 exemption #" + str(results.index(acct) +1))
				countRemaining(int(results.index(acct)), len(results))
				continue;

			if "DISABLED" in browser.page_source:
				print(acct + " has disabled exemption #" + str(results.index(acct) +1))
				countRemaining(int(results.index(acct)), len(results))
				continue;

			addressStart = pageContentLeft.find('Address:')
			addressEnd = pageContentLeft.find('Property Site Address')
			address = pageContentLeft[addressStart +8:addressEnd]

			if "bexar" in address.lower():
				print(acct + " is owned by bexar county - " + str(results.index(acct) +1))
				countRemaining(int(results.index(acct)), len(results))
				continue;

			amtDueStart = pageContentLeft.find('Total Amount Due:')
			amtDueEnd = pageContentLeft.find('Last')
			amtDue = pageContentLeft[amtDueStart + 18:amtDueEnd]
			amtDue = amtDue.replace('$', '')
			amtDue = amtDue.replace(',', '')
			totalAmountDue = float(amtDue)

			if totalAmountDue < 2000:
				print(acct + " owes less than $2000 #" + str(results.index(acct) +1))
				countRemaining(int(results.index(acct)), len(results))
				continue;

			marketValStart = pageContentRight.find('Total Market Value:')
			marketValEnd = pageContentRight.find('Land')
			marketVal = pageContentRight[marketValStart + 19:marketValEnd]
			marketVal = marketVal.replace('$','')
			marketVal = marketVal.replace(',','')
			totalMarketValue = float(marketVal)

			if totalAmountDue > 0 and totalMarketValue > 0:
				total = totalAmountDue / totalMarketValue

				if total > .2:
					print(acct + " total owed is more than 20 percent of the market value #" + str(results.index(acct) +1))
					countRemaining(int(results.index(acct)), len(results))
					continue;

			print(acct + " matched all of our criteria  #" + str(results.index(acct) +1))
			countRemaining(int(results.index(acct)), len(results))
			addressList = address.split("\n")

			if len(addressList) >= 6:
				name = addressList[0].replace(',',' ') + " " + addressList[1].replace(',',' ')
				street = addressList[3]
				cityStateZip = addressList[4]
				city = cityStateZip.split(',')[0]
				stateZip = cityStateZip.split(',')[1]
				state = stateZip[0:3]
				zipCode = stateZip[4:]
			if len(addressList) < 6:
				name = addressList[0].replace(',',' ') + " " + addressList[1].replace(',',' ')
				street = addressList[2]
				cityStateZip = addressList[3]
				city = cityStateZip.split(',')[0]
				stateZip = cityStateZip.split(',')[1]
				state = stateZip[0:3]
				zipCode = stateZip[4:]
			file = open('output.csv', 'a')
			file.write("" + "," + name +"," + "" + "," + "" + "," + "" + "," + "" + "," + "" + ","  + street + "," + " " + ","  + city  +","+ state + "," + zipCode + "\n")

		except:
			print(acct + " couldn't be located on county website #" +  str(results.index(acct) +1))
			countRemaining(int(results.index(acct)), len(results))
			continue;

getDataFromPdf()
createEmptyCsvTemplate()
filterListToCSV()
