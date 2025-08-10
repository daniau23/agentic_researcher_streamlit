from langchain_community.document_loaders import SeleniumURLLoader
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from shared import ResearchState
import os
import shutil

MAX_CHARS = 100_000

def get_headless_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Detect environment
    if shutil.which("chromium-browser"):
        chrome_options.binary_location = "/usr/bin/chromium-browser"
    elif shutil.which("chrome"):
        chrome_options.binary_location = shutil.which("chrome")

    chromedriver_path = shutil.which("chromedriver") or "/usr/bin/chromedriver"
    service = Service(chromedriver_path)
    
    return webdriver.Chrome(service=service, options=chrome_options)

def load_node(state: ResearchState) -> dict:
    if not state.url:
        return {"content": "No URL to load"}

    driver = get_headless_driver()
    loader = SeleniumURLLoader(urls=[str(state.url)], browser=driver)
    docs = loader.load()
    driver.quit()

    content = docs[0].page_content if docs else "No content"
    truncated_content = content[:MAX_CHARS]
    return {"content": truncated_content}
