from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import urllib.parse
import time
import csv

def setup_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    return webdriver.Chrome(options=options)

def build_search_url(query, degree_list, lang_list, bgn_list, limit):
    base_url = "https://www2.daad.de/deutschland/studienangebote/international-programmes/en/result/"
    params = {
        "q": query,
        "degree[]": degree_list,
        "lang[]": lang_list,
        "bgn[]": bgn_list,
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

def remove_modal(driver):
    try:
        WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, "snoop-modal-wrapper")))
        time.sleep(1)
    except:
        pass
    driver.execute_script("""
        document.querySelectorAll('.snoop-modal-wrapper, .snoop-modal-backdrop').forEach(el => el.remove());
    """)
    time.sleep(1)

def extract_registration_data(driver, wait):
    try:
        remove_modal(driver)
        registration_tab = wait.until(EC.element_to_be_clickable((By.ID, "registration-tab")))
        driver.execute_script("arguments[0].scrollIntoView(true);", registration_tab)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", registration_tab)

        registration = wait.until(EC.presence_of_element_located((By.ID, "registration")))
        time.sleep(1)

        registration_fields = {
            "Academic Requirements": None,
            "Language Requirements": None,
            "Submit Application To": None
        }

        reg_dt_elements = registration.find_elements(By.TAG_NAME, "dt")
        for dt in reg_dt_elements:
            label = dt.text.strip()
            dd = dt.find_element(By.XPATH, "following-sibling::dd[1]")
            html_value = dd.get_attribute("innerHTML").strip()
            soup = BeautifulSoup(html_value, "html.parser")
            clean_text = soup.get_text(separator="\n", strip=True)

            if "Academic admission requirements" in label:
                registration_fields["Academic Requirements"] = clean_text
            elif "Language requirements" in label:
                registration_fields["Language Requirements"] = clean_text
            elif "Submit application to" in label:
                registration_fields["Submit Application To"] = clean_text

        return registration_fields

    except Exception as e:
        return {
            "Academic Requirements": None,
            "Language Requirements": None,
            "Submit Application To": None
        }

def run_scraper(query, degree_list, lang_list, bgn_list, limit, output_file):
    search_url = build_search_url(query, degree_list, lang_list, bgn_list, limit)
    driver = setup_driver()
    wait = WebDriverWait(driver, 10)
    course_data = []

    try:
        driver.get(search_url)
        time.sleep(3)
        course_links = driver.find_elements(By.CSS_SELECTOR, "a.js-course-detail-link")
        course_urls = list({link.get_attribute("href") for link in course_links if "/detail/" in link.get_attribute("href")})

        for idx, url in enumerate(course_urls, start=1):
            driver.get(url)

            try:
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
                    university_name = driver.find_element(By.CSS_SELECTOR, "a.c-contact__link")
                    fields["University Name"] = university_name.text.strip()
                except:
                    fields["University Name"] = None

                overview = driver.find_element(By.ID, "overview")
                dt_elements = overview.find_elements(By.TAG_NAME, "dt")
                for dt in dt_elements:
                    label = dt.text.strip()
                    dd = dt.find_element(By.XPATH, "following-sibling::dd[1]")
                    paragraphs = dd.find_elements(By.TAG_NAME, "p")
                    value = "\n".join(p.text.strip() for p in paragraphs if p.text.strip()) if paragraphs else dd.text.strip()

                    if label == "Degree":
                        fields["Degree"] = value
                    elif label == "Course location":
                        fields["Course Location"] = value
                    elif label == "Teaching language":
                        fields["Teaching Language"] = value
                    elif label == "Full-time / part-time":
                        fields["Full-time / Part-time"] = value
                    elif label == "Programme duration":
                        fields["Programme Duration"] = value
                    elif label == "Beginning":
                        fields["Beginning"] = value
                    elif label == "Application deadline":
                        fields["Application Deadline"] = value
                    elif label == "Tuition fees per semester in EUR":
                        fields["Tuition Fees"] = value

                reg_data = extract_registration_data(driver, wait)
                fields.update(reg_data)

                try:
                    course_site = driver.find_element(By.CSS_SELECTOR, "a.c-contact__link.visitCourseWebsite")
                    fields["Course Website"] = course_site.get_attribute("href")
                except:
                    fields["Course Website"] = None

                course_data.append(fields)

            except Exception as e:
                print(f"❌ Error in URL {url}: {e}")

    finally:
        driver.quit()

    if course_data:
        keys = list(course_data[0].keys())
        with open(output_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(course_data)
        return len(course_data)
    else:
        return 0
