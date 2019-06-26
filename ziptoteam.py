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
import glob
import requests
import civis

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

def upload(driver, filepath):
	# Go to upload select data type page
	driver.get('https://www.votebuilder.com/UploadDataSelectType.aspx')
	time.sleep(2)
	# Click next
	driver.find_element_by_id('ctl00_ContentPlaceHolderVANPage_ButtonUploadSubmit').click()
	time.sleep(2)
	# Submit file name
	driver.find_element_by_id('ctl00_ContentPlaceHolderVANPage_InputFileDefault').send_keys(filepath)
	time.sleep(5)
	# Scroll down to the upload button
	driver.execute_script("return arguments[0].scrollIntoView();", driver.find_element_by_id('ctl00_ContentPlaceHolderVANPage_ButtonSubmitDefault'))
	time.sleep(2)
	# Click upload
	driver.find_element_by_id('ctl00_ContentPlaceHolderVANPage_ButtonSubmitDefault').click()
	time.sleep(15)

	# A view may appear that tells you certain VAN IDs in excel do not match those in the database
	# If this appears, we click the next button. Otherwise print that all IDs match
	try:
		driver.find_element_by_name('ctl00$ContentPlaceHolderVANPage$ctl05').click()
	except:
		print('All VAN IDs match.')
	time.sleep(3)

	# Select Warren Activity Region from the Apply New Mappings dropdown
	Select(driver.find_element_by_id('ctl00_ContentPlaceHolderVANPage_ctl02_AddULFieldID')).select_by_value("270")
	time.sleep(5)
	driver.switch_to_frame(driver.find_element_by_name("RadWindow1"))
	# Toggle the 'Choose Column from Data File' radio button
	driver.find_element_by_id('ctl01_ContentPlaceHolderVANPage_myLabelCont0_CF129_ToggleColumn_CF129').click()
	time.sleep(3)
	# Set Activity Region to region_name
	Select(driver.find_element_by_id('ctl01_ContentPlaceHolderVANPage_myLabelCont0_CF129_Column_ddl_Column')).select_by_value("column1")
	time.sleep(3)
	# Set Activity Organizer to fo_name
	Select(driver.find_element_by_id('ctl01_ContentPlaceHolderVANPage_myLabelCont0_CF130_Column_ddl_Column')).select_by_value("column2")
	time.sleep(3)
	# Set Activity Team to team_name
	Select(driver.find_element_by_id('ctl01_ContentPlaceHolderVANPage_myLabelCont0_CF131_Column_ddl_Column')).select_by_value("column3")
	time.sleep(3)
	# Click next
	driver.find_element_by_id('ctl01_ContentPlaceHolderVANPage_Next0').click()
	time.sleep(10)

	# Get the number of rows to be mapped from region_name to Activity Region
	row_count_region = len(driver.find_elements_by_xpath("//*[@id='ctl01_ContentPlaceHolderVANPage_1']/div/div[1]/table/tbody/tr"))

	for row in range(1, row_count_region): # Start at 1 to ignore the header row
		# Get text of region name from appropriate row (+1 because the rows are 2-indexed)
		region_name = driver.find_element_by_xpath("//*[@id='ctl01_ContentPlaceHolderVANPage_1']/div/div[1]/table/tbody/tr["+str(row+1)+"]/td[1]").text
		# Select dropdown of region_name in the corresponding row
		Select(driver.find_element_by_xpath("//*[@id='ctl01_ContentPlaceHolderVANPage_1']/div/div[1]/table/tbody/tr["+str(row+1)+"]/td[3]/span/select")).select_by_visible_text(region_name)
		time.sleep(.1)

	# Click next
	driver.find_element_by_id('ctl01_ContentPlaceHolderVANPage_Next1').click()
	time.sleep(5)

	# Get the number of rows to be mapped from fo_name to Activity Organizer
	row_count_foname = len(driver.find_elements_by_xpath("//*[@id='ctl01_ContentPlaceHolderVANPage_2']/div/div[1]/table/tbody/tr"))

	for row in range(1, row_count_foname): # Start at 1 to ignore the header row
		# Get text of fo_name from appropriate row (+1 because the rows are 2-indexed)
		fo_name = driver.find_element_by_xpath("//*[@id='ctl01_ContentPlaceHolderVANPage_2']/div/div[1]/table/tbody/tr["+str(row+1)+"]/td[2]").text
		# Select the dropdown of fo_name in the corresponding row
		driver.execute_script("return arguments[0].scrollIntoView();", driver.find_element_by_xpath("//*[@id='ctl01_ContentPlaceHolderVANPage_2']/div/div[1]/table/tbody/tr["+str(row+1)+"]/td[4]/span/select"))
		Select(driver.find_element_by_xpath("//*[@id='ctl01_ContentPlaceHolderVANPage_2']/div/div[1]/table/tbody/tr["+str(row+1)+"]/td[4]/span/select")).select_by_visible_text(fo_name)
		time.sleep(.1)

	driver.find_element_by_id('ctl01_ContentPlaceHolderVANPage_Next2').click()
	time.sleep(5)

	# Get the number of rows to be mapped from team_name to Activity Organizer
	row_count_teamname = len(driver.find_elements_by_xpath("//*[@id='ctl01_ContentPlaceHolderVANPage_3']/div/div[1]/table/tbody/tr"))

	for row in range(1, row_count_teamname): # Start at 1 to ignore the header row
		# Get text of team_name from appropriate row (+1 because the rows are 2-indexed)
		team_name = driver.find_element_by_xpath("//*[@id='ctl01_ContentPlaceHolderVANPage_3']/div/div[1]/table/tbody/tr["+str(row+1)+"]/td[3]").text
		# Select the dropdown of team_name in the corresponding row
		driver.execute_script("return arguments[0].scrollIntoView();", driver.find_element_by_xpath("//*[@id='ctl01_ContentPlaceHolderVANPage_3']/div/div[1]/table/tbody/tr["+str(row+1)+"]/td[5]/span/select"))
		Select(driver.find_element_by_xpath("//*[@id='ctl01_ContentPlaceHolderVANPage_3']/div/div[1]/table/tbody/tr["+str(row+1)+"]/td[5]/span/select")).select_by_visible_text(team_name)
		time.sleep(0.1)

	driver.find_element_by_id('ctl01_ContentPlaceHolderVANPage_Next3').click()
	time.sleep(5)

	#driver.find_element_by_id('ctl00_ContentPlaceHolderVANPage_ButtonFinishUpload').click()
	time.sleep(5)

	#driver.find_element_by_id('ctl00_ContentPlaceHolderVANPage_FinishUploadModal__submitButton').click()
	time.sleep(5)

	time.sleep(10000)

def download_zip_to_team(CIVIS_API_KEY, date, driver):
	script = ""
	with open('ziptoteam_query.txt', 'r') as myfile:
  		script = myfile.read()

	client = civis.APIClient(api_key=CIVIS_API_KEY)
	fut = civis.io.civis_to_csv(filename="zip_to_team_" + str(date) + ".csv", sql=script, database="Warren for MA", job_name="zip_to_team_" + str(date), client=client)
	results = fut.result()
	filename = results['output'][0]['output_name']
	path = results['output'][0]['path']

	driver.get(path)
	time.sleep(30)

	os.chdir("../Downloads/")
	file_path = str(os.getcwd()) + "/" + str(filename)

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

	CIVIS_API_KEY = secrets['civis']['api_key']
	action_id_email = secrets['van']['user']
	action_id_pw = secrets['van']['password']
	pin = secrets['van']['pin']

	# Get todays date
	now = datetime.datetime.now()
	month = str(now.month) 
	if len(month) != 2:
		month = '0' + month
	date = month + str(now.day) + str(now.year)

	committee_name = "Elizabeth Warren for President 2020"

	# Setup Selenium driver
	options = webdriver.ChromeOptions()
	options.add_argument('user-data-dir=Profile')
	# options.add_argument("--headless")

	my_driver = webdriver.Chrome(options=options)

	print("Running civis query.")
	path = download_zip_to_team(CIVIS_API_KEY, date, my_driver)
	print("Logging in.")
	login(my_driver, action_id_email, action_id_pw, pin, committee_name)
	print("Uploading csv.")
	upload(my_driver, path)
	print("Logging out.")
	logout(my_driver)
	my_driver.close()

main()



