import tkinter as tk
from tkinter import ttk, messagebox
import threading
import requests
from bs4 import BeautifulSoup
from scraper_core import run_scraper  # Backend scraping function

class DAADScraperApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("DAAD University Scraper")
        self.geometry("400x350")

        self.subject_var = tk.StringVar()
        self.degree_var = tk.StringVar()
        self.language_var = tk.StringVar()

        self.subjects = {}
        self.degrees = {}
        self.languages = {}

        self.create_widgets()
        self.load_filter_options()

    def create_widgets(self):
        padding = {"padx": 10, "pady": 10}

        ttk.Label(self, text="Subject Group:").pack(**padding)
        self.subject_combo = ttk.Combobox(self, textvariable=self.subject_var)
        self.subject_combo.pack(**padding)

        ttk.Label(self, text="Degree Type:").pack(**padding)
        self.degree_combo = ttk.Combobox(self, textvariable=self.degree_var)
        self.degree_combo.pack(**padding)

        ttk.Label(self, text="Teaching Language:").pack(**padding)
        self.language_combo = ttk.Combobox(self, textvariable=self.language_var)
        self.language_combo.pack(**padding)

        ttk.Button(self, text="Start Scraping", command=self.start_scraping_thread).pack(pady=20)

    def load_filter_options(self):
        try:
            url = "https://www.daad.de/en/studying-in-germany/universities/all-degree-programmes/"
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(response.text, "lxml")

            def extract_options(name):
                select = soup.find("select", {"name": name})
                options = {}
                if select:
                    for opt in select.find_all("option"):
                        val = opt.get("value", "").strip()
                        label = opt.text.strip()
                        if val:
                            options[label] = val
                return options

            self.subjects = extract_options("hec-subjectGroup")
            self.degrees = extract_options("hec-degreeType")
            self.languages = extract_options("hec-teachingLanguage")

            self.subject_combo["values"] = list(self.subjects.keys())
            self.degree_combo["values"] = list(self.degrees.keys())
            self.language_combo["values"] = list(self.languages.keys())

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load filter options: {str(e)}")

    def start_scraping_thread(self):
        t = threading.Thread(target=self.run_scraper)
        t.start()

    def run_scraper(self):
        subject = self.subjects.get(self.subject_var.get())
        degree = self.degrees.get(self.degree_var.get())
        language = self.languages.get(self.language_var.get())

        if not all([subject, degree, language]):
            messagebox.showerror("Error", "Please select all fields.")
            return

        try:
            run_scraper(subject_group=subject, degree_type=degree, language=language)
            messagebox.showinfo("Done", "Scraping completed! Data saved to daad_results.csv")
        except Exception as e:
            messagebox.showerror("Scraping Error", str(e))

if __name__ == "__main__":
    app = DAADScraperApp()
    app.mainloop()
