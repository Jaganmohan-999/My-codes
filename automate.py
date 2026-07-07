from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time

driver = webdriver.Chrome()
driver.get("YOUR_URL")

# login steps here...

time.sleep(5)

actions = ActionChains(driver)

# Loop through locations (pseudo)
locations = driver.find_elements(By.CLASS_NAME, "location-item")

for loc in locations:
    loc.click()
    time.sleep(3)

    # Select all checkbox
    driver.find_element(By.XPATH, "//input[@type='checkbox']").click()

    # Hover on Export button
    export_btn = driver.find_element(By.XPATH, "//button[contains(., 'Export')]")
    actions.move_to_element(export_btn).perform()
    time.sleep(1)

    # Click Excel option
    excel_option = driver.find_element(By.XPATH, "//span[contains(., 'Excel')]")
    excel_option.click()

    time.sleep(5)  # wait for download