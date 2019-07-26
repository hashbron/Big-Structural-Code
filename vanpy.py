import csv
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import zipfile
import json
import os
import glob
import civis
import requests
#########################################################
#                  Welcome to VANPY                     #
#########################################################

# VANPY is a pyhton library that uses Selenium to script VAN. 
# Please be careful when useing these functions so as to not get caught by VAN!

# The functions below are split into 3 sections:

#	1. Account Functions - these include methods for logging in, loggin out, switching committees, and other activities related to your account
#	2. List Functions - these include functions for the process of building a list
#	3. Upload Functions - these include function for the bulk upload process

#########################################################
#            SECTION 1 - Account Functions              #
#########################################################

# This function opens votebuilder.com and logs into the specified committee using the specified login credentials
# @params driver - is the Selenium webdriver
#         aciton_id_email - is a string of the email of the Action ID account to be used
#		  action_id_pw - is a string of the password of the Action ID account to be used
#		  pin - is a string the four digit pin for the Action ID account to be used 
#		  committee - is a string of the name of the Committee to be logged in to
#		  twofa - is a boolean flag that when set to true pauses for the user to enter the 2-factor authentification code
# @ends   on the My Campaign home screen

def login(driver, action_id_email, action_id_pw, pin, committee, twofa):
	driver.get('https://www.votebuilder.com/SelectCommittee.aspx')
	time.sleep(3)
	driver.find_element_by_id('OpenIDSelectorLinkLink4').click()
	time.sleep(2)
	driver.find_element_by_id('username').send_keys(action_id_email)
	time.sleep(3)
	driver.find_element_by_id('password').send_keys(action_id_pw)
	time.sleep(3)
	driver.find_element_by_xpath("//section[@id='body-content']/div[2]/div/div/div/form/fieldset/button").click()

	# Pause for 2-factor authentication IF FLAG IS SET - assumes user also hits enter at end to get to Select Committee page
	if (twofa):
		time.sleep(30)
	else:
		time.sleep(5)

	select_committee(driver, committee)

	### Enter PIN ###
	# Store the xpaths of each number in the pin pad (first element is 0 to create 1-indexing)
	xpaths = ["//*[@id='ctl00_ContentPlaceHolderVANPage_PanelWideColumn']/div/div[4]/div[2]/div/span[2]",
	"//*[@id='ctl00_ContentPlaceHolderVANPage_PanelWideColumn']/div/div[1]/div[1]/div/span[2]",
	"//*[@id='ctl00_ContentPlaceHolderVANPage_PanelWideColumn']/div/div[1]/div[2]/div/span[2]",
	"//*[@id='ctl00_ContentPlaceHolderVANPage_PanelWideColumn']/div/div[1]/div[3]/div/span[2]",
	"//*[@id='ctl00_ContentPlaceHolderVANPage_PanelWideColumn']/div/div[2]/div[1]/div/span[2]",
	"//*[@id='ctl00_ContentPlaceHolderVANPage_PanelWideColumn']/div/div[2]/div[2]/div/span[2]",
	"//*[@id='ctl00_ContentPlaceHolderVANPage_PanelWideColumn']/div/div[2]/div[3]/div/span[2]",
	"//*[@id='ctl00_ContentPlaceHolderVANPage_PanelWideColumn']/div/div[3]/div[1]/div/span[2]",
	"//*[@id='ctl00_ContentPlaceHolderVANPage_PanelWideColumn']/div/div[3]/div[2]/div/span[2]",
	"//*[@id='ctl00_ContentPlaceHolderVANPage_PanelWideColumn']/div/div[3]/div[3]/div/span[2]"]

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

# This function selects a committee from the committee selection dropdown page
# @params driver - is the Selenium webdriver
#		  committee - is a string of the name of the committee to be logged in to
# @starts on the committee slection dropdown page. This can be the entire page, or a iFrame within a page
# @ends   on the page following the committee slection page - this may be the home page for My Campaign or My Voters

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

# This function switched from one committee to another
# @params driver - is the Selenium webdriver
#		  committee - is a string of the name of the committee to be logged in to
# @ends   on the page following the committee slection page - this may be the home page for My Campaign or My Voters

def switch_committees(driver, committee):
	# Click the account dropdown
	driver.find_element_by_css_selector('li.dropdown:nth-child(3)').click()
	time.sleep(2)
	# Click to switch committees
	driver.find_element_by_id('action-bar-dropdown-switch-context').click()
	time.sleep(2)
	driver.switch_to_frame(driver.find_element_by_name('VANRadWindowContextSwitch'))

	select_committee(driver, committee)

# This function logs out of votebuilder
# @params driver - is the Selenium webdriver
# @ends   on the page following a logout

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

# This function goes to the My Campaign homescreen from whatever page you are on
# @params driver - is the Selenium webdriver
# @ends   on the my campaign home screen

def go_to_my_campaign(driver):
	driver.find_element_by_link_text('My Campaign').click()
	time.sleep(2)

#########################################################
#              SECTION 2 - List Functions               #
#########################################################

# This function clicks the create a list button on the home page
# @params driver - is the Selenium webdriver
# @ends   on the create a list view

def create_a_list(driver):
	# Click Create A List
	driver.find_element_by_id('ctl00_ContentPlaceHolderVANPage_HyperLinkMenuCreateANewList').click()
	time.sleep(2)

# This function removes all suppressions from the list being built
# @params driver - is the Selenium webdriver
# @starts on the create a list view
# @ends   on the create a list view

def remove_all_suppressions(driver):
	# Scroll down to the Suppressions dropdown
	driver.execute_script("return arguments[0].scrollIntoView();", driver.find_element_by_id('ImageButtonSectionRoboCalls'))
	time.sleep(1)
	# Click on the Suppressions dropdown
	driver.find_element_by_id("ImageButtonSectionSuppressions").click()
	time.sleep(2)
	# Click on the "Remove all Suppressions link"
	driver.find_element_by_id("RemoveAllSuppressions").click()

# This function runs the search created in the create a list view
# @params driver - is the Selenium webdriver
# @starts on the create a list view
# @ends   on the my list view

def run_search(driver):
	# Scroll into the search button view
	driver.execute_script("return arguments[0].scrollIntoView();", driver.find_element_by_id('ctl00_ContentPlaceHolderVANPage_SearchRunButton'))
	time.sleep(1)
	# Click to run the search
	driver.find_element_by_id('ctl00_ContentPlaceHolderVANPage_SearchRunButton').click()
	time.sleep(10)

# This function runs the search created in the create a list view and then clicks to export that search
# @params driver - is the Selenium webdriver
# @starts on the create a list view
# @ends   on the first export view

def run_search_and_export(driver):
	run_search(driver)
	# Click to export
	driver.find_element_by_id('ctl00_ContentPlaceHolderVANPage_HyperLinkImageExport').click()
	time.sleep(5)

# This function clicks to export a list
# @params driver - is the Selenium webdriver
# @starts on the my list view
# @ends   on the first export view

def export(driver):
	# Click to export
	driver.find_element_by_id('ctl00_ContentPlaceHolderVANPage_HyperLinkImageExport').click()
	time.sleep(5)

# This function selects a custom export and removes all of the initial fields (Name, Home Phone, Primary Address)
# @params driver - is the Selenium webdriver
# @starts on the first export view
# @ends   on the custom export view with all fields removed (except VANID)

def custom_export_remove_fields(driver):
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

# This function adds a field to a custom export format
# @params driver - is the Selenium webdriver
#		  field - is a string containing the exact text for the field name as it appears in te dropdown
# @starts on the custom export view
# @ends   on the custom export view 

def custom_export_add_field(driver, field):
	driver.find_element_by_class_name("select2-choice").click()
	driver.find_element_by_class_name('select2-input').send_keys(field)
	driver.find_element_by_class_name('select2-input').send_keys(Keys.RETURN);
	time.sleep(2)

#########################################################
#             SECTION 3 - Upload Functions              #
#########################################################

# This function loads a file using bulk upload by VANID to be uploaded into VAN. It waits 60 seconds for the file to upload
# @params driver - is the Selenium webdriver
#		  filepath - is a string containing the complete filepath to the desired file to be uploaded
#		  waittime - is an int of the number of seconds the program should wait for the file to upload
#			     	 this value is set to 60 if left blank
# @ends   on the file upload page that allows you to define a mapping between your file and VAN

def upload(driver, filepath, waittime=60):
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
	time.sleep(waittime)

	# A view may appear that tells you certain VAN IDs in excel do not match those in the database
	# If this appears, we click the next button. Otherwise print that all IDs match
	try:
		driver.find_element_by_name('ctl00$ContentPlaceHolderVANPage$ctl05').click()
	except:
		print('All VAN IDs match.')
	time.sleep(3)

#########################################################
#                      VARIABLES                        #
#########################################################

ENTER = "u'\ue007'"

