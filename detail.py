# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC

# # Setup headless Chrome
# options = Options()
# options.add_argument("--headless")
# options.add_argument("--disable-gpu")
# options.add_argument("--window-size=1920,1080")
# driver = webdriver.Chrome(options=options)

# # Target course URL
# url = "https://www2.daad.de/deutschland/studienangebote/international-programmes/en/detail/8305/"

# try:
#     driver.get(url)
#     wait = WebDriverWait(driver, 10)

#     # Wait for the Overview section to load
#     overview = wait.until(EC.presence_of_element_located((By.ID, "overview")))

#     # Target labels to extract
#     desired_fields = {
#         "Degree": None,
#         "Course location": None,
#         "Teaching language": None,
#         "Full-time / part-time": None,
#         "Programme duration": None,
#         "Beginning": None,
#         "Application deadline": None,
#         "Tuition fees per semester in EUR": None
#     }

#     # Find all dt elements and map values
#     dt_elements = overview.find_elements(By.TAG_NAME, "dt")

#     for dt in dt_elements:
#         label = dt.text.strip()
#         if label in desired_fields:
#             dd = dt.find_element(By.XPATH, "following-sibling::dd[1]")
#             # Get all text inside the <dd>
#             paragraphs = dd.find_elements(By.TAG_NAME, "p")
#             if paragraphs:
#                 value = "\n".join(p.text.strip() for p in paragraphs if p.text.strip())
#             else:
#                 value = dd.text.strip()
#             desired_fields[label] = value

#     # Print extracted fields
#     print("🟦 Overview Data:")
#     for key, value in desired_fields.items():
#         print(f"{key}: {value if value else '❌ Not found'}")

# except Exception as e:
#     print("❌ Error:", e)

# finally:
#     driver.quit()

# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from bs4 import BeautifulSoup
# import time

# # Setup headless Chrome
# options = Options()
# options.add_argument("--headless")
# options.add_argument("--disable-gpu")
# options.add_argument("--window-size=1920,1080")
# driver = webdriver.Chrome(options=options)

# # URL directly to the registration tab
# url = "https://www2.daad.de/deutschland/studienangebote/international-programmes/en/detail/8305/#tab_registration"

# try:
#     driver.get(url)
#     time.sleep(2)  # Let content load

#     wait = WebDriverWait(driver, 10)
#     registration = wait.until(EC.presence_of_element_located((By.ID, "registration")))

#     registration_fields = {
#         "Academic admission requirements": None,
#         "Language requirements": None,
#         "Submit application to": None
#     }

#     # Get all <dt> labels and their corresponding <dd> values
#     reg_dt_elements = registration.find_elements(By.TAG_NAME, "dt")

#     for dt in reg_dt_elements:
#         label = dt.text.strip()
#         for key in registration_fields:
#             if key in label:
#                 dd = dt.find_element(By.XPATH, "following-sibling::dd[1]")
#                 html_value = dd.get_attribute("innerHTML").strip()
                
#                 # Convert HTML to readable text using BeautifulSoup
#                 soup = BeautifulSoup(html_value, "html.parser")
#                 clean_text = soup.get_text(separator="\n", strip=True)
                
#                 registration_fields[key] = clean_text
#                 break

#     print("\n🟧 Requirements / Registration Data (Plain Text):")
#     for key, value in registration_fields.items():
#         print(f"\n🔹 {key}:\n{value if value else '❌ Not found'}")

# except Exception as e:
#     print("❌ Error:", e)

# finally:
#     driver.quit()



from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

def setup_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    return webdriver.Chrome(options=options)

def extract_overview_data(driver, wait):
    overview = wait.until(EC.presence_of_element_located((By.ID, "overview")))

    desired_fields = {
        "Degree": None,
        "Course location": None,
        "Teaching language": None,
        "Full-time / part-time": None,
        "Programme duration": None,
        "Beginning": None,
        "Application deadline": None,
        "Tuition fees per semester in EUR": None
    }

    dt_elements = overview.find_elements(By.TAG_NAME, "dt")
    for dt in dt_elements:
        label = dt.text.strip()
        if label in desired_fields:
            dd = dt.find_element(By.XPATH, "following-sibling::dd[1]")
            paragraphs = dd.find_elements(By.TAG_NAME, "p")
            if paragraphs:
                value = "\n".join(p.text.strip() for p in paragraphs if p.text.strip())
            else:
                value = dd.text.strip()
            desired_fields[label] = value

    print("🟦 Overview Data:")
    for key, value in desired_fields.items():
        print(f"{key}: {value if value else '❌ Not found'}")

def remove_modal_and_backdrop(driver):
    try:
        # Wait for modal or backdrop to appear (if any)
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "snoop-modal-wrapper"))
        )
        time.sleep(1)  # let it fully render before removing
    except:
        pass  # Modal might not appear every time

    # Remove both modal and backdrop
    driver.execute_script("""
        let modal = document.querySelector('.snoop-modal-wrapper');
        if (modal) modal.remove();
        let backdrop = document.querySelector('.snoop-modal-backdrop');
        if (backdrop) backdrop.remove();
    """)
    time.sleep(1)  # let DOM settle
    print("✅ Removed modal and backdrop")


def extract_registration_data(driver, wait):
    try:
        # Ensure modal and backdrop are removed
        remove_modal_and_backdrop(driver)
        time.sleep(1)

        # Click the Requirements / Registration tab
        registration_tab = wait.until(EC.element_to_be_clickable((By.ID, "registration-tab")))
        driver.execute_script("arguments[0].scrollIntoView(true);", registration_tab)
        time.sleep(1)
        registration_tab.click()

        # Wait for the tab content to load
        registration = wait.until(EC.presence_of_element_located((By.ID, "registration")))
        time.sleep(1)

        registration_fields = {
            "Academic admission requirements": None,
            "Language requirements": None,
            "Submit application to": None
        }

        reg_dt_elements = registration.find_elements(By.TAG_NAME, "dt")
        for dt in reg_dt_elements:
            label = dt.text.strip()
            for key in registration_fields:
                if key in label:
                    dd = dt.find_element(By.XPATH, "following-sibling::dd[1]")
                    html_value = dd.get_attribute("innerHTML").strip()
                    soup = BeautifulSoup(html_value, "html.parser")
                    clean_text = soup.get_text(separator="\n", strip=True)
                    registration_fields[key] = clean_text
                    break

        print("\n🟧 Requirements / Registration Data:")
        for key, value in registration_fields.items():
            print(f"\n🔹 {key}:\n{value if value else '❌ Not found'}")

    except Exception as e:
        print("❌ Error in registration tab:", e)


def extract_course_website(driver, wait):
    try:
        link_element = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a.c-contact__link.visitCourseWebsite"))
        )
        href = link_element.get_attribute("href")
        print(f"\n🔗 Course Website: {href}")
        return href
    except:
        print("\n🔗 Course Website: ❌ Not found")
        return None


def main():
    url = "https://www2.daad.de/deutschland/studienangebote/international-programmes/en/detail/8324/"
    driver = setup_driver()
    wait = WebDriverWait(driver, 10)

    try:
        driver.get(url)
        extract_overview_data(driver, wait)
        extract_registration_data(driver, wait)
        extract_course_website(driver, wait)
    except Exception as e:
        print("❌ Error:", e)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
