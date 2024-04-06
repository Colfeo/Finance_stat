from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

driver = webdriver.Firefox()

#driver.maximize_window()
driver.get("https://www.binance.com/en/futures-activity/leaderboard/user/um?encryptedUid=8D27A8FA0C0A726CF01A7D11E0095577")
# identify element
l = driver.find_element(By.CSS_SELECTOR, "h1")
# get text and print
print("Text is: " + l.text)
driver.close()