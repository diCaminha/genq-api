import requests
from bs4 import BeautifulSoup
import re
import logging
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def extract_text_with_requests(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        for script_or_style in soup(['script', 'style', 'header', 'footer', 'nav']):
            script_or_style.extract()
            
        text = soup.get_text(separator=' ', strip=True)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    except Exception as e:
        logging.error(f"Requests method failed: {e}")
        return None

def extract_text_with_selenium_render(url, wait_time=10, scroll=True):
    driver = None
    try:
        chrome_options = Options()
        
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN", "/usr/bin/google-chrome")
        
        driver_path = os.environ.get("CHROMEDRIVER_PATH", "/usr/bin/chromedriver")
        service = Service(executable_path=driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        driver.get(url)
        
        WebDriverWait(driver, wait_time).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        if scroll:
            last_height = driver.execute_script("return document.body.scrollHeight")
            
            for _ in range(3):  # Limit scrolling to avoid timeouts
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                
                time.sleep(2)
                
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
        
        page_source = driver.page_source
        
        soup = BeautifulSoup(page_source, 'html.parser')
        
        for element in soup.select('script, style, header, footer, nav, .ads, .comments, .sidebar'):
            element.extract()
        
        text = soup.get_text(separator=' ', strip=True)
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    except Exception as e:
        logging.error(f"Selenium method failed on Render: {e}")
        return None
    finally:
        if driver:
            driver.quit()

def get_webpage_text(url):
    """Main function to extract text from a webpage, optimized for Render"""
    logging.basicConfig(level=logging.INFO)
    
    logging.info("Trying requests method first...")
    result = extract_text_with_requests(url)
    
    if not result or len(result.strip()) < 100:
        logging.info("Requests returned insufficient text. Trying Selenium method...")
        result = extract_text_with_selenium_render(url)
    
    return result if result else "Failed to extract text content."
