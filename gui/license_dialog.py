import tkinter as tk
from tkinter import filedialog, messagebox
import json
from datetime import date
import shutil
from core.license_manager import verify_license, LICENSE_DIR
import os

os.makedirs(LICENSE_DIR, exist_ok=True)


class LicenseDialog(tk.Toplevel):
    def __init__(self, parent, on_success):
        super().__init__(parent)
        self.on_success = on_success
        self.title("Import License")
        self.geometry("400x100")

        # Optional modal: comment these out for now
        self.transient(parent)  # keeps relative to parent
        self.lift()  # brings to front
        self.attributes('-topmost', True)  # ensures top
        self.after_idle(lambda: self.attributes('-topmost', False))  # allow normal stacking

        tk.Label(self, text="Import your license file to enable full features.").pack(pady=10)
        self.import_btn = tk.Button(self, text="Select File", command=self.import_file)
        self.import_btn.pack(pady=5)

        self.center_window()

        print("LicenseDialog initialized")


    def center_window(self):
        self.update_idletasks()
        w = self.winfo_width() or 400
        h = self.winfo_height() or 100
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    def import_file(self):
        # Disable button to prevent double-click
        self.import_btn.config(state="disabled")

        try:
            file_path = filedialog.askopenfilename(
                parent=self,
                title="Select License File",
                filetypes=[("JSON files", "*.json")]
            )
            if not file_path:
                return  # Just exit; button will be re-enabled in finally

            with open(file_path, "r") as f:
                license_data = json.load(f)

            valid, msg = verify_license(license_data)
            if valid:
                today = date.today().isoformat()
                shutil.copy(file_path, f"{LICENSE_DIR}/license_{today}.json")
                #messagebox.showinfo("Success", "License imported successfully!")
                self.after(0, self.finish_success)
            else:
                messagebox.showerror("Invalid License", msg)

        except Exception as e:
            messagebox.showerror("Error", str(e))

        finally:
            # Always re-enable button in case of cancel/error
            if self.import_btn.winfo_exists():
                self.import_btn.config(state="normal")

    def finish_success(self):
        try:
            self.on_success()
        finally:
            self.destroy()
