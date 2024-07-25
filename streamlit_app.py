import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from dotenv import load_dotenv
from twocaptcha import TwoCaptcha
from urllib.parse import urlparse

# Load environment variables
load_dotenv()
TWOCAPTCHA_API_KEY = os.getenv('TWOCAPTCHA_API_KEY', 'd5fa15aa1ebe69e79826793890792f77')  # Replace with your actual API key

# Function to solve captcha using 2Captcha
def solve_captcha(driver, site_key, url):
    solver = TwoCaptcha(TWOCAPTCHA_API_KEY)
    try:
        result = solver.recaptcha(sitekey=site_key, url=url)
        response_code = result['code']
        driver.execute_script(f'document.getElementById("g-recaptcha-response").innerHTML = "{response_code}";')
        return True
    except Exception as e:
        print(f"Captcha solving error: {e}")
        return False

# Function to perform search and click
def get_url(search_url, proxy, search_keyword="keyword"):
    try:
        options = webdriver.ChromeOptions()
        if proxy:
            options.add_argument(f'--proxy-server={proxy["server"]}:{proxy["port"]}')

        driver = webdriver.Chrome(options=options)
        driver.get("https://www.google.com/")

        # Wait for the search box to load and then perform search
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "q"))
        )
        search_box.send_keys(search_keyword)
        search_box.send_keys(Keys.RETURN)

        # Wait for search results to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.g"))
        )

        # Solve CAPTCHA if present
        try:
            captcha_box = driver.find_element(By.CLASS_NAME, 'g-recaptcha')
            site_key = captcha_box.get_attribute('data-sitekey')
            solve_captcha(driver, site_key, driver.current_url)
        except:
            pass

        elements = driver.find_elements(By.CSS_SELECTOR, 'div.g')
        for element in elements:
            try:
                anchor = element.find_element(By.TAG_NAME, 'a')
                url = anchor.get_attribute('href')
                if search_url in url.lower():
                    anchor.click()
                    break
            except Exception as e:
                print(f"Error finding or clicking on search result: {e}")

        driver.quit()
    except Exception as e:
        print(f"Error during browser automation: {e}")

# Function to create proxy accounts
def make_number_list(start, end, n):
    base_list = list(range(start, end+1))
    num_list = [base_list[i % len(base_list)] for i in range(n)]
    return num_list

def get_proxy_accounts(num_of_proxy, proxy_server, proxy_username, proxy_password, start_port, end_port):
    proxy_accounts = []
    port_list = make_number_list(start_port, end_port, num_of_proxy)
    for i in range(num_of_proxy):
        proxy_account = {
            "server": proxy_server,
            "port": port_list[i],
            "username": proxy_username,
            "password": proxy_password
        }
        proxy_accounts.append(proxy_account)
    return proxy_accounts

# Main function to run tasks
def main(url_list, proxy_server, proxy_username, proxy_password, start_port, end_port):
    task_list = url_list
    proxy_accounts = get_proxy_accounts(len(task_list), proxy_server, proxy_username, proxy_password, start_port, end_port)
    for i in range(len(task_list)):
        get_url(search_url=task_list[i].get("search_url"), proxy=proxy_accounts[i], search_keyword=task_list[i].get("search_keyword"))

# Function to extract domain from URL
def extract_domain(url):
    url = url.lower()
    if not ("http://" in url or "https://" in url):
        url = "http://" + url
    domain = urlparse(url).netloc
    if 'www.' in domain:
        return domain.replace('www.', '')
    else:
        return domain

# Function to parse the search file
def parse_file(file):
    search_list = []
    content = file.read().decode('utf-8')  # Decode the file content to string
    lines = content.splitlines()
    for line in lines:
        search_dict = {}
        parts = line.split(" ", 1)  # split at the first space
        if len(parts) == 2:
            search_dict["search_url"] = extract_domain(parts[0])
            search_dict["search_keyword"] = parts[1].strip()  # remove the trailing newline
            search_list.append(search_dict)
    return search_list

# Streamlit UI
st.title('Auto-Click Bot')

# Proxy settings
proxy_username = st.text_input('Proxy Username')
proxy_password = st.text_input('Proxy Password', type='password')
proxy_address = st.text_input('Proxy Address')
proxy_start_port = st.number_input('Proxy Start Port', min_value=10000, max_value=10019)
proxy_end_port = st.number_input('Proxy End Port', min_value=10000, max_value=10019)

# Search file upload
search_file = st.file_uploader('Upload search.txt file', type='txt')

# Start button
if st.button('Start'):
    if search_file is not None:
        url_list = parse_file(search_file)
        main(url_list, proxy_address, proxy_username, proxy_password, proxy_start_port, proxy_end_port)
        st.write("Completed all iterations")
    else:
        st.write("Please upload the search.txt file")
