# main.py
import customtkinter as ctk
from tkinter import filedialog
import threading
import csv
from scraper import build_search_url, extract_data

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class DAADApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("DAAD Course Scraper")
        self.geometry("600x500")

        self.inputs = {}

        self.create_widgets()

    def create_widgets(self):
        self.title_label = ctk.CTkLabel(self, text="🎓 DAAD Course Scraper", font=ctk.CTkFont(size=20, weight="bold"))
        self.title_label.pack(pady=10)

        self.form_frame = ctk.CTkFrame(self)
        self.form_frame.pack(pady=10, padx=20, fill="both", expand=True)

        fields = [
            ("Search Keyword", "query"),
            ("Degree (1-Bachelor, 2-Master,...)", "degree"),
            ("Language (1-German, 2-English,...)", "lang"),
            ("Start (1-Winter, 2-Summer,...)", "bgn"),
            ("Results Limit (e.g. 10, 20)", "limit")
        ]

        for label_text, key in fields:
            label = ctk.CTkLabel(self.form_frame, text=label_text)
            label.pack(anchor="w", padx=10)
            entry = ctk.CTkEntry(self.form_frame)
            entry.pack(fill="x", padx=10, pady=5)
            self.inputs[key] = entry

        self.status = ctk.CTkLabel(self, text="", text_color="gray")
        self.status.pack(pady=5)

        self.scrape_button = ctk.CTkButton(self, text="Start Scraping", command=self.start_scraping)
        self.scrape_button.pack(pady=10)

    def start_scraping(self):
        self.status.configure(text="🔄 Scraping in progress...")
        self.scrape_button.configure(state="disabled")
        thread = threading.Thread(target=self.run_scraper)
        thread.start()

    def run_scraper(self):
        data = self.get_input_values()
        search_url = build_search_url(**data)
        results = extract_data(search_url)

        if results:
            file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
            if file_path:
                with open(file_path, "w", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=results[0].keys())
                    writer.writeheader()
                    writer.writerows(results)
                self.status.configure(text=f"✅ Saved {len(results)} courses.")
            else:
                self.status.configure(text="⚠️ Save cancelled.")
        else:
            self.status.configure(text="⚠️ No data found.")

        self.scrape_button.configure(state="normal")

    def get_input_values(self):
        return {key: entry.get().strip() for key, entry in self.inputs.items()}

if __name__ == "__main__":
    app = DAADApp()
    app.mainloop()
