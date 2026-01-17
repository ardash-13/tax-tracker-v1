# ================== IMPORTS ==================
# Standard library
from datetime import date, datetime
import tkinter as tk
from tkinter import ttk, messagebox

# Third-party
import customtkinter as ctk

# Core modules
from core.storage import StorageManager
from core.backup import backup_income, backup_expense, backup_summary
from core.license_manager import check_license

# GUI modules
from gui.setup_wizard import SetupWizard
from gui.income_form import IncomeForm
from gui.expense_form import ExpenseForm
from gui.reports_tab import ReportsTab
from gui.license_dialog import LicenseDialog

# Local modules
from .reminders import check_filing_reminders


# ================== MAIN WINDOW ==================
class MainWindow:
    def __init__(self, root, app_state):
        self.root = root
        self.app_state = app_state
        self.storage = StorageManager()
        self.undo_stack = []

        # ================== CTK GLOBAL ==================
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # ================== WINDOW ==================
        self.root.title("Non-VAT Income & Expense Tax Tracker")
        # self.root.state("zoomed")
        # self.root.attributes("-fullscreen", True)
        self.root.configure(bg="#040f21")

        # Get screen size
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Set fixed full-screen size (fills the screen but keeps title bar / X button)
        self.root.geometry(f"{screen_width}x{screen_height}+{-8}+{-5}")
        self.root.resizable(False, False)  # prevent resizing

        # ================== ROOT CONTAINER ==================
        self.main_container = ctk.CTkFrame(
            self.root,
            fg_color="#040f21",
            corner_radius=0
        )
        self.main_container.pack(fill="both", expand=True)

        # ================== HEADER ==================
        self.header = ctk.CTkFrame(
            self.main_container,
            height=75,
            fg_color="#040f21",
            corner_radius=0
        )
        self.header.pack(fill="x", padx=16, pady=(20, 10))
        self.header.pack_propagate(False)

        self.header_left = ctk.CTkFrame(
            self.header,
            fg_color="#040f21"
        )
        self.header_left.pack(side="left", padx=30, pady=10)

        self.title_label = ctk.CTkLabel(
            self.header_left,
            text="Non-VAT Income & Expense Tax Tracker",
            font=("Segoe UI", 25, "bold"),
            text_color="#ffffff"
        )
        self.title_label.pack(anchor="w")

        self.subtitle_label = ctk.CTkLabel(
            self.header_left,
            text="An efficient solution for tracking income, expense, and taxes in Non-VAT businesses.",
            font=("Segoe UI", 14),
            text_color="#b6c2d4"
        )
        self.subtitle_label.pack(anchor="w", pady=(3, 0))

        # ================== CONTENT ==================
        self.content = ctk.CTkFrame(
            self.main_container,
            fg_color="#040f21",
            corner_radius=0
        )
        self.content.pack(fill="both", expand=True, padx=30, pady=20)

        # ================== TTK STYLE ==================
        self.style = ttk.Style()
        self.style.theme_use("default")

        # ---------- NOTEBOOK ----------
        self.style.configure(
            "TNotebook",
            background="#040f21",
            borderwidth=0
        )

        self.style.configure(
            "TNotebook.Tab",
            padding=(30, 10),
            font=("Segoe UI", 9),
            background="#111827",
            foreground="#669ef2",
            borderwidth=0
        )

        self.style.map(
            "TNotebook.Tab",
            foreground=[("selected", "#040f21")],
            background=[("selected", "#5d8dd4")]
        )

        # ---------- TREEVIEW ----------
        self.style.configure(
            "Treeview",
            font=("Segoe UI", 11),
            rowheight=30,
            background="#040f21",
            fieldbackground="#040f21",
            foreground="#ffffff",
            borderwidth=0,
            relief="flat"
        )

        self.style.configure(
            "Treeview.Heading",
            font=("Segoe UI", 12, "bold"),
            background="#040f21",
            foreground="#ffffff",
            borderwidth=0,
            relief="flat"
        )

        self.style.map(
            "Treeview",
            background=[("selected", "#1a2945")],
            foreground=[("selected", "#ffffff")]
        )

        self.style.map(
            "Treeview.Heading",
            background=[("active", "#040f21")],
            relief=[("active", "flat")]
        )

        self.root.bind_all("<FocusIn>", lambda e: self.root.focus_set())

        # ================== MENU ==================
        self.build_menu()

        # ================== APP FLOW ==================
        self.tracking_enabled = False

        self.build_tabs()  # UI must exist first

        self.check_existing_license()

        if not self.tracking_enabled:
            self.root.after(100, self.show_license_popup)

        self.lock_treeview(self.income_table)
        self.lock_treeview(self.expense_table)

        self.check_vat_threshold()
        self.safe_check_filing_reminders()

        self.update_ui_state()

    def lock_treeview(self, tree):
        if not tree:
            return

        for col in tree["columns"]:
            tree.column(col, stretch=False, width=130)

        # ttk-safe options only
        tree.configure(takefocus=False)
        tree.bind("<Motion>", lambda e: "break")

    def safe_check_filing_reminders(self):
        try:
            check_filing_reminders()
        except tk.TclError:
            pass

    # ================== MENU ==================
    def build_menu(self):
        # Create the menubar
        menubar = tk.Menu(
            self.root,
            bg="#040f21",
            fg="#fff",
            activebackground="#040f21",
            activeforeground="#fff",
            bd=0,
            borderwidth=1
        )

        # LICENSE MENU
        license_menu = tk.Menu(
            menubar,
            tearoff=0,
            bg="#fff",
            fg="#111",
            activebackground="#fff",
            activeforeground="#111"
        )
        # Make sure the command actually calls your dialog
        license_menu.add_command(
            label="Import Activation File",
            command=self.open_license_dialog  # just call directly
        )

        menubar.add_cascade(label="License", menu=license_menu)

        # PROFILE MENU
        profile_menu = tk.Menu(
            menubar,
            tearoff=0,
            bg="#fff",
            fg="#111",
            activebackground="#fff",
            activeforeground="#111"
        )
        profile_menu.add_command(label="Edit Profile", command=self.open_edit_profile)
        menubar.add_cascade(label="Profile", menu=profile_menu)

        # ABOUT MENU
        about_menu = tk.Menu(
            menubar,
            tearoff=0,
            bg="#fff",
            fg="#111",
            activebackground="#fff",
            activeforeground="#111"
        )
        about_menu.add_command(label="About", command=self.open_about)
        menubar.add_cascade(label="About", menu=about_menu)

        # Link menubar to root
        self.root.config(menu=menubar)

    # ================= LICENSE =================
    def on_license_success(self):
        messagebox.showinfo("License Activated", "License imported and activated!")
        self.enable_features()  # enable app features after license
        self.tracking_enabled = True

    # ================= ABOUT =================
    def open_about(self):
        from gui.about_dialog import AboutDialog
        AboutDialog(self.root)

    # ================= TABS =================
    def build_tabs(self):
        # Notebook (layout only)
        self.tabs = ttk.Notebook(self.content)
        self.tabs.pack(fill="both", expand=True, padx=0, pady=0)

        # Raw ttk frames (NO UI, just containers)
        self.income_tab = ttk.Frame(self.tabs)
        self.expense_tab = ttk.Frame(self.tabs)

        self.tabs.add(self.income_tab, text="INCOME")
        self.tabs.add(self.expense_tab, text="EXPENSE")

        self.build_income_tab()
        self.build_expense_tab()

        self.build_reports_tab()

    # ================= INCOME TAB =================
    def build_income_tab(self):
        # ================= ROOT CTK CONTAINER =================
        income_root = ctk.CTkFrame(
            self.income_tab,
            fg_color="#040f21",
            corner_radius=0
        )
        income_root.pack(fill="both", expand=True)

        # ================= HEADER =================
        header = ctk.CTkFrame(
            income_root,
            fg_color="#040f21",
            corner_radius=0
        )
        header.pack(fill="x", padx=16, pady=(20, 10))

        self.income_label = ctk.CTkLabel(
            header,
            text="Income Records",
            font=("Segoe UI", 26, "bold"),
            text_color="#ffffff"
        )
        self.income_label.pack(anchor="w")

        ctk.CTkLabel(
            header,
            text="Track gross income, withholding tax, and collections",
            font=("Segoe UI", 14),
            text_color="#b6c2d4"
        ).pack(anchor="w", pady=(4, 0))

        # ================= FILTER CONTROLS =================
        controls = ctk.CTkFrame(
            income_root,
            fg_color="#040f21",
            corner_radius=0
        )
        controls.pack(fill="x", padx=16, pady=(10, 30))

        self.income_view_var = tk.StringVar(value="Quarter")
        self.income_year_var = tk.StringVar()
        self.income_quarter_var = tk.StringVar()

        # ---------------- HELPER: GET CURRENT QUARTER ----------------
        def get_current_quarter():
            m = date.today().month
            return "Q1" if m <= 3 else "Q2" if m <= 6 else "Q3" if m <= 9 else "Q4"

        # ---------------- FUNCTION TO UPDATE QUARTER STATE ----------------
        def update_income_quarter_state(*args):
            if self.income_view_var.get() == "Annual":
                self.income_quarter_dropdown.configure(state="disabled")
            else:
                self.income_quarter_dropdown.configure(state="normal")
            # only call load_income_table if table exists
            if hasattr(self, "income_table"):
                self.load_income_table()  # refresh table whenever dropdown changes

        # ---------------- VIEW DROPDOWN ----------------
        self.income_view_dropdown = ctk.CTkOptionMenu(
            controls,
            values=["Quarter", "Annual"],
            variable=self.income_view_var,
            width=140,
            fg_color="#2b3545",
            button_color="#2b3545",
            dropdown_fg_color="#2b3545",
            dropdown_hover_color="#246ae3",
            text_color="#ffffff"
        )
        self.income_view_var.trace_add("write", update_income_quarter_state)
        self.income_view_dropdown.pack(side="left", padx=(0, 8))

        # ---------------- YEAR DROPDOWN ----------------
        years = [r["year"] for r in self.storage.cursor.execute("""
            SELECT DISTINCT strftime('%Y', date) AS year
            FROM income
            ORDER BY year DESC
        """).fetchall()]

        current_year = str(date.today().year)
        if current_year not in years:
            years.insert(0, current_year)

        self.income_year_var.set(current_year)
        self.income_year_dropdown = ctk.CTkOptionMenu(
            controls,
            values=years,
            variable=self.income_year_var,
            width=100,
            fg_color="#2b3545",
            button_color="#2b3545",
            dropdown_fg_color="#2b3545",
            dropdown_hover_color="#246ae3",
            text_color="#ffffff"
        )
        self.income_year_var.trace_add("write", lambda *args: self.load_income_table() if hasattr(self,
                                                                                                  "income_table") else None)
        self.income_year_dropdown.pack(side="left", padx=8)

        # ---------------- QUARTER DROPDOWN ----------------
        self.income_quarter_var.set(get_current_quarter())
        self.income_quarter_dropdown = ctk.CTkOptionMenu(
            controls,
            values=["Q1", "Q2", "Q3", "Q4"],
            variable=self.income_quarter_var,
            width=100,
            fg_color="#2b3545",
            button_color="#2b3545",
            dropdown_fg_color="#2b3545",
            dropdown_hover_color="#246ae3",
            text_color="#ffffff"
        )
        self.income_quarter_var.trace_add("write", lambda *args: self.load_income_table() if hasattr(self,
                                                                                                     "income_table") else None)
        self.income_quarter_dropdown.pack(side="left", padx=8)

        # ---------------- INITIALIZE QUARTER STATE ----------------
        # only call if table exists
        if hasattr(self, "income_table"):
            update_income_quarter_state()

        # ================= ACTION BUTTONS =================
        btns = ctk.CTkFrame(income_root, fg_color="#040f21")
        btns.pack(fill="x", padx=16, pady=(0, 10))
        BTN_HEIGHT = 36
        BTN_RADIUS = 8

        self.add_income_btn = ctk.CTkButton(
            btns,
            text="Add Income",
            height=BTN_HEIGHT,
            corner_radius=BTN_RADIUS,
            fg_color="#2042a1",
            hover_color="#040f21",
            text_color="#fff",
            border_color="#2042a1",
            border_width=2,
            command=self.add_income
        )
        self.add_income_btn.pack(side="left", padx=(0, 10), pady=8)

        self.edit_income_btn = ctk.CTkButton(
            btns,
            text="Edit",
            height=BTN_HEIGHT,
            corner_radius=BTN_RADIUS,
            fg_color="#2042a1",
            hover_color="#040f21",
            text_color="#fff",
            border_color="#2042a1",
            border_width=2,
            command=self.edit_selected_income
        )
        self.edit_income_btn.pack(side="left", padx=10, pady=8)

        self.delete_income_btn = ctk.CTkButton(
            btns,
            text="Delete",
            height=BTN_HEIGHT,
            corner_radius=BTN_RADIUS,
            fg_color="#ab3226",
            hover_color="#b81c1c",
            text_color="white",
            border_color="#C0392B",
            border_width=2,
            command=self.delete_selected_income
        )
        self.delete_income_btn.pack(side="left", padx=10, pady=8)

        self.undo_income_btn = ctk.CTkButton(
            btns,
            text="Undo",
            height=BTN_HEIGHT,
            corner_radius=BTN_RADIUS,
            fg_color="#2042a1",
            hover_color="#040f21",
            text_color="#fff",
            border_color="#2042a1",
            border_width=2,
            command=self.undo_action
        )
        self.undo_income_btn.pack(side="left", padx=10, pady=8)

        # ================= TABLE CARD =================
        self.income_table_card = ctk.CTkFrame(
            income_root,
            fg_color="#2E3458",
            corner_radius=15,
            border_width=5,  # Thickness of the border
            border_color="#246ae3"  # Border color
        )
        self.income_table_card.pack(fill="both", expand=True, padx=16, pady=(16, 16))

        columns = ("date", "gross_income", "description", "cwt", "atc", "income_received")
        self.income_table = ttk.Treeview(
            self.income_table_card,
            columns=columns,
            show="headings",
        )

        # Set initial column headings and minimal config
        for col in columns:
            self.income_table.heading(col, text=col.replace("_", " ").title())
            self.income_table.column(col, anchor="center", stretch=False, width=140)

        self.income_table.pack(fill="both", expand=True, padx=5, pady=5)

        self.load_income_table()  # Your existing method to populate data

        # Adjust column widths initially and on resize
        self.income_table_card.after(100, self.adjust_income_columns)
        self.income_table_card.bind("<Configure>", lambda e: self.adjust_income_columns())

    def adjust_income_columns(self):
        self.income_table_card.update_idletasks()  # Ensure layout is updated
        total_width = self.income_table_card.winfo_width()  # Get container width

        columns = self.income_table["columns"]
        if len(columns) == 0:
            return  # Avoid division by zero

        col_width = int(total_width / len(columns))  # Equal width per column

        for col in columns:
            self.income_table.column(col, width=col_width, anchor="center")

    # ================= EXPENSE TAB =================
    def build_expense_tab(self):
        # ================= ROOT CTK CONTAINER =================
        expense_root = ctk.CTkFrame(
            self.expense_tab,
            fg_color="#040f21",
            corner_radius=0
        )
        expense_root.pack(fill="both", expand=True)

        # ================= HEADER =================
        header = ctk.CTkFrame(
            expense_root,
            fg_color="#040f21",
            corner_radius=0
        )
        header.pack(fill="x", padx=16, pady=(20, 10))

        self.expense_label = ctk.CTkLabel(
            header,
            text="Deductible Expenses",
            font=("Segoe UI", 26, "bold"),
            text_color="#ffffff"
        )
        self.expense_label.pack(anchor="w")

        ctk.CTkLabel(
            header,
            text="Manage business expenses and tax deductions",
            font=("Segoe UI", 14),
            text_color="#b6c2d4"
        ).pack(anchor="w", pady=(4, 0))

        # ================= FILTER CONTROLS =================
        controls = ctk.CTkFrame(
            expense_root,
            fg_color="#040f21",
            corner_radius=0
        )
        controls.pack(fill="x", padx=16, pady=(10, 30))

        self.expense_view_var = tk.StringVar(value="Quarter")
        self.expense_year_var = tk.StringVar()
        self.expense_quarter_var = tk.StringVar(value="Q1")

        self.expense_view_dropdown = ctk.CTkOptionMenu(
            controls,
            values=["Quarter", "Annual"],
            variable=self.expense_view_var,
            width=140,
            fg_color="#2b3545",
            button_color="#2b3545",
            dropdown_fg_color="#2b3545",
            dropdown_hover_color="#246ae3",
            text_color="#ffffff"
        )
        self.expense_view_dropdown.pack(side="left", padx=(0, 8))

        self.expense_year_dropdown = ctk.CTkOptionMenu(
            controls,
            values=[str(date.today().year)],
            variable=self.expense_year_var,
            width=100,
            fg_color="#2b3545",
            button_color="#2b3545",
            dropdown_fg_color="#2b3545",
            dropdown_hover_color="#246ae3",
            text_color="#ffffff"
        )
        self.expense_year_dropdown.pack(side="left", padx=8)

        self.expense_quarter_dropdown = ctk.CTkOptionMenu(
            controls,
            values=["Q1", "Q2", "Q3", "Q4"],
            variable=self.expense_quarter_var,
            width=100,
            fg_color="#2b3545",
            button_color="#2b3545",
            dropdown_fg_color="#2b3545",
            dropdown_hover_color="#246ae3",
            text_color="#ffffff"
        )
        self.expense_quarter_dropdown.pack(side="left", padx=8)

        # ================= ACTION BUTTONS =================
        btns = ctk.CTkFrame(expense_root, fg_color="#040f21")
        btns.pack(fill="x", padx=16, pady=(0, 10))
        BTN_HEIGHT = 36
        BTN_RADIUS = 8

        self.add_expense_btn = ctk.CTkButton(
            btns,
            text="Add Expense",
            height=BTN_HEIGHT,
            corner_radius=BTN_RADIUS,
            fg_color="#2042a1",
            hover_color="#040f21",
            text_color="#fff",
            border_color="#2042a1",
            border_width=2,
            command=self.add_expense
        )
        self.add_expense_btn.pack(side="left", padx=(0, 10), pady=8)

        self.edit_expense_btn = ctk.CTkButton(
            btns,
            text="Edit",
            height=BTN_HEIGHT,
            corner_radius=BTN_RADIUS,
            fg_color="#2042a1",
            hover_color="#040f21",
            text_color="#fff",
            border_color="#2042a1",
            border_width=2,
            command=self.edit_selected_expense
        )
        self.edit_expense_btn.pack(side="left", padx=10, pady=8)

        self.delete_expense_btn = ctk.CTkButton(
            btns,
            text="Delete",
            height=BTN_HEIGHT,
            corner_radius=BTN_RADIUS,
            fg_color="#ab3226",
            hover_color="#b81c1c",
            text_color="white",
            border_color="#b81c1c",
            border_width=2,
            command=self.delete_selected_expense
        )
        self.delete_expense_btn.pack(side="left", padx=10, pady=8)

        self.undo_expense_btn = ctk.CTkButton(
            btns,
            text="Undo",
            height=BTN_HEIGHT,
            corner_radius=BTN_RADIUS,
            fg_color="#2042a1",
            hover_color="#040f21",
            text_color="#fff",
            border_color="#2042a1",
            border_width=2,
            command=self.undo_action
        )
        self.undo_expense_btn.pack(side="left", padx=10, pady=8)

        # ================= TABLE CARD =================
        self.expense_table_card = ctk.CTkFrame(
            expense_root,
            fg_color="#2E3458",
            corner_radius=15,
            border_width=5,  # Thickness of the border
            border_color="#246ae3"  # Border color
        )
        self.expense_table_card.pack(fill="both", expand=True, padx=16, pady=(16, 16))

        columns = ("date", "gross_expense", "description", "wt", "atc", "expense_paid")
        self.expense_table = ttk.Treeview(
            self.expense_table_card,
            columns=columns,
            show="headings"
        )

        # Set initial column headings and minimal config
        for col in columns:
            self.expense_table.heading(col, text=col.replace("_", " ").title())
            self.expense_table.column(col, anchor="center", stretch=False, width=140)

        self.expense_table.pack(fill="both", expand=True, padx=5, pady=5)

        self.load_expense_table()  # Your existing method to populate data

        # Adjust column widths initially and on resize
        self.adjust_expense_columns()
        self.expense_table_card.bind("<Configure>", lambda e: self.adjust_expense_columns())

    def adjust_expense_columns(self):
        self.expense_table_card.update_idletasks()  # Ensure layout is updated
        total_width = self.expense_table_card.winfo_width()  # Get container width

        columns = self.expense_table["columns"]
        if len(columns) == 0:
            return  # Avoid division by zero

        col_width = int(total_width / len(columns))  # Equal width per column

        for col in columns:
            self.expense_table.column(col, width=col_width, anchor="center")

    # ================= REPORTS TAB =================
    def build_reports_tab(self):
        self.reports_tab = ReportsTab(self.tabs, self.storage, self.app_state)
        self.tabs.add(self.reports_tab, text="REPORTS")

    # ================= LOAD TABLES =================
    def update_income_years_dropdown(self):
        """Refresh the year dropdown based on actual income data."""
        # Get all distinct years in the income table
        years = [row["year"] for row in self.storage.cursor.execute("""
            SELECT DISTINCT strftime('%Y', date) AS year
            FROM income
            ORDER BY year DESC
        """).fetchall()]

        current_year = str(date.today().year)
        if current_year not in years:
            years.insert(0, current_year)

        # Update the dropdown values
        self.income_year_dropdown.configure(values=years)

        # If current selection is gone, reset to current year
        if self.income_year_var.get() not in years:
            self.income_year_var.set(current_year)

    def load_income_table(self):
        self.update_income_years_dropdown()

        # Clear table
        for row in self.income_table.get_children():
            self.income_table.delete(row)

        all_incomes = self.storage.get_all_income()

        # ----------------- Year filter -----------------
        years = sorted({int(rec["date"][:4]) for rec in all_incomes})
        if not years:
            years = [date.today().year]
        self.income_year_dropdown['values'] = years

        selected_year = self.income_year_var.get()
        if selected_year not in map(str, years):
            selected_year = str(years[-1])
            self.income_year_var.set(selected_year)

        filtered_incomes = [inc for inc in all_incomes if inc["date"].startswith(selected_year)]

        # ----------------- Quarter filter -----------------
        if self.income_view_var.get() == "Quarter":
            quarter = self.income_quarter_var.get()
            month_start = {"Q1": 1, "Q2": 4, "Q3": 7, "Q4": 10}[quarter]
            month_end = month_start + 2
            filtered_incomes = [
                inc for inc in filtered_incomes
                if month_start <= int(inc["date"][5:7]) <= month_end
            ]
        # No state changes here — handled in update_income_quarter_state()

        # ----------------- Populate table -----------------
        for income in filtered_incomes:
            iid = str(income["id"])
            if iid in self.income_table.get_children():  # remove duplicate if exists
                self.income_table.delete(iid)
            self.income_table.insert(
                "",
                "end",
                iid=iid,
                values=(
                    income["date"],
                    f"₱{income['gross_income']:,.2f}",
                    income.get("description", ""),
                    f"₱{income['cwt']:,.2f}",
                    income.get("atc", ""),
                    f"₱{income['income_received']:,.2f}"
                )
            )

    def load_expense_table(self):
        # Clear table
        for row in self.expense_table.get_children():
            self.expense_table.delete(row)

        all_expenses = self.storage.get_all_expense()

        # ----------------- Year filter -----------------
        years = sorted({int(rec["date"][:4]) for rec in all_expenses})
        if not years:
            years = [date.today().year]
        self.expense_year_dropdown['values'] = years

        selected_year = self.expense_year_var.get()
        if selected_year not in map(str, years):
            selected_year = str(years[-1])
            self.expense_year_var.set(selected_year)

        filtered_expenses = [exp for exp in all_expenses if exp["date"].startswith(selected_year)]

        # ----------------- Quarter filter -----------------
        if self.expense_view_var.get() == "Quarter":
            quarter = self.expense_quarter_var.get()
            month_start = {"Q1": 1, "Q2": 4, "Q3": 7, "Q4": 10}[quarter]
            month_end = month_start + 2
            filtered_expenses = [
                exp for exp in filtered_expenses
                if month_start <= int(exp["date"][5:7]) <= month_end
            ]
        # No state changes here — handled in update_expense_quarter_state()

        # ----------------- Populate table -----------------
        for expense in filtered_expenses:
            iid = str(expense["id"])
            if iid in self.expense_table.get_children():  # remove duplicate if exists
                self.expense_table.delete(iid)
            self.expense_table.insert(
                "",
                "end",
                iid=iid,
                values=(
                    expense["date"],
                    f"₱{expense['gross_expense']:,.2f}",
                    expense.get("description", ""),
                    f"₱{expense['wt']:,.2f}",
                    expense.get("atc", ""),
                    f"₱{expense['expense_paid']:,.2f}"
                )
            )

    # ================= QUARTER STATE =================
    def update_income_quarter_state(self):
        if self.income_view_var.get() == "Annual":
            #self.income_quarter_label.grid_forget()  # Hide "Quarter" label
            self.income_quarter_dropdown.configure(state="disabled")
        else:
            self.income_quarter_label.grid(row=0, column=4, padx=10)  # Show "Quarter" label
            self.income_quarter_dropdown.configure(state="readonly")
        self.load_income_table()

    def update_expense_quarter_state(self):
        if self.expense_view_var.get() == "Annual":
            # self.expense_quarter_label.grid_forget()  # Hide "Quarter" label
            self.expense_quarter_dropdown.configure(state="disabled")
        else:
            self.expense_quarter_label.grid(row=0, column=4, padx=10)  # Show "Quarter" label
            self.expense_quarter_dropdown.configure(state="readonly")
        self.load_expense_table()

    # ================= ADD / EDIT / DELETE / UNDO =================
    def add_income(self):
        def on_save(new_id):
            self.undo_stack.append({"action": "add", "type": "income", "record_id": new_id, "old_data": None})
            self.load_income_table()
            backup_income(self.storage)
            backup_summary(self.storage, self.app_state, datetime.now().year)
            self.reports_tab.load_report_years()
            self.reports_tab.refresh()

            # --- new: check VAT threshold immediately ---
            self.check_vat_threshold()
            # --- optional: check filing reminders ---
            self.safe_check_filing_reminders()

        self.root.withdraw()
        IncomeForm(self.root, self.storage, refresh_callback=on_save)
        # IncomeForm(self.root, self.storage, refresh_callback=on_save).wait_window()

    def edit_selected_income(self):
        selected = self.income_table.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a record to edit.")
            return
        record_id = int(selected[0])
        record = next(i for i in self.storage.get_all_income() if i["id"] == record_id)
        before_edit = record.copy()

        def on_save(updated_id):
            self.undo_stack.append({"action": "edit", "type": "income", "record_id": updated_id, "old_data": before_edit})
            self.load_income_table()
            backup_income(self.storage)
            backup_summary(self.storage, self.app_state, datetime.now().year)
            self.reports_tab.load_report_years()
            self.reports_tab.refresh()

            # --- new: check VAT threshold immediately ---
            self.check_vat_threshold()
            # --- optional: check filing reminders ---
            self.safe_check_filing_reminders()

        self.root.withdraw()
        IncomeForm(self.root, self.storage, record, refresh_callback=on_save)

    def delete_selected_income(self):
        selected = self.income_table.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a record to delete.")
            return
        record_id = int(selected[0])
        record = next(i for i in self.storage.get_all_income() if i["id"] == record_id)

        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this income record?"):
            self.undo_stack.append({"action": "delete", "type": "income", "record_id": None, "old_data": record})
            self.storage.delete_income(record_id)
            self.load_income_table()
            backup_income(self.storage)
            backup_summary(self.storage, self.app_state, datetime.now().year)
            self.reports_tab.load_report_years()
            self.reports_tab.refresh()
            # --- new: check VAT threshold immediately ---
            self.check_vat_threshold()
            # --- optional: check filing reminders ---
            self.safe_check_filing_reminders()

    def add_expense(self):
        def on_save(new_id):
            self.undo_stack.append({"action": "add", "type": "expense", "record_id": new_id, "old_data": None})
            self.load_expense_table()
            backup_expense(self.storage)
            backup_summary(self.storage, self.app_state, datetime.now().year)
            self.reports_tab.load_report_years()
            self.reports_tab.refresh()

            # --- new: check VAT threshold immediately ---
            self.check_vat_threshold()
            # --- optional: check filing reminders ---
            self.safe_check_filing_reminders()

        self.root.withdraw()
        ExpenseForm(self.root, self.storage, refresh_callback=on_save)
        # ExpenseForm(self.root, self.storage, refresh_callback=on_save).wait_window()

    def edit_selected_expense(self):
        selected = self.expense_table.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a record to edit.")
            return
        record_id = int(selected[0])
        record = next(i for i in self.storage.get_all_expense() if i["id"] == record_id)
        before_edit = record.copy()

        def on_save(updated_id):
            self.undo_stack.append({"action": "edit", "type": "expense", "record_id": updated_id, "old_data": before_edit})
            self.load_expense_table()
            backup_expense(self.storage)
            backup_summary(self.storage, self.app_state, datetime.now().year)
            self.reports_tab.load_report_years()
            self.reports_tab.refresh()

            # --- new: check VAT threshold immediately ---
            self.check_vat_threshold()
            # --- optional: check filing reminders ---
            self.safe_check_filing_reminders()

        self.root.withdraw()
        ExpenseForm(self.root, self.storage, record, refresh_callback=on_save)

    def delete_selected_expense(self):
        selected = self.expense_table.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a record to delete.")
            return
        record_id = int(selected[0])
        record = next(i for i in self.storage.get_all_expense() if i["id"] == record_id)

        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this expense record?"):
            self.undo_stack.append({"action": "delete", "type": "expense", "record_id": None, "old_data": record})
            self.storage.delete_expense(record_id)
            self.load_expense_table()
            backup_expense(self.storage)
            backup_summary(self.storage, self.app_state, datetime.now().year)
            self.reports_tab.load_report_years()
            self.reports_tab.refresh()
            # --- new: check VAT threshold immediately ---
            self.check_vat_threshold()
            # --- optional: check filing reminders ---
            self.safe_check_filing_reminders()

    def undo_action(self):
        if not self.undo_stack:
            messagebox.showinfo("Undo", "Nothing to undo.")
            return

        last = self.undo_stack.pop()
        action = last["action"]
        rtype = last["type"]
        rid = last.get("record_id")
        old = last.get("old_data")

        if action == "add":
            if rtype == "income":
                self.storage.delete_income(rid)
                self.load_income_table()
            else:
                self.storage.delete_expense(rid)
                self.load_expense_table()
        elif action == "delete":
            if rtype == "income":
                self.storage.restore_income(old)
                self.load_income_table()
            else:
                self.storage.restore_expense(old)
                self.load_expense_table()
        elif action == "edit":
            if rtype == "income":
                self.storage.update_income(rid, old)
                self.load_income_table()
            else:
                self.storage.update_expense(rid, old)
                self.load_expense_table()

        backup_income(self.storage)
        backup_expense(self.storage)
        current_year = datetime.now().year
        backup_summary(self.storage, self.app_state, current_year)
        self.reports_tab.load_report_years()
        self.reports_tab.refresh()
        # --- new: check VAT threshold immediately ---
        self.check_vat_threshold()
        # --- optional: check filing reminders ---
        self.safe_check_filing_reminders()

    # ================= LICENSE & PROFILE =================
    def check_existing_license(self):
        """Check license in proper license folder and enable features if valid."""
        status, license_data = check_license()  # uses data/license internally

        # ================= VALID LICENSE =================
        if status == "valid":
            self.enable_features()

            # 🔔 LICENSE EXPIRY NOTIFICATIONS
            expiry_date = license_data.get("_expiry_date")
            if expiry_date:
                days_left = (expiry_date - date.today()).days

                # ⚠ 3 DAYS BEFORE EXPIRY
                if days_left == 3:
                    messagebox.showwarning(
                        "License Expiring Soon",
                        "⚠ Your license will expire in 3 days.\n\n"
                        "Please prepare and import a new license to avoid interruption."
                    )

                # ⛔ EXPIRY DAY
                elif days_left == 0:
                    messagebox.showerror(
                        "License Expired Today",
                        "⛔ Your license expires today.\n\n"
                        "You must import a new license to continue using the app."
                    )

            return True

        # ================= EXPIRED =================
        elif status == "expired":
            messagebox.showerror(
                "License Expired",
                "⛔ Your license has expired.\n\n"
                "Please import a new license to continue using the application."
            )
            self.tracking_enabled = False
            return False

        # ================= SYSTEM DATE WARNING =================
        elif status == "warning":
            messagebox.showwarning(
                "System Date Error",
                "⚠ Your system date appears to have been changed.\n\n"
                "Please restore the correct date to continue using the application."
            )
            self.root.destroy()
            return False

        # ================= INVALID =================
        elif status == "invalid":
            messagebox.showerror(
                "Invalid License",
                "Your license is invalid.\n\n"
                "Please import a valid license file."
            )
            self.tracking_enabled = False
            return False

        # ================= MISSING =================
        else:
            self.tracking_enabled = False
            return False

    # VAT THRESHOLD NOTIF
    def check_vat_threshold(self):
        current_year = datetime.now().year
        gross_income = self.storage.get_year_gross_income(current_year)

        if gross_income >= 3_000_000:
            messagebox.showwarning(
                "⚠ VAT Threshold Reached",
                "Your recorded gross sales have reached ₱3,000,000 "
                f"for the year {current_year}.\n\n"
                "Under BIR rules, businesses that exceed this threshold "
                "are required to register as VAT.\n\n"
                "This system is designed for NON-VAT businesses only.\n\n"
                "You may continue viewing past records, but new entries "
                "may no longer reflect correct tax computations.\n\n"
                "We strongly recommend consulting a licensed accountant "
                "or BIR officer to guide your VAT registration and compliance."
            )

    def show_license_popup(self):
        """Open license import dialog."""

        def on_success():
            self.enable_features()  # enable features after successful import

        popup = LicenseDialog(self.root, on_success=on_success)
        # After popup closes, re-check license
        self.check_existing_license()

    def enable_features(self):
        self.tracking_enabled = True

        # Enable buttons safely
        for btn_name in [
            "add_income_btn", "edit_income_btn", "delete_income_btn", "undo_income_btn",
            "add_expense_btn", "edit_expense_btn", "delete_expense_btn", "undo_expense_btn"
        ]:
            if hasattr(self, btn_name):
                getattr(self, btn_name).configure(state="normal")

        # Enable labels safely
        self.income_label.configure(text_color="#fff")
        self.expense_label.configure(text_color="#fff")

    def open_license_dialog(self):
        print("MENU CLICKED")
        LicenseDialog(self.root, on_success=self.on_license_success)

    #PROFILE
    def open_edit_profile(self):
        def profile_updated():
            messagebox.showinfo("Profile Updated", "Your profile has been updated successfully.")

            # Refresh summary and tables immediately
            self.reports_tab.refresh()  # update reports/summary
            self.load_income_table()  # reload income table if needed
            self.load_expense_table()  # reload expense table if needed

            # Trigger backups
            from core.backup import backup_summary, backup_income, backup_expense
            backup_summary(self.storage, self.app_state, datetime.now().year)
            backup_income(self.storage)
            backup_expense(self.storage)

        wizard = SetupWizard(
            root=self.root,
            parent=self.root,
            app_state=self.app_state,
            on_complete=profile_updated,
            edit_mode=True
        )

        wizard.wait_window()

    def refresh_profile_ui(self):
        # Example: update labels or fields that display profile info
        self.profile_label.config(text=f"Earner Type: {self.app_state.earner_type}")
        self.tax_label.config(text=f"Tax Type: {self.app_state.tax_type}")

    def update_ui_state(self):
        state = "normal" if self.tracking_enabled else "disabled"

        for btn in [
            self.add_income_btn, self.edit_income_btn, self.delete_income_btn, self.undo_income_btn,
            self.add_expense_btn, self.edit_expense_btn, self.delete_expense_btn, self.undo_expense_btn
        ]:
            btn.configure(state=state)

        color = "#FFFFFF" if self.tracking_enabled else "#777777"

        self.income_label.configure(text_color=color)
        self.expense_label.configure(text_color=color)
