import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from datetime import date, datetime
from tkcalendar import DateEntry
import customtkinter as ctk
from core.storage import StorageManager


class IncomeForm(tk.Toplevel):
    def __init__(self, parent, storage: StorageManager, row_data=None, refresh_callback=None):
        super().__init__(parent)
        self.parent = parent

        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.storage = storage
        self.row_data = row_data
        self.refresh_callback = refresh_callback

        self.title("Add Income" if not row_data else "Edit Income")
        self.geometry("600x550")
        self.resizable(False, False)

        # ---------------- ROOT CTK FRAME ----------------
        root_frame = ctk.CTkFrame(self, fg_color="#040f21", corner_radius=12)  # rounded frame
        self.configure(bg="#040f21")
        root_frame.pack(fill="both", expand=True, padx=40, pady=30)

        # ---------------- DATE ----------------
        ctk.CTkLabel(
            root_frame,
            text="Date:",
            text_color="white",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", pady=(5, 2))

        self.date_var = tk.StringVar(
            value=row_data["date"] if row_data else date.today().isoformat()
        )

        # ---------------- DATE PICKER ----------------
        self.date_picker = DateEntry(
            root_frame,
            textvariable=self.date_var,
            date_pattern="yyyy-mm-dd",
            maxdate=date.today(),  # disables future dates automatically
            background="#123",  # background of calendar popup
            foreground="white",  # day text color
            headersbackground="#eee",  # month header background
            headersforeground="#000",  # month header text color
            weekendbackground="#fff",  # weekend day background
            weekendforeground="#000",  # weekend day text color
            othermonthforeground="red",  # days not in current month
            selectbackground="#365580",  # selected day background
            selectforeground="white",  # selected day text
            disableddaybackground="#ccc",  # disabled arrow button background
            disableddayforeground="#333",  # disabled arrow text
            borderwidth=1,
            showweeknumbers=False
        )

        # Pack with inner padding
        self.date_picker.pack(fill="x", pady=(0, 8), ipady=4)

        # ---------------- GROSS INCOME ----------------
        ctk.CTkLabel(
            root_frame,
            text="Gross Income:",
            text_color="white",
            font=ctk.CTkFont(size=14)
        ).pack(anchor="w", pady=(5, 2))

        self.amount_var = tk.StringVar(
            value=f"{row_data['gross_income']:,.2f}" if row_data else ""
        )
        self.amount_entry = ctk.CTkEntry(
            root_frame,
            textvariable=self.amount_var,
            fg_color="#1f2a38",
            text_color="white",
            placeholder_text="Enter gross income",
            corner_radius=8,
            border_width=2,
            border_color="#365580",
            height=25
        )
        self.amount_entry.pack(fill="x", pady=(0, 8))

        self.amount_entry.bind(
            "<FocusOut>",
            lambda e: self.format_amount(self.amount_var)
        )
        self.amount_var.trace_add("write", self.update_received)

        # ---------------- DESCRIPTION ----------------
        ctk.CTkLabel(
            root_frame,
            text="Description:",
            text_color="white",
            font=ctk.CTkFont(size=14)
        ).pack(anchor="w", pady=(5, 2))

        self.desc_var = tk.StringVar(value=row_data.get("description") if row_data else "")
        ctk.CTkEntry(
            root_frame,
            textvariable=self.desc_var,
            fg_color="#1f2a38",
            text_color="white",
            placeholder_text="Enter description",
            corner_radius=8,
            border_width=2,
            border_color="#365580",
            height=25
        ).pack(fill="x", pady=(0, 8))

        # ---------------- CWT ----------------
        ctk.CTkLabel(
            root_frame,
            text="CWT (withholding tax, if any):",
            text_color="white",
            font=ctk.CTkFont(size=14)
        ).pack(anchor="w", pady=(5, 2))

        self.cwt_var = tk.StringVar(
            value=f"{row_data['cwt']:,.2f}" if row_data else ""
        )
        self.cwt_entry = ctk.CTkEntry(
            root_frame,
            textvariable=self.cwt_var,
            fg_color="#1f2a38",
            text_color="white",
            placeholder_text="Enter CWT",
            corner_radius=8,
            border_width=2,
            border_color="#365580",
            height=25
        )
        self.cwt_entry.pack(fill="x", pady=(0, 8))

        self.cwt_entry.bind(
            "<FocusOut>",
            lambda e: self.format_amount(self.cwt_var)
        )
        self.cwt_var.trace_add("write", self.update_received)

        # ---------------- ATC ----------------
        ctk.CTkLabel(
            root_frame,
            text="ATC Code (optional):",
            text_color="white",
            font=ctk.CTkFont(size=14)
        ).pack(anchor="w", pady=(5, 2))

        self.atc_var = tk.StringVar(value=row_data.get("atc") if row_data else "")
        ctk.CTkEntry(
            root_frame,
            textvariable=self.atc_var,
            fg_color="#1f2a38",
            text_color="white",
            placeholder_text="Enter ATC code (optional)",
            corner_radius=8,
            border_width=2,
            border_color="#365580",
            height=25
        ).pack(fill="x", pady=(0, 8))

        # ---------------- INCOME RECEIVED ----------------
        ctk.CTkLabel(
            root_frame,
            text="Income Received (auto-calculated):",
            text_color="white",
            font=ctk.CTkFont(size=14),
        ).pack(anchor="w", pady=(5, 2))

        self.received_var = tk.StringVar(value=row_data["income_received"] if row_data else 0)
        ctk.CTkEntry(
            root_frame,
            textvariable=self.received_var,
            state="readonly",
            font=("Arial", 15),
            fg_color="#040f21",
            text_color="white",
            corner_radius=8,
            border_width=2,
            border_color="#365580",
            height=25
        ).pack(fill="x", pady=(0, 8))

        # ---------------- BUTTONS ----------------
        btn_frame = ctk.CTkFrame(root_frame, fg_color="#040f21", corner_radius=12)
        btn_frame.pack(fill="x", pady=(30, 10))

        BTN_HEIGHT = 40
        BTN_RADIUS = 12

        ctk.CTkButton(
            btn_frame,
            text="Save",
            height=BTN_HEIGHT,
            corner_radius=BTN_RADIUS,
            fg_color="#3d77d4",
            hover_color="#040f21",
            border_color="#3d77d4",
            text_color="white",
            font=ctk.CTkFont(size=14),
            border_width=3,
            command=self.save_income
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            height=BTN_HEIGHT,
            corner_radius=BTN_RADIUS,
            fg_color="#b81c1c",
            hover_color="#040f21",
            border_color="#b81c1c",
            text_color="white",
            font=ctk.CTkFont(size=14),
            border_width=3,
            command=self.destroy
        ).pack(side="left")

        # ---------------- INITIAL CALCULATION ----------------
        self.update_received()

        # ---------------- CENTER & FRONT ----------------
        self.update_idletasks()
        self.after(10, lambda: self.center_window(parent))
        self.lift()
        self.focus_force()
        self.attributes("-topmost", True)
        self.after(100, lambda: self.attributes("-topmost", False))

    # ---------------- CENTER WINDOW ----------------
    def center_window(self, parent):
        self.update_idletasks()

        # Dialog size
        w = self.winfo_width()
        h = self.winfo_height()

        # Parent position and size (absolute screen coords)
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_w = parent.winfo_width()
        parent_h = parent.winfo_height()

        # Add offset corrections here (example: shift left by 10px, up by 5px)
        offset_x = -10
        offset_y = -55

        x = parent_x + (parent_w // 2) - (w // 2) + offset_x
        y = parent_y + (parent_h // 2) - (h // 2) + offset_y

        self.geometry(f"{w}x{h}+{x}+{y}")

    # ---------------- LOGIC ----------------
    def parse_amount(self, value: str) -> float:
        if not value:
            return 0.0
        return float(value.replace(",", ""))

    def format_amount(self, var: tk.StringVar):
        try:
            value = self.parse_amount(var.get())
            if value == 0:
                var.set("")
            else:
                var.set(f"{value:,.2f}")
        except ValueError:
            var.set("")

    def update_received(self, *args):
        try:
            gross = self.parse_amount(self.amount_var.get())
            cwt = self.parse_amount(self.cwt_var.get())
            received = max(0, gross - cwt)

            if received == 0:
                self.received_var.set("")
            else:
                self.received_var.set(f"{received:,.2f}")
        except ValueError:
            self.received_var.set("")

    def save_income(self):
        try:
            record_date = self.date_var.get()
            datetime.fromisoformat(record_date)
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD.")
            return

        gross_income = self.parse_amount(self.amount_var.get())
        cwt = self.parse_amount(self.cwt_var.get())
        income_received  = gross_income - cwt

        if gross_income <= 0:
            messagebox.showerror("Error", "Gross income must be greater than 0.")
            return

        data = {
            "date": record_date,
            "description": self.desc_var.get(),
            "gross_income": gross_income,
            "cwt": cwt,
            "atc": self.atc_var.get(),
            "income_received": income_received
        }

        if self.row_data:
            new_id = self.row_data["id"]
            self.storage.update_income(new_id, data)
        else:
            new_id = self.storage.add_income(data)

        messagebox.showinfo("Saved", "Income recorded successfully ✅")

        if self.refresh_callback:
            try:
                self.refresh_callback(new_id)
            except TypeError:
                self.refresh_callback()

        self.parent.deiconify()
        self.destroy()

    def on_close(self):
        self.parent.deiconify()  # bring main window back
        self.parent.update_idletasks()

        # restore full-screen size
        sw = self.parent.winfo_screenwidth()
        sh = self.parent.winfo_screenheight()
        self.parent.geometry(f"{sw}x{sh}+{-8}+{-5}")

        self.destroy()  # close this form