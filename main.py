from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import uvicorn
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import os
import time

# Get API Key from environment variable
API_KEY = os.getenv("api-key", "default_key")

def authenticate(token: str = Depends()):
    if token != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return token

app = FastAPI()

class SearchRequest(BaseModel):
    keywords: list[str]
    api_key: str

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
    
    service = Service("/usr/bin/chromedriver")  # Adjust path if needed
    driver = webdriver.Chrome(service=service, options=options)
    return driver

@app.post("/search")
def search_google(request: SearchRequest):
    if request.api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    
    driver = setup_driver()
    results_dict = {}
    
    try:
        for keyword in request.keywords:
            driver.get("https://www.google.com.au/")
            time.sleep(2)  # Let the page load

            search_box = driver.find_element("name", "q")
            search_box.send_keys(keyword)
            search_box.submit()
            time.sleep(3)
            
            page_source = driver.page_source
            results_dict[keyword] = page_source
    
    finally:
        driver.quit()
    
    return {"search_results": results_dict}
