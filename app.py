from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import time

# Configuration
portal_url = "http://202.168.87.90/StudentPortal/"
password_reset_url = portal_url + "ForgetPassword.aspx"
login_url = portal_url + "Login.aspx"
data_url = portal_url + "default.aspx"
username_prefix = "2022UGEC"
password = "1"
username_range = range(1, 118)  # 001 to 120

# Selenium Setup
driver_path = "C:\\Users\\HP Laptop\\Downloads\\chromedriver-win64\\chromedriver-win64\\chromedriver.exe"

service = Service(driver_path)
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Run browser in headless mode for automation
options.add_argument("--disable-gpu")
driver = webdriver.Chrome(service=service, options=options)

# Wait Wrapper
wait = WebDriverWait(driver, 10)

# Function to change passwords
def change_password(username):
    driver.get(password_reset_url)
    wait.until(EC.presence_of_element_located((By.ID, "txt_username")))

    driver.find_element(By.ID, "txt_username").send_keys(username)
    driver.find_element(By.ID, "txtnewpass").send_keys(password)
    driver.find_element(By.ID, "txtConfirmpass").send_keys(password)
    driver.find_element(By.ID, "btnSubmit").click()

    # Handle the alert dialog
    try:
        WebDriverWait(driver, 5).until(EC.alert_is_present())
        alert = driver.switch_to.alert
        print(f"Alert detected: {alert.text}")
        alert.accept()  # Dismiss the alert
    except Exception as e:
        print(f"No alert detected: {e}")

    time.sleep(2)  # Allow time for the page to update


# Function to login and fetch data
def fetch_student_data(username):
    # Step 1: Log in to the portal
    driver.get(login_url)
    wait.until(EC.presence_of_element_located((By.ID, "txt_username")))

    driver.find_element(By.ID, "txt_username").send_keys(username)
    driver.find_element(By.ID, "txt_password").send_keys(password)
    driver.find_element(By.ID, "btnSubmit").click()

    time.sleep(2)  # Allow time for the login to complete

    # Step 2: Navigate to the data URL and extract hidden fields
    driver.get(data_url)
    wait.until(EC.presence_of_element_located((By.NAME, "__VIEWSTATE")))

    # Extract hidden fields required for the POST request
    viewstate = driver.find_element(By.NAME, "__VIEWSTATE").get_attribute("value")
    eventvalidation = driver.find_element(By.NAME, "__EVENTTARGET").get_attribute("value")
    viewstategenerator = driver.find_element(By.NAME, "__EVENTARGUMENT").get_attribute("value")
    hfidno = driver.find_element(By.NAME, "hfIdno").get_attribute("value")

    # Step 3: Create the payload
    payload = {
        "__VIEWSTATE": viewstate,
        "__EVENTTARGET": eventvalidation,
        "__EVENTARGUMENT": viewstategenerator,
        "ddlSemester": "5",  # Set to Semester 5 as required
        "hfIdno": hfidno,
        "btnimgShowResult.x": "51",
        "btnimgShowResult.y": "2",
        "hdfidno": hfidno
    }

    # Step 4: Extract cookies for the session
    cookies = driver.get_cookies()
    session = requests.Session()
    for cookie in cookies:
        session.cookies.set(cookie['name'], cookie['value'])

    # Step 5: Send the POST request
    response = session.post(data_url, data=payload)
    return response.text


# Main Automation Loop
all_data = {}

try:
    for i in username_range:
        username = f"{username_prefix}{i:03}"

        print(f"Processing {username}...")

        # Step 1: Change Password
        change_password(username)

        # Step 2: Fetch Data
        student_data = fetch_student_data(username)

        # Store the fetched data
        all_data[username] = student_data

finally:
    driver.quit()

# Save the data to a file
with open("student_data.json", "w") as f:
    import json
    json.dump(all_data, f)

print("Data collection complete. Saved to student_data.json")
