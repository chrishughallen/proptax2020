# DEVELOPER NOTES
# There are three methods to this script.
# 1. getDataFromPdf() = Scrapes account numbers from records.pdf based on a regex pattern.
# 2. createEmptyCsvTemplate() = Creates a new csv template with the correct column names.
# 3. filterListToCSV() = Checks each account number meets the requirements, and if so it is added to the csv.
# For performance and because of multiple exceptions being checked for, variables will only be instantiated if they need to be checked.
import pdb
import PyPDF2
import re
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

# should start empty
# results = []

testResults = ["000000113138", "000000131539", "140930010070", "029770021040", "349200130090", "055720130170" ]
matchedResults = ["000000113138", "000000131539"]
halfPayerExemption = ["140930010070"]
disabledExemption = ['029770021040']
over65exemption = ["349200130090", "055720130170"]
results = testResults

def getDataFromPdf():
	acctNumberRegex = re.compile(r'\d\d\d\d\d-\d\d\d-\d\d\d\d')
	pdfFile = open('records.pdf', 'rb')
	reader = PyPDF2.PdfFileReader(pdfFile)
	# for pageNum in range(reader.numPages):
	for pageNum in range(20):
		page = reader.getPage(pageNum).extractText()
		accounts = acctNumberRegex.findall(page)
		for acct in accounts:
			if acct not in results:
				results.append(acct)
	print(len(results))

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

			# First check to see if account has an active lawsuit
			if "none" not in pageContentLeft.lower():
				print(acct + " has an active lawsuit #" + str(results.index(acct) +1))
				countRemaining(int(results.index(acct)), len(results))
				continue;

			# Check if account has half payer exemption
			if "The current year is under the half pay option - " in browser.page_source:
				print(acct + " is under the half pay option #" + str(results.index(acct) +1))
				countRemaining(int(results.index(acct)), len(results))
				continue;

			# Check if page has over 65 exemption
			if "OVER 65" in browser.page_source:
				print(acct + " has over 65 exemption #" + str(results.index(acct) +1))
				countRemaining(int(results.index(acct)), len(results))
				continue;

			# Check for disabled exemption
			if "DISABLED" in browser.page_source:
				print(acct + " has disabled exemption #" + str(results.index(acct) +1))
				countRemaining(int(results.index(acct)), len(results))
				continue;

			# Locate address and see if it's owned by Bexar County
			addressStart = pageContentLeft.find('Address:')
			addressEnd = pageContentLeft.find('Property Site Address')
			address = pageContentLeft[addressStart +8:addressEnd]

			if "bexar" in address.lower():
				print(acct + " is owned by bexar county - " + str(results.index(acct) +1))
				countRemaining(int(results.index(acct)), len(results))
				continue;

			# Locate total amount due and see if it's less than $2000
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

			# Calculate if total amount owed is more than 20% of the total market value
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

			# No exclusions if it reaches this point.
			print(acct + " matched all of our criteria  #" + str(results.index(acct) +1))
			countRemaining(int(results.index(acct)), len(results))
			addressList = address.split("\n")

			# Magic to render correctly to csv
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

		# Exception - account number wasn't found on site
		except:
			print(acct + " couldn't be located on county website #" +  str(results.index(acct) +1))
			countRemaining(int(results.index(acct)), len(results))
			continue;

# getDataFromPdf()
createEmptyCsvTemplate()
filterListToCSV()
