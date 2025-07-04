# scraper_core.py

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

def run_scraper(subject_group, degree_type, language, output="daad_results.csv"):
    base_url = "https://www.daad.de/en/studying-in-germany/universities/all-degree-programmes/"
    headers = {"User-Agent": "Mozilla/5.0"}

    params = {
        "hec-subjectGroup": subject_group,
        "hec-degreeType": degree_type,
        "hec-teachingLanguage": language,
        "page": 1
    }

    def get_total_pages():
        res = requests.get(base_url, params=params, headers=headers)
        soup = BeautifulSoup(res.text, "lxml")
        try:
            return int(soup.select("ul.pagination__list li")[-2].text.strip())
        except:
            return 1

    def extract_programs(page):
        params["page"] = page
        res = requests.get(base_url, params=params, headers=headers)
        soup = BeautifulSoup(res.text, "lxml")
        programs = []

        for item in soup.select("li.result-list__item"):
            try:
                title = item.select_one(".result-list__link").text.strip()
                university = item.select_one(".result-list__university").text.strip()
                location = item.select_one(".result-list__location").text.strip()
                link = "https://www.daad.de" + item.select_one("a.result-list__link")["href"]
                programs.append({
                    "Title": title,
                    "University": university,
                    "Location": location,
                    "URL": link
                })
            except Exception:
                continue
        return programs

    def extract_details(url):
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, "lxml")
        info = {}

        facts = soup.select("dl.program-facts__list")
        for fact in facts:
            for dt, dd in zip(fact.select("dt"), fact.select("dd")):
                key = dt.text.strip()
                value = dd.text.strip()
                info[key] = value
        return info

    all_programs = []
    total_pages = get_total_pages()
    print(f"Total pages: {total_pages}")

    for page in range(1, total_pages + 1):
        print(f"Scraping page {page}...")
        programs = extract_programs(page)
        for prog in programs:
            try:
                details = extract_details(prog["URL"])
                prog.update(details)
            except Exception as e:
                prog["Error"] = str(e)
            time.sleep(0.5)
        all_programs.extend(programs)
        time.sleep(1)

    df = pd.DataFrame(all_programs)
    df.to_csv(output, index=False)
    print(f"✅ Data saved to {output}")
