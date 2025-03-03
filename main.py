from fastapi import FastAPI, Query, HTTPException, Depends
import uvicorn
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time

# Authentication Token
API_TOKEN = "your_secure_api_token_here"

def authenticate(token: str = Query(..., alias="api_token")):
    if token != API_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid API Token")
    return token

app = FastAPI()

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

@app.get("/search")
def search_google(query: str, token: str = Depends(authenticate)):
    driver = setup_driver()
    
    try:
        driver.get("https://www.google.com.au/")
        time.sleep(2)  # Let the page load

        search_box = driver.find_element("name", "q")
        search_box.send_keys(query)
        search_box.submit()
        time.sleep(3)
        
        results = driver.find_elements("css selector", "h3")
        search_results = [result.text for result in results[:5] if result.text]
    
    finally:
        driver.quit()
    
    return {"query": query, "results": search_results}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
