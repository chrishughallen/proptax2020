from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

results = ["140930010070", "098390010080"]

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

				continue;

			# Check if account has half payer exemption
			if "The current year is under the half pay option" in browser.page_source:
				print(acct + " is under the half pay option #" + str(results.index(acct) +1))

				continue;

			# Check if page has over 65 exemption
			if "OVER 65" in browser.page_source:
				print(acct + " has over 65 exemption #" + str(results.index(acct) +1))

				continue;

			# Check for disabled exemption
			if "DISABLED" in browser.page_source:
				print(acct + " has disabled exemption #" + str(results.index(acct) +1))

				continue;

			# Locate address and see if it's owned by Bexar County
			addressStart = pageContentLeft.find('Address:')
			addressEnd = pageContentLeft.find('Property Site Address')
			address = pageContentLeft[addressStart +8:addressEnd]

			if "bexar" in address.lower():
				print(acct + " is owned by bexar county - " + str(results.index(acct) +1))

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

					continue;

			# No exclusions if it reaches this point.
			print(acct + " matched all of our criteria  #" + str(results.index(acct) +1))

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

			continue;

filterListToCSV()
