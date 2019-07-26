import csv
import time
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import json
import os
import civis
import vanpy

def upload_zip_to_team(driver, filepath):
	# Upload file
	vanpy.upload(driver, filepath, waittime=20)
	# Select Warren Activity Region from the Apply New Mappings dropdown
	Select(driver.find_element_by_id('ctl00_ContentPlaceHolderVANPage_ctl02_AddULFieldID')).select_by_value("575")
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

	driver.find_element_by_id('ctl00_ContentPlaceHolderVANPage_ButtonFinishUpload').click()
	time.sleep(5)

	driver.find_element_by_id('ctl00_ContentPlaceHolderVANPage_FinishUploadModal__submitButton').click()
	time.sleep(5)

def upload_OOS_vols(driver, filepath):
	# Upload file
	vanpy.upload(driver, filepath, waittime=20)
	# Select Warren Activity Region from the Apply New Mappings dropdown
	Select(driver.find_element_by_id('ctl00_ContentPlaceHolderVANPage_ctl02_AddULFieldID')).select_by_value("1")
	time.sleep(5)
	driver.switch_to_frame(driver.find_element_by_name("RadWindow1"))
	# Select the activist code OOS
	Select(driver.find_element_by_id('ctl01_ContentPlaceHolderVANPage_myLabelCont0_ActivistCodeID_ACValue_ddl_ACValue')).select_by_value("4538205")
	time.sleep(5)
	# Click next
	driver.find_element_by_id('ctl01_ContentPlaceHolderVANPage_Next0').click()
	time.sleep(5)

	driver.find_element_by_id('ctl01_ContentPlaceHolderVANPage_Next3').click()
	time.sleep(5)

	driver.find_element_by_id('ctl00_ContentPlaceHolderVANPage_ButtonFinishUpload').click()
	time.sleep(5)

	driver.find_element_by_id('ctl00_ContentPlaceHolderVANPage_FinishUploadModal__submitButton').click()
	time.sleep(5)


def download_zip_to_team(CIVIS_API_KEY, date):
	# Get the SQL query from a txt file
	script = ""
	with open('ziptoteam_query.txt', 'r') as myfile:
  		script = myfile.read()

  	# Setup the civis client
	client = civis.APIClient(api_key=CIVIS_API_KEY)
	# Run the civis query
	fut = civis.io.civis_to_csv(filename="zip_to_team_" + str(date) + ".csv", sql=script, database="Warren for MA", job_name="zip_to_team_" + str(date), client=client)
	# Wait for query results
	results = fut.result()
	filename = results['output'][0]['output_name'] # Get CSV filename from the results
	filepath = str(os.getcwd()) + "/" + str(filename) # Get the complete filepath to the CSV (stored in current directory by default)
	return filepath

def download_OOS_vols(CIVIS_API_KEY, date):
	# Get the SQL query from a txt file
	script = ""
	with open('OOS_query.txt', 'r') as myfile:
  		script = myfile.read()

  	# Setup the civis client
	client = civis.APIClient(api_key=CIVIS_API_KEY)
	# Run the civis query
	fut = civis.io.civis_to_csv(filename="OOS_vols_" + str(date) + ".csv", sql=script, database="Warren for MA", job_name="OOS_vols_" + str(date), client=client)
	# Wait for query results
	results = fut.result()
	filename = results['output'][0]['output_name'] # Get CSV filename from the results
	filepath = str(os.getcwd()) + "/" + str(filename) # Get the complete filepath to the CSV (stored in current directory by default)
	return filepath

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

	committee_name = "Elizabeth Warren for President 2020"

	options = webdriver.ChromeOptions()
	options.add_argument('user-data-dir=Profile')
	options.add_argument("--start-maximized")
	# options.add_argument("--headless")
	my_driver = webdriver.Chrome(chrome_options=options)

	# Get todays date
	now = datetime.datetime.now()
	month, day = str(now.month), str(now.day) 
	if len(month) != 2:
		month = '0' + month
	if len(day) != 2:
		day = '0' + day
	date = month + day + str(now.year)

	# Run civis query and get the filepath to the CSV
	print("Running civis queries.")
	path_zip = download_zip_to_team(CIVIS_API_KEY, date)
	path_oos = download_OOS_vols(CIVIS_API_KEY, date)

	print("Logging in to VAN.")
	vanpy.login(my_driver, action_id_email, action_id_pw, pin, committee_name, False)
	print("Uploading csvs.")
	upload_zip_to_team(my_driver, path_zip)
	upload_OOS_vols(my_driver, path_oos)
	print("Logging out.")
	vanpy.logout(my_driver)

main()



