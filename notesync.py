import csv
import time
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import zipfile
import json
import os
import vanpy

def match(driver, tagged, csv):
	# Select Apply Notes from the Apply New Mappings dropdown
	Select(driver.find_element_by_id('ctl00_ContentPlaceHolderVANPage_ctl02_AddULFieldID')).select_by_value("30")
	time.sleep(5)
	driver.switch_to_frame(driver.find_element_by_name("RadWindow1"))

	# Click on the Choose Column from Data File radio button
	driver.find_element_by_id('ctl01_ContentPlaceHolderVANPage_myLabelCont0_NoteText_ToggleColumn_NoteText').click()
	time.sleep(2)

	# Select the desired excel column from the dropdown
	Select(driver.find_element_by_id('ctl01_ContentPlaceHolderVANPage_myLabelCont0_NoteText_Column_ddl_Column')).select_by_value("column2")
	time.sleep(2)

	# Special case for only 1 note
	try:
		driver.find_element_by_id('ctl01_ContentPlaceHolderVANPage_myLabelCont0_NoteCategoryID_ToggleColumn_NoteCategoryID').click()
		print("here")
	except:
		print("Unable to find the fucking radio button. Terminating early for " + str(csv))
		return

	if tagged:
		# Click on the Choose Column from Data File radio button
		driver.find_element_by_id('ctl01_ContentPlaceHolderVANPage_myLabelCont0_NoteCategoryID_ToggleColumn_NoteCategoryID').click()
		time.sleep(2)

		# Select the desired excel column from the dropdown
		Select(driver.find_element_by_id('ctl01_ContentPlaceHolderVANPage_myLabelCont0_NoteCategoryID_Column_ddl_Column')).select_by_value("column1")
		time.sleep(2)

	# Click the next button
	driver.find_element_by_id('ctl01_ContentPlaceHolderVANPage_Next0').click()
	time.sleep(3)

	if tagged:

		# Get the number of rows to be mapped for catagory_name 
		row_count = len(driver.find_elements_by_xpath("/html/body/form/div[6]/div/div/div[2]/div/div[1]/table/tbody/tr"))
		print(row_count)

		for row in range(1, row_count):
			# Get text of catagory name from appropriate row (+1 because the rows are 2-indexed)
			catagory_name = driver.find_element_by_xpath("//*[@id='ctl01_ContentPlaceHolderVANPage_2']/div/div[1]/table/tbody/tr["+str(row+1)+"]/td[1]").text
			print(catagory_name)
			# Select dropdown of catagory_name in the corresponding row
			Select(driver.find_element_by_xpath("//*[@id='ctl01_ContentPlaceHolderVANPage_2']/div/div[1]/table/tbody/tr["+str(row + 1)+"]/td[3]/span/select")).select_by_visible_text(catagory_name)
			time.sleep(0.1)

		# Click next
		driver.find_element_by_id('ctl01_ContentPlaceHolderVANPage_Next2').click()
		time.sleep(5)

	# Click Finish
	#driver.find_element_by_id('ctl00_ContentPlaceHolderVANPage_ButtonFinishUpload').click()
	time.sleep(5)

	# Click Finish in popup
	#driver.find_element_by_id('ctl00_ContentPlaceHolderVANPage_FinishUploadModal__submitButton').click()
	time.sleep(5)

def main():
	# Get login credentials from secrets file
	try:
		secrets = json.load(open('secrets.json'))
	except IOError:
		print("No secrets file found.")
		sys.exit(1)
	except json.JSONDecodeError:
		print("Secrets file is not valid json.")

	action_id_email = secrets['van']['user']
	action_id_pw = secrets['van']['password']
	pin = secrets['van']['pin']

	options = webdriver.ChromeOptions()
	options.add_argument('user-data-dir=Profile')
	options.add_argument("--start-maximized");
	my_driver = webdriver.Chrome(options=options)

	twofa = False
	organizing = "Elizabeth Warren for President 2020"
	political = "Elizabeth Warren Political 2020"

	csv1 = "into_campaign_tagged_political.csv"
	csv2 = "into_campaign_untagged_political.csv"
	csv3 = "into_political_tagged_campaign.csv"
	csv4 = "into_political_untagged_campaign.csv"

	path = str(os.getcwd()) + "/"

	print("Logging in to VAN and uploading to Campign Committee")
	vanpy.login(my_driver, action_id_email, action_id_pw, pin, organizing, twofa)
	vanpy.upload(my_driver, path + csv1)
	match(my_driver, True, csv1)
	vanpy.upload(my_driver, path + csv2)
	match(my_driver, False, csv2)

	print("Switching committees and uploading to Political Committee")
	vanpy.switch_committees(my_driver, political)
	vanpy.upload(my_driver, path + csv3)
	match(my_driver, True, csv3)
	vanpy.upload(my_driver, path + csv4)
	match(my_driver, False, csv4)

	vanpy.logout(my_driver)

main()