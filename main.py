import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
from scraper import scrape_courses

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("DAAD Course Scraper")
        self.geometry("600x500")

        self.query_var = ctk.StringVar()
        self.limit_var = ctk.StringVar(value="10")

        self.degree_vars = {
            "Bachelor's": ctk.BooleanVar(),
            "Master's": ctk.BooleanVar(),
            "PhD / Doctorate": ctk.BooleanVar(),
            "Research school": ctk.BooleanVar(),
            "Language course": ctk.BooleanVar(),
            "Short course": ctk.BooleanVar(),
            "Preparatory course": ctk.BooleanVar(),
        }

        self.lang_vars = {
            "German only": ctk.BooleanVar(),
            "English only": ctk.BooleanVar(),
            "Other": ctk.BooleanVar(),
            "German & English": ctk.BooleanVar(),
        }

        self.bgn_vars = {
            "Winter semester": ctk.BooleanVar(),
            "Summer semester": ctk.BooleanVar(),
            "Other": ctk.BooleanVar(),
        }

        self.create_widgets()

    def create_widgets(self):
        frame = ctk.CTkFrame(self)
        frame.pack(padx=20, pady=20, fill="both", expand=True)

        ctk.CTkLabel(frame, text="🔍 Course Query:").pack(anchor="w")
        ctk.CTkEntry(frame, textvariable=self.query_var).pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(frame, text="🎓 Course Type:").pack(anchor="w")
        for name, var in self.degree_vars.items():
            ctk.CTkCheckBox(frame, text=name, variable=var).pack(anchor="w")

        ctk.CTkLabel(frame, text="🌐 Language:").pack(anchor="w", pady=(10, 0))
        for name, var in self.lang_vars.items():
            ctk.CTkCheckBox(frame, text=name, variable=var).pack(anchor="w")

        ctk.CTkLabel(frame, text="📅 Start of Programme:").pack(anchor="w", pady=(10, 0))
        for name, var in self.bgn_vars.items():
            ctk.CTkCheckBox(frame, text=name, variable=var).pack(anchor="w")

        ctk.CTkLabel(frame, text="🔢 Results Limit:").pack(anchor="w", pady=(10, 0))
        ctk.CTkEntry(frame, textvariable=self.limit_var).pack(fill="x", pady=(0, 10))

        self.progress = ctk.CTkLabel(frame, text="")
        self.progress.pack(pady=(5, 5))

        self.scrape_button = ctk.CTkButton(frame, text="Start Scraping", command=self.start_scraping)
        self.scrape_button.pack(pady=10)

    def start_scraping(self):
        self.scrape_button.configure(state="disabled")
        self.progress.configure(text="⏳ Scraping in progress...")
        threading.Thread(target=self.run_scraper).start()

    def run_scraper(self):
        try:
            query = self.query_var.get()
            degrees = [str(i + 1) for i, v in enumerate(self.degree_vars.values()) if v.get()]
            langs = [str(i + 1) for i, v in enumerate(self.lang_vars.values()) if v.get()]
            bgns = [str(i + 1) if i < 2 else "5" for i, v in enumerate(self.bgn_vars.values()) if v.get()]
            limit = self.limit_var.get()

            if not query or not degrees or not langs or not bgns or not limit:
                raise ValueError("Please fill all fields correctly.")

            save_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
            if not save_path:
                self.progress.configure(text="❌ Operation cancelled.")
                self.scrape_button.configure(state="normal")
                return

            scrape_courses(query, degrees, langs, bgns, limit, save_path)

            self.progress.configure(text=f"✅ Scraping complete. CSV saved to:\n{save_path}")

        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.progress.configure(text="❌ Scraping failed.")
        finally:
            self.scrape_button.configure(state="normal")

if __name__ == "__main__":
    app = App()
    app.mainloop()
