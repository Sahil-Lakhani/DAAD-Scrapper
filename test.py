from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

# -- Setup headless Chrome
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")

# -- Update the path to your ChromeDriver here
driver = webdriver.Chrome(options=chrome_options)

# -- Target URL
url = "https://www2.daad.de/deutschland/studienangebote/international-programmes/en/result/?cert=&admReq=&langExamPC=&scholarshipLC=&langExamLC=&scholarshipSC=&langExamSC=&degree%5B%5D=&fos=&langDeAvailable=&langEnAvailable=&lang%5B%5D=2&modStd%5B%5D=&cit%5B%5D=&tyi%5B%5D=&ins%5B%5D=&fee=&bgn%5B%5D=&dat%5B%5D=&prep_subj%5B%5D=&prep_degree%5B%5D=&sort=4&dur=&subjects%5B%5D=&q=computer%20science&limit=10&offset=&display=list&lvlDe%5B%5D=B1-B2&lvlEn%5B%5D=#tab_result-list"

# -- Load page
driver.get(url)
time.sleep(5)  # Wait for content to load; adjust if needed

# -- Find all course links
links = driver.find_elements(By.CSS_SELECTOR, "a.js-course-detail-link")

# -- Extract href attributes
course_urls = []
for link in links:
    href = link.get_attribute("href")
    if href and "/detail/" in href:
        course_urls.append(href)

# -- Print result
print("Found course links:")
for course in set(course_urls):
    print(course)

# -- Clean up
driver.quit()
