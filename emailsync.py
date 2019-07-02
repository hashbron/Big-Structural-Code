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

ENTER = "u'\ue007'"

def login(driver, action_id_email, action_id_pw, pin, committee):
	driver.get('https://www.votebuilder.com/SelectCommittee.aspx')
	time.sleep(3)
	driver.find_element_by_id('OpenIDSelectorLinkLink4').click()
	time.sleep(2)
	driver.find_element_by_id('username').send_keys(action_id_email)
	time.sleep(3)
	driver.find_element_by_id('password').send_keys(action_id_pw)
	time.sleep(3)
	driver.find_element_by_xpath("//section[@id='body-content']/div[2]/div/div/div/form/fieldset/button").click()

	# Pause for 2-factor authentication IF NEEDED - assumes user also hits enter at end to get to Select Committee page
	time.sleep(5)

	select_committee(driver, committee)

	### Enter PIN ###
	# Store the xpaths of each number in the pin pad (first element is 0 to create 1-indexing)
	xpaths = [0, "//*[@id='ctl00_ContentPlaceHolderVANPage_PanelWideColumn']/div/div[1]/div[1]/div/span[2]",
	"//*[@id='ctl00_ContentPlaceHolderVANPage_PanelWideColumn']/div/div[1]/div[2]/div/span[2]",
	"//*[@id='ctl00_ContentPlaceHolderVANPage_PanelWideColumn']/div/div[1]/div[3]/div/span[2]",
	"//*[@id='ctl00_ContentPlaceHolderVANPage_PanelWideColumn']/div/div[2]/div[1]/div/span[2]",
	"//*[@id='ctl00_ContentPlaceHolderVANPage_PanelWideColumn']/div/div[2]/div[2]/div/span[2]",
	"//*[@id='ctl00_ContentPlaceHolderVANPage_PanelWideColumn']/div/div[2]/div[3]/div/span[2]",
	"//*[@id='ctl00_ContentPlaceHolderVANPage_PanelWideColumn']/div/div[3]/div[1]/div/span[2]",
	"//*[@id='ctl00_ContentPlaceHolderVANPage_PanelWideColumn']/div/div[3]/div[2]/div/span[2]",
	"//*[@id='ctl00_ContentPlaceHolderVANPage_PanelWideColumn']/div/div[3]/div[3]/div/span[2]",
	"//*[@id='ctl00_ContentPlaceHolderVANPage_PanelWideColumn']/div/div[4]/div[2]/div/span[2]"]

	# Construct the letters corresponding to PIN
	letter_pin = ""
	for num in pin:
		letter_pin = letter_pin + str(driver.find_element_by_xpath(xpaths[int(num)]).text)

	# Enter the letters corresponding to PIN
	driver.find_element_by_id('ctl00_ContentPlaceHolderVANPage_VANDetailsItemPIN_VANInputItemDetailsItemPINCode_PINCode').send_keys(letter_pin)
	time.sleep(2)

	# Click the submit button
	driver.find_element_by_id('ctl00_ContentPlaceHolderVANPage_ButtonNarrowSubmit').click()
	time.sleep(2)

	# Make sure we are in My Campaign
	driver.find_element_by_link_text('My Campaign').click()
	time.sleep(2)

def build_and_export_list(driver, today, name):
	# # Click on my list
	# driver.find_element_by_id("ctl00_ContentPlaceHolderVANPage_HyperLinkMenuViewCurrentList").click()
	# time.sleep(2)

	# Click to Create A List
	driver.find_element_by_id('ctl00_ContentPlaceHolderVANPage_HyperLinkMenuCreateANewList').click()
	time.sleep(2)

	### Add all emails ###
	# Scroll so that the Email dropdown is in view
	driver.execute_script("return arguments[0].scrollIntoView();", driver.find_element_by_id('ImageButtonSectionBatchEmailJobs'))
	time.sleep(1)
	# Drop down the Email menu
	driver.find_element_by_id('ImageButtonSectionEmailSource').click()
	time.sleep(5)
	# Add all email types
	driver.find_element_by_id('EmailTypeCombo_Input').click()
	time.sleep(2)
	driver.find_element_by_class_name("rcbCheckAllItemsCheckBox").click()
	time.sleep(2)

	### Remove all supressions ###
	# Scroll down to the Suppressions dropdown
	driver.execute_script("return arguments[0].scrollIntoView();", driver.find_element_by_id('ImageButtonSectionRoboCalls'))
	time.sleep(1)
	# Click on the Suppressions dropdown
	driver.find_element_by_id("ImageButtonSectionSuppressions").click()
	time.sleep(2)
	# Click on the "Remove all Suppressions link"
	driver.find_element_by_id("RemoveAllSuppressions").click()

	### Run Search ###
	# Scroll into the search button view
	driver.execute_script("return arguments[0].scrollIntoView();", driver.find_element_by_id('ctl00_ContentPlaceHolderVANPage_SearchRunButton'))
	time.sleep(1)
	# Click to run the search
	driver.find_element_by_id('ctl00_ContentPlaceHolderVANPage_SearchRunButton').click()
	time.sleep(10)

	### Export ###
	# Click to export
	driver.find_element_by_id('ctl00_ContentPlaceHolderVANPage_HyperLinkImageExport').click()
	time.sleep(5)
	# Choose the standard text export format
	driver.find_element_by_class_name("select2-choice").click()
	driver.find_element_by_class_name('select2-input').send_keys("Standard Text")
	driver.find_element_by_class_name('select2-input').send_keys(Keys.RETURN);
	time.sleep(2)
	# Scroll down to the Customize Export button
	driver.execute_script("return arguments[0].scrollIntoView();", driver.find_element_by_id('ctl00_ContentPlaceHolderVANPage_WizardControl_StartNavigationTemplateContainerID_ButtonStartNext'))
	time.sleep(1)
	# Click the Customize Export button
	driver.find_element_by_id('ctl00_ContentPlaceHolderVANPage_WizardControl_StartNavigationTemplateContainerID_ButtonStartNext').click()
	time.sleep(2)
	# Remove the fields: Name, Home Phone, and Primary Address (My Campaign)
	driver.find_element_by_css_selector("li.draggableBox:nth-child(2) > a:nth-child(3)").click()
	driver.find_element_by_css_selector("li.draggableBox:nth-child(2) > a:nth-child(3)").click()
	driver.find_element_by_css_selector(".close").click()
	time.sleep(2)
	# Add fields 
	# Other Email
	driver.find_element_by_class_name("select2-choice").click()
	driver.find_element_by_class_name('select2-input').send_keys("Other Email")
	driver.find_element_by_class_name('select2-input').send_keys(Keys.RETURN);
	time.sleep(2)
	# Personal Email
	driver.find_element_by_class_name("select2-choice").click()
	driver.find_element_by_class_name('select2-input').send_keys("Personal Email")
	driver.find_element_by_class_name('select2-input').send_keys(Keys.RETURN);
	time.sleep(2)
	# Work Email
	driver.find_element_by_class_name("select2-choice").click()
	driver.find_element_by_class_name('select2-input').send_keys("Work Email")
	driver.find_element_by_class_name('select2-input').send_keys(Keys.RETURN);
	#time.sleep(2)
	#Name Export File
	driver.find_element_by_class_name("form-control").click()
	driver.find_element_by_css_selector("input.form-control").send_keys(name + today)
	# Scroll down to the export button
	driver.execute_script("return arguments[0].scrollIntoView();", driver.find_element_by_css_selector('input.btn:nth-child(2)'))
	time.sleep(1)
	# Click the export button
	driver.find_element_by_css_selector('input.btn:nth-child(2)').click()
	input.btn:nth-child(2)
	time.sleep(2)

	# Click to the My Export Files link
	driver.find_element_by_link_text('My Export Files').click()
	time.sleep(5) 

	# Wait for the file to be prepared
	while(driver.find_element_by_xpath('//*[@id="ctl00_ContentPlaceHolderVANPage_gvList"]/tbody/tr[1]/td[6]').text != "Download File"):
		print("File not prepared. Refrehsing.")
		time.sleep(5)
		driver.refresh()
	# Click to download the file
	driver.find_element_by_xpath('//*[@id="ctl00_ContentPlaceHolderVANPage_gvList"]/tbody/tr[1]/td[6]').click()

def select_committee(driver, committee):
	# Open committee selector
	driver.find_element_by_id("s2id_ctl01_ContentPlaceHolderVANPage_DropDownListCommittees").click()
	time.sleep(2)
	# Enter committee name
	ActionChains(driver).send_keys(committee).perform()
	ActionChains(driver).send_keys('\ue007').perform()
	time.sleep(2)
	# Click the next button
	driver.find_element_by_css_selector("#ctl01_ContentPlaceHolderVANPage_ButtonContinue").click()
	time.sleep(5)

def logout(driver):
	# Make sure we are in the My Campaign homepage
	driver.find_element_by_link_text('My Campaign').click()
	time.sleep(2)
	# Click the account dropdown
	driver.find_element_by_css_selector('li.dropdown:nth-child(3)').click()
	time.sleep(2)
	# Click logout
	driver.find_element_by_css_selector('.action-bar-dropdown-body > li:nth-child(11) > a:nth-child(1)').click()
	time.sleep(2)

def switch_committees(driver, committee):
	# Click the account dropdown
	driver.find_element_by_css_selector('li.dropdown:nth-child(3)').click()
	time.sleep(2)
	# Click to switch committees
	driver.find_element_by_id('action-bar-dropdown-switch-context').click()
	time.sleep(2)
	driver.switch_to_frame(driver.find_element_by_name('VANRadWindowContextSwitch'))

	select_committee(driver, committee)

def upload_xls(driver, filepath, mapping_values):
	# Go to upload select data type page
	driver.get('https://www.votebuilder.com/UploadDataSelectType.aspx')
	time.sleep(2)
	# Click next
	driver.find_element_by_id('ctl00_ContentPlaceHolderVANPage_ButtonUploadSubmit').click()
	time.sleep(2)
	# Submit the file
	driver.find_element_by_id('ctl00_ContentPlaceHolderVANPage_InputFileDefault').send_keys(filepath)
	time.sleep(2)
	# Scroll down to the upload button
	driver.execute_script("return arguments[0].scrollIntoView();", driver.find_element_by_id('ctl00_ContentPlaceHolderVANPage_ButtonSubmitDefault'))
	time.sleep(2)
	# Click upload
	driver.find_element_by_id('ctl00_ContentPlaceHolderVANPage_ButtonSubmitDefault').click()
	time.sleep(60) # Wait for the file to upload

	# A view may appear that tells you certain VAN IDs in excel do not match those in the database
	# If this appears, we click the next button. Otherwise print that all IDs match
	try:
		driver.find_element_by_name('ctl00$ContentPlaceHolderVANPage$ctl05').click()
	except:
		print('All VAN IDs match.')
	time.sleep(3)

	# Select Apply Email Address from the Apply New Mappings dropdown
	Select(driver.find_element_by_id('ctl00_ContentPlaceHolderVANPage_ctl02_AddULFieldID')).select_by_value("5")
	time.sleep(5)
	driver.switch_to_frame(driver.find_element_by_name("RadWindow1"))

	# Click on the Choose Colimn from Data File radio button
	driver.find_element_by_id('ctl01_ContentPlaceHolderVANPage_myLabelCont0_Email_ToggleColumn_Email').click()
	time.sleep(2)

	# Select the desired excel column from the dropdown
	Select(driver.find_element_by_id('ctl01_ContentPlaceHolderVANPage_myLabelCont0_Email_Column_ddl_Column')).select_by_value(mapping_values[0])
	time.sleep(2)

	# Select the desired email type from the dropdown
	Select(driver.find_element_by_id('ctl01_ContentPlaceHolderVANPage_myLabelCont0_EmailTypeId_ddlEmailTypes_ddl_ddlEmailTypes')).select_by_value(mapping_values[1])
	time.sleep(2)

	# Click the next button
	driver.find_element_by_id('ctl01_ContentPlaceHolderVANPage_Next0').click()
	time.sleep(5)

	# A view may appear that tells you certain VAN IDs in excel do not match those in the database
	# If this appears, we click the next button. Otherwise print that all IDs match
	try:
		driver.find_element_by_name('ctl00$ContentPlaceHolderVANPage$ctl05').click()
	except:
		print('All VAN IDs match.')
	time.sleep(3)

	# Click the finish button
	driver.find_element_by_id('ctl00_ContentPlaceHolderVANPage_ButtonFinishUpload').click()
	time.sleep(2)

	# Click finish again in the "are you sure" pop up
	driver.find_element_by_id('ctl00_ContentPlaceHolderVANPage_FinishUploadModal__submitButton').click()
	time.sleep(3)

def WrangleData(today, name):
	# Move to downloads folder if not already there
	if (os.getcwd()[-9:] != 'Downloads'):
		os.chdir("../Downloads/")

	# Get the name of the export file
	export_file = [x for x in os.listdir() if x.startswith('StandardText' + name + today) and x.endswith(".zip")][0]

	# Unzip the export file
	zipfile.ZipFile(export_file,'r').extractall()

	# Get the name of the unzipped xls file
	export_file = export_file[:-3] + 'xls'
	file_path = str(os.getcwd()) + "/" + str(export_file)

	return file_path

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

	# Get todays date
	now = datetime.datetime.now()
	month, day = str(now.month), str(now.day) 
	if len(month) != 2:
		month = '0' + month
	if len(day) != 2:
		day = '0' + day
	date = month + day + str(now.year)

	# Setup Selenium driver
	options = webdriver.ChromeOptions()
	options.add_argument('user-data-dir=Profile')
	# options.add_argument("--headless")

	my_driver = webdriver.Chrome(options=options)

	organizing = "Elizabeth Warren for President 2020", "Organizing"
	political = "Elizabeth Warren Political 2020", "Political"

	mapping_values_other = "column1", "3"
	mapping_values_personal = "column2", "1"
	mapping_values_work = "column3", "2"

	# Export organizing data
	print("Organizing Data Exporting:")
	print("Logging in.")
	login(my_driver, action_id_email, action_id_pw, pin, organizing[0])
	print("Getting data from VAN.")
	build_and_export_list(my_driver, date, organizing[1])
	print()

	# Export political data
	print("Political Data Exporting:")
	print("Switching to Political Committee.")
	switch_committees(my_driver, political[0])
	print("Getting data from VAN.")
	build_and_export_list(my_driver, date, political[1])
	print()
	time.sleep(20) # wait for files to finish downloading

	# Wrangle the data
	print("Wrangling data.")
	organizing_filepath = WrangleData(date, organizing[1])
	political_filepath = WrangleData(date, political[1])
	print()

	# Upload the organizing data to the political committee
	print("Organizing Data Uploading:")
	print("Uploading data - other.")
	upload_xls(my_driver, organizing_filepath, mapping_values_other)
	print("Uploading data - personal.")
	upload_xls(my_driver, organizing_filepath, mapping_values_personal)
	print("Uploading data - work.")
	upload_xls(my_driver, organizing_filepath, mapping_values_work)
	print()

	# Upload the political data to the organizing committee
	print("Political Data Uploading:")
	print("Switching to Organizing committee.")
	switch_committees(my_driver, organizing[0])
	print("Uploading data - other.")
	upload_xls(my_driver, political_filepath, mapping_values_other)
	print("Uploading data - personal.")
	upload_xls(my_driver, political_filepath, mapping_values_personal)
	print("Uploading data - work.")
	upload_xls(my_driver, political_filepath, mapping_values_work)
	print()
	
	# Log out and quit the driver
	print("Logging out.")
	logout(my_driver)
	my_driver.close()
	print("Finished.")

main()