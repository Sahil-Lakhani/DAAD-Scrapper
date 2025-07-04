from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd

# Headless browser setup
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--window-size=1920,1080")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")

# Load driver
driver = webdriver.Chrome(options=options)

# Target URL
URL = "https://www.daad.de/en/studying-in-germany/universities/all-degree-programmes/?hec-subjectGroup=2-229&hec-degreeType=37&hec-teachingLanguage=2"

def extract_programs():
    driver.get(URL)
    wait = WebDriverWait(driver, 20)
    
    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "li.result-list__item")))
    except Exception as e:
        print("⚠️ Timeout waiting for listings. Page might not have loaded correctly.")
        return []

    items = driver.find_elements(By.CSS_SELECTOR, "li.result-list__item")
    programs = []

    for item in items:
        try:
            title = item.find_element(By.CSS_SELECTOR, ".result-list__link").text.strip()
            university = item.find_element(By.CSS_SELECTOR, ".result-list__university").text.strip()
            location = item.find_element(By.CSS_SELECTOR, ".result-list__location").text.strip()
            link = item.find_element(By.CSS_SELECTOR, "a.result-list__link").get_attribute("href")

            programs.append({
                "Title": title,
                "University": university,
                "Location": location,
                "URL": link
            })
        except Exception as e:
            print("❌ Error parsing a result:", e)
            continue
    return programs

def run():
    print("🔎 Scraping DAAD page...\n")
    data = extract_programs()

    if not data:
        print("❌ No data scraped. Try increasing wait time or use non-headless mode.")
    else:
        print(f"✅ {len(data)} programs found. Saving to CSV.")
        pd.DataFrame(data).to_csv("daad_results.csv", index=False)
        print("📁 Saved as daad_results.csv")

    driver.quit()

if __name__ == "__main__":
    run()
