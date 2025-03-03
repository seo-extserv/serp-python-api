from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import uvicorn
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import os
import time
import logging
import subprocess
from fastapi.responses import JSONResponse

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get API Key from environment variable
API_KEY = os.getenv("api-key", "default_key")

def authenticate(token: str = Depends()):
    if token != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return token

app = FastAPI()

@app.get("/")
def ping():
    return {"message": "API is live"}

class SearchRequest(BaseModel):
    keywords: list[str]
    api_key: str

def install_chromedriver():
    try:
        logger.info("Installing latest ChromeDriver...")
        subprocess.run("apt-get update && apt-get install -y chromium chromium-driver", shell=True, check=True)
        logger.info("ChromeDriver installed successfully.")
    except Exception as e:
        logger.error(f"Error installing ChromeDriver: {str(e)}")
        raise HTTPException(status_code=500, detail="ChromeDriver installation failed")

def setup_driver():
    try:
        # Use a predefined Chrome and ChromeDriver path (for Render compatibility)
        chrome_path = "/usr/bin/google-chrome-stable"
        chromedriver_path = "/usr/bin/chromedriver"

        options = webdriver.ChromeOptions()
        options.binary_location = chrome_path  # Ensure the correct binary location
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

        service = Service(chromedriver_path)
        driver = webdriver.Chrome(service=service, options=options)
        return driver
    except Exception as e:
        logger.error(f"Error setting up Selenium driver: {str(e)}")
        raise HTTPException(status_code=500, detail="Selenium setup failed")

@app.post("/search")
def search_google(request: SearchRequest):
    if request.api_key != API_KEY:
        logger.warning("Unauthorized API Key attempt")
        raise HTTPException(status_code=401, detail="Invalid API Key")
    
    driver = setup_driver()
    results_dict = {}

    try:
        for keyword in request.keywords:
            logger.info(f"Searching Google for: {keyword}")
            driver.get("https://www.google.com.au/")
            time.sleep(2)  # Let the page load

            search_box = driver.find_element("name", "q")
            search_box.send_keys(keyword)
            search_box.submit()
            time.sleep(3)

            page_source = driver.page_source
            results_dict[keyword] = page_source
    
    except Exception as e:
        logger.error(f"Error during search: {str(e)}")
        return JSONResponse(status_code=500, content={"error": str(e)})

    finally:
        driver.quit()
    
    return {"search_results": results_dict}
