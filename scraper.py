# scraper.py
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import urllib.parse
import time

def setup_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    return webdriver.Chrome(options=options)

def build_search_url(query, degree, lang, bgn, limit):
    base_url = "https://www2.daad.de/deutschland/studienangebote/international-programmes/en/result/"
    params = {
        "q": query,
        "degree[]": degree.split(","),
        "lang[]": lang.split(","),
        "bgn[]": bgn.split(","),
        "limit": limit,
        "sort": "4",
        "display": "list"
    }
    query_params = []
    for key, values in params.items():
        if isinstance(values, list):
            for val in values:
                query_params.append((key, val.strip()))
        else:
            query_params.append((key, values.strip()))
    return base_url + "?" + urllib.parse.urlencode(query_params, doseq=True)

def extract_data(search_url):
    driver = setup_driver()
    wait = WebDriverWait(driver, 10)
    course_data = []
    try:
        driver.get(search_url)
        course_links = driver.find_elements(By.CSS_SELECTOR, "a.js-course-detail-link")
        course_urls = list({link.get_attribute("href") for link in course_links if "/detail/" in link.get_attribute("href")})

        for url in course_urls:
            driver.get(url)
            wait.until(EC.presence_of_element_located((By.ID, "overview")))
            fields = {
                "Course URL": url,
                "University Name": None,
                "Degree": None,
                "Course Location": None,
                "Teaching Language": None,
                "Full-time / Part-time": None,
                "Programme Duration": None,
                "Beginning": None,
                "Application Deadline": None,
                "Tuition Fees": None,
                "Academic Requirements": None,
                "Language Requirements": None,
                "Submit Application To": None,
                "Course Website": None
            }

            try:
                fields["University Name"] = driver.find_element(By.CSS_SELECTOR, "a.c-contact__link").text.strip()
            except:
                pass

            overview = driver.find_element(By.ID, "overview")
            dt_elements = overview.find_elements(By.TAG_NAME, "dt")
            for dt in dt_elements:
                label = dt.text.strip()
                dd = dt.find_element(By.XPATH, "following-sibling::dd[1]")
                paragraphs = dd.find_elements(By.TAG_NAME, "p")
                value = "\n".join(p.text.strip() for p in paragraphs if p.text.strip()) if paragraphs else dd.text.strip()
                label_map = {
                    "Degree": "Degree",
                    "Course location": "Course Location",
                    "Teaching language": "Teaching Language",
                    "Full-time / part-time": "Full-time / Part-time",
                    "Programme duration": "Programme Duration",
                    "Beginning": "Beginning",
                    "Application deadline": "Application Deadline",
                    "Tuition fees per semester in EUR": "Tuition Fees"
                }
                if label in label_map:
                    fields[label_map[label]] = value

            try:
                reg_tab = wait.until(EC.element_to_be_clickable((By.ID, "registration-tab")))
                driver.execute_script("arguments[0].click();", reg_tab)
                time.sleep(1)
                registration = driver.find_element(By.ID, "registration")
                reg_dts = registration.find_elements(By.TAG_NAME, "dt")
                for dt in reg_dts:
                    label = dt.text.strip()
                    dd = dt.find_element(By.XPATH, "following-sibling::dd[1]")
                    html_value = dd.get_attribute("innerHTML")
                    clean_text = BeautifulSoup(html_value, "html.parser").get_text(separator="\n", strip=True)
                    if "Academic admission requirements" in label:
                        fields["Academic Requirements"] = clean_text
                    elif "Language requirements" in label:
                        fields["Language Requirements"] = clean_text
                    elif "Submit application to" in label:
                        fields["Submit Application To"] = clean_text
            except:
                pass

            try:
                fields["Course Website"] = driver.find_element(By.CSS_SELECTOR, "a.c-contact__link.visitCourseWebsite").get_attribute("href")
            except:
                pass

            course_data.append(fields)

    finally:
        driver.quit()

    return course_data
