import customtkinter as ctk
from tkinter import messagebox
from tkinter import filedialog  # ✅ Added for save file dialog
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import urllib.parse
import time
import csv

# Initialize CustomTkinter
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# === DEGREE AND LANGUAGE OPTIONS ===
degree_map = {
    "1 - Bachelor's": "1",
    "2 - Master's": "2",
    "3 - PhD / Doctorate": "3",
    "4 - Research school": "4",
    "5 - Language course": "5",
    "6 - Short course": "6",
    "7 - Preparatory course": "7"
}

language_map = {
    "1 - German only": "1",
    "2 - English only": "2",
    "3 - Other": "3",
    "4 - German & English": "4"
}

bgn_map = {
    "1 - Winter semester": "1",
    "2 - Summer semester": "2",
    "5 - Other": "5"
}

def setup_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    return webdriver.Chrome(options=options)

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
        print("❌ Error in registration tab:", e)
        return {
            "Academic Requirements": None,
            "Language Requirements": None,
            "Submit Application To": None
        }

def start_scraping():
    query = entry_query.get().strip()
    degree_selected = [k for k, var in degree_vars.items() if var.get() == 1]
    lang_selected = [k for k, var in language_vars.items() if var.get() == 1]
    bgn_selected = [k for k, var in bgn_vars.items() if var.get() == 1]
    limit = entry_limit.get().strip()

    if not limit.isdigit():
        limit = "10"

    base_url = "https://www2.daad.de/deutschland/studienangebote/international-programmes/en/result/"
    params = {
        "q": query,
        "degree[]": [degree_map[d] for d in degree_selected],
        "lang[]": [language_map[l] for l in lang_selected],
        "bgn[]": [bgn_map[b] for b in bgn_selected],
        "limit": limit,
        "sort": "4",
        "display": "list"
    }

    query_params = []
    for key, values in params.items():
        for val in values if isinstance(values, list) else [values]:
            query_params.append((key, val.strip()))

    search_url = base_url + "?" + urllib.parse.urlencode(query_params, doseq=True)
    print("\n🌐 Searching:", search_url)

    driver = setup_driver()
    wait = WebDriverWait(driver, 10)
    course_data = []
    progress_bar.set(0)
    progress_bar.update()

    try:
        driver.get(search_url)
        time.sleep(3)
        course_links = driver.find_elements(By.CSS_SELECTOR, "a.js-course-detail-link")
        course_urls = list({link.get_attribute("href") for link in course_links if "/detail/" in link.get_attribute("href")})

        total = len(course_urls)
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
            progress_bar.set(idx / total)
            progress_bar.update()

    finally:
        driver.quit()

    if course_data:
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title="Save CSV File As",
            initialfile="courses.csv"  # ✅ Default name
        )
        if file_path:
            keys = list(course_data[0].keys())
            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(course_data)
            messagebox.showinfo("Success", f"Exported {len(course_data)} results to:\n{file_path}")
        else:
            messagebox.showwarning("Cancelled", "CSV export cancelled by the user.")
    else:
        messagebox.showwarning("No Results", "No data was scraped.")

# === GUI ===
app = ctk.CTk()
app.title("DAAD Scraper GUI")
app.geometry("800x750")

ctk.CTkLabel(app, text="Search Keyword:").pack(pady=5)
entry_query = ctk.CTkEntry(app, width=400)
entry_query.pack()

ctk.CTkLabel(app, text="Degree Types (Multiple):").pack(pady=5)
degree_frame = ctk.CTkFrame(app)
degree_frame.pack()
degree_vars = {}
for idx, label in enumerate(degree_map.keys()):
    var = ctk.IntVar()
    cb = ctk.CTkCheckBox(degree_frame, text=label, variable=var)
    cb.grid(row=idx // 3, column=idx % 3, padx=10, pady=2, sticky="w")
    degree_vars[label] = var

ctk.CTkLabel(app, text="Course Languages (Multiple):").pack(pady=5)
language_frame = ctk.CTkFrame(app)
language_frame.pack()
language_vars = {}
for idx, label in enumerate(language_map.keys()):
    var = ctk.IntVar()
    cb = ctk.CTkCheckBox(language_frame, text=label, variable=var)
    cb.grid(row=idx // 3, column=idx % 3, padx=10, pady=2, sticky="w")
    language_vars[label] = var

ctk.CTkLabel(app, text="Start of Programme (Multiple):").pack(pady=5)
bgn_frame = ctk.CTkFrame(app)
bgn_frame.pack()
bgn_vars = {}
for idx, label in enumerate(bgn_map.keys()):
    var = ctk.IntVar()
    cb = ctk.CTkCheckBox(bgn_frame, text=label, variable=var)
    cb.grid(row=idx // 3, column=idx % 3, padx=10, pady=2, sticky="w")
    bgn_vars[label] = var

ctk.CTkLabel(app, text="Result Limit:").pack(pady=5)
entry_limit = ctk.CTkEntry(app, width=100)
entry_limit.insert(0, "10")
entry_limit.pack()

progress_bar = ctk.CTkProgressBar(app, width=500)
progress_bar.pack(pady=15)
progress_bar.set(0)

ctk.CTkButton(app, text="Search & Export to CSV", command=start_scraping).pack(pady=20)

app.mainloop()
