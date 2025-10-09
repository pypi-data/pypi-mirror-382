from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pyotp
import time
import requests
import logging


def auto_login(API_KEY, SECRET_KEY, USER_ID, PIN, TOTP_SECRET, redirect_url="https://127.0.0.1:5000/"):
    try:
        options = Options()
        options.add_argument("--no-sandbox")
        options.add_argument("--headless")
        options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(options=options)
        url = f"https://api-v2.upstox.com/login/authorization/dialog?response_type=code&client_id={API_KEY}&redirect_uri={redirect_url}"
        driver.get(url)

        WebDriverWait(driver, 30).until(lambda d: d.execute_script("return document.readyState") == "complete")
        driver.find_element(By.ID, "mobileNum").send_keys(USER_ID)
        driver.find_element(By.ID, "getOtp").click()

        otp = pyotp.TOTP(TOTP_SECRET).now()
        time.sleep(5)
        driver.find_element(By.ID, "otpNum").send_keys(otp)
        driver.find_element(By.ID, "continueBtn").click()

        pin_input = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '//*[@id="pinCode"]')))
        pin_input.send_keys(PIN)

        current_url = driver.current_url
        driver.find_element(By.ID, "pinContinueBtn").click()
        WebDriverWait(driver, 30).until(EC.url_changes(current_url))

        redirected_url = driver.current_url.split("?code=")[1]

        token_url = "https://api.upstox.com/v2/login/authorization/token"
        headers = {
            "accept": "application/json",
            "Api-Version": "2.0",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {
            "code": redirected_url,
            "client_id": API_KEY,
            "client_secret": SECRET_KEY,
            "redirect_uri": redirect_url,
            "grant_type": "authorization_code",
        }

        response = requests.post(token_url, headers=headers, data=data)
        response.raise_for_status()
        access_token = response.json().get("access_token")

        driver.quit()
        print("Successfully logged in!")
        return access_token

    except Exception as e:
        logging.error(f"Login failed: {e}")
        return None


url = "https://api-hft.upstox.com/v2/order/retrieve-all"
# url = "https://api-sandbox.upstox.com/v2/order/retrieve-all"   # for Sandbox api use this urls

def get_all_orders(access_token: str, url: str):
    session = requests.Session()
    session.headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }
    try:
        response = session.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, ValueError) as e:
        raise RuntimeError(f"Failed to fetch orders: {e}")
    

url = 'https://api.upstox.com/v2/order/positions/exit'


def exit_orders(access_token: str, url = "https://api.upstox.com/v2/order/positions/exit"):
    url = 'https://api.upstox.com/v2/order/positions/exit'
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {access_token}',
    }
    data = {}
    try:
        response = requests.post(url, json=data, headers=headers)
        print('Response Code:', response.status_code)
        print('Response Body:', response.json())
    except Exception as e:
        print('Error:', str(e))
