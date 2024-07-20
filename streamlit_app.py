import streamlit as st
from playwright.async_api import async_playwright
import asyncio
import os
from dotenv import load_dotenv
from twocaptcha import TwoCaptcha
from urllib.parse import urlparse
import random

# Load environment variables
load_dotenv()
TWOCAPTCHA_API_KEY = os.getenv('TWOCAPTCHA_API_KEY')

# Function to solve captcha
async def solve_captcha(page):
    solver = TwoCaptcha(TWOCAPTCHA_API_KEY)
    try:
        recaptcha_element = await page.query_selector('div.g-recaptcha')
        await page.wait_for_load_state() 
        if recaptcha_element:
            site_key = await recaptcha_element.get_attribute('data-sitekey')
            data_s = await recaptcha_element.get_attribute('data-s')
            response = solver.recaptcha(
                sitekey=site_key,
                url=page.url,
                data_s=data_s
            )
            code = response['code']
            response_textarea = await recaptcha_element.query_selector('textarea#g-recaptcha-response')

            if response_textarea:
                await response_textarea.evaluate('el => el.value = "{}"'.format(code))

            await page.wait_for_load_state()  
    except Exception as e:
        print(e)

# Function to perform search and click
async def get_url(search_url, proxy_account, search_keyword="keyword", proxy_option=False):
    async with async_playwright() as p:
        proxy = proxy_account        
        browser = None
        page = None
        while True:
            try:
                if proxy_option:
                    browser = await p.chromium.launch(headless=False, proxy=proxy)
                else:
                    browser = await p.chromium.launch(headless=False)
                context = await browser.new_context()
                page = await context.new_page()
                await page.goto("https://www.google.com/")
                await solve_captcha(page)
                await page.fill('css=[name="q"]', search_keyword)
                await page.press('css=[name="q"]', "Enter")
                await solve_captcha(page)

                elements = await page.query_selector_all('div.v5yQqb')
                await page.wait_for_load_state()
                
                for element in elements:
                    anchor = await element.query_selector('a[attributionsrc]')
                    await page.wait_for_load_state()
                    if anchor:
                        url = await page.evaluate('(element) => element.href', anchor)
                        await page.wait_for_load_state()
                        
                        if search_url in url.lower():
                            a_node = await element.query_selector('a.sVXRqc')
                            await page.wait_for_load_state()
                            await a_node.click()
                            await page.wait_for_load_state()
            except Exception as e:
                print(e)
            finally:
                if page:
                    await page.close()
                if browser:
                    await browser.close()

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
            "server": f'{proxy_server}:{port_list[i]}',
            "username": proxy_username,
            "password": proxy_password
        }
        proxy_accounts.append(proxy_account)
    return proxy_accounts

# Main function to run tasks
async def main(url_list, proxy_server, proxy_username, proxy_password, start_port, end_port):
    task_list = url_list
    proxy_accounts = get_proxy_accounts(len(task_list), proxy_server, proxy_username, proxy_password, start_port, end_port)
    tasks = [get_url(search_url=task_list[i].get("search_url"), proxy_account=proxy_accounts[i], search_keyword=task_list[i].get("search_keyword")) for i in range(len(task_list))]
    await asyncio.gather(*tasks)

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
        asyncio.run(main(url_list, proxy_address, proxy_username, proxy_password, proxy_start_port, proxy_end_port))
        st.write("Completed all iterations")
    else:
        st.write("Please upload the search.txt file")
