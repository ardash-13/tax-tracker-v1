import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from core.storage import StorageManager
from datetime import datetime

TAX_EXEMPTION = 250_000


class ReportsTab(ctk.CTkFrame):
    def __init__(self, parent, storage: StorageManager, app_state):
        super().__init__(parent, fg_color="#040f21", corner_radius=0)

        self.storage = storage
        self.app_state = app_state

        # ================= HEADER =================
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=16, pady=(20, 20))

        ctk.CTkLabel(
            header,
            text="Reports & Summary",
            font=("Segoe UI", 26, "bold"),
            text_color="#ffffff"
        ).pack(anchor="w")

        ctk.CTkLabel(
            header,
            text="Income, expenses, and tax overview",
            font=("Segoe UI", 14),
            text_color="#A0AEC0"
        ).pack(anchor="w")

        # ================= VARIABLES =================
        self.report_mode = tk.StringVar(value="Quarter")
        self.selected_year = tk.StringVar(value=str(datetime.now().year))
        self.selected_quarter = tk.StringVar(value=self.get_current_quarter())

        self.report_mode.trace_add("write", self.update_quarter_state)

        # ================= CONTROLS =================
        controls = ctk.CTkFrame(self, fg_color="transparent")
        controls.pack(fill="x", padx=10, pady=(10, 30))

        ctk.CTkLabel(controls, text="View", text_color="#fff").grid(row=0, column=0, padx=8)
        self.view_dropdown = ctk.CTkOptionMenu(
            controls,
            values=["Quarter", "Annual"],
            variable=self.report_mode,
            command=lambda v: self.update_quarter_state(),
            width=120,
            fg_color="#2b3545",
            button_color="#2b3545",
            dropdown_fg_color="#2b3545",
            dropdown_hover_color="#246ae3",
            text_color="#fff"
        )
        self.view_dropdown.grid(row=0, column=1, padx=5)

        ctk.CTkLabel(controls, text="Year", text_color="#fff").grid(row=0, column=2, padx=8)
        self.year_dropdown = ctk.CTkOptionMenu(
            controls,
            values=[],
            variable=self.selected_year,
            command=lambda v: self.refresh(),
            width=90,
            fg_color="#2b3545",
            button_color="#2b3545",
            dropdown_fg_color="#2b3545",
            dropdown_hover_color="#246ae3",
            text_color="#fff"
        )
        self.year_dropdown.grid(row=0, column=3, padx=5)

        self.quarter_label = ctk.CTkLabel(controls, text="Quarter", text_color="#fff")
        self.quarter_label.grid(row=0, column=4, padx=8)

        self.quarter_dropdown = ctk.CTkOptionMenu(
            controls,
            values=["Q1", "Q2", "Q3", "Q4"],
            variable=self.selected_quarter,
            command=lambda v: self.refresh(),
            width=90,
            fg_color="#2b3545",
            button_color="#2b3545",
            dropdown_fg_color="#2b3545",
            dropdown_hover_color="#246ae3",
            text_color="#fff"
        )
        self.quarter_dropdown.grid(row=0, column=5, padx=5)

        self.load_report_years()

        # ================= SUMMARY CARDS =================
        self.cards = ctk.CTkFrame(self, fg_color="transparent")
        self.cards.pack(fill="x", padx=10, pady=(0, 20))

        self.card_values = {}

        def create_card(title):
            card = ctk.CTkFrame(self.cards, fg_color="#111827", corner_radius=12)
            card.pack(side="left", expand=True, fill="both", padx=8)

            ctk.CTkLabel(
                card, text=title, text_color="#9CA3AF", font=("Segoe UI", 12)
            ).pack(anchor="w", padx=15, pady=(12, 0))

            value = ctk.CTkLabel(
                card, text="₱ 0.00", text_color="#fff", font=("Segoe UI", 22, "bold")
            )
            value.pack(anchor="w", padx=15, pady=(4, 12))

            self.card_values[title] = value

        create_card("Total Income")
        create_card("Total Expenses")
        create_card("Net Taxable Income")
        create_card("Estimated Tax Due")

        # ================= TABLE =================
        # Outer frame with border color
        table_card = ctk.CTkFrame(
            self,
            fg_color="#2E3458",  # Background color of the frame
            corner_radius=5,
            border_width=5,  # Thickness of the border
            border_color="#246ae3"  # Border color
        )
        table_card.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Treeview inside with padding so the border shows
        columns = ("field", "value")
        self.tree = ttk.Treeview(
            table_card,
            columns=columns,
            show="headings"
        )

        self.tree.heading("field", text="Field")
        self.tree.heading("value", text="Value")

        self.tree.column("field", anchor="w", width=340)
        self.tree.column("value", anchor="e", width=220)

        # Pack with padding so the border is visible
        self.tree.pack(fill="both", expand=True, padx=4, pady=4)

        self.update_quarter_state()
        self.refresh()

    # ================= YEARS =================
    def load_report_years(self):
        rows = self.storage.cursor.execute("""
            SELECT DISTINCT strftime('%Y', date) as year
            FROM (
                SELECT date FROM income
                UNION ALL
                SELECT date FROM expense
            )
            ORDER BY year DESC
        """).fetchall()

        years = [r["year"] for r in rows]
        current_year = str(datetime.now().year)

        if current_year not in years:
            years.insert(0, current_year)

        self.year_dropdown.configure(values=years)
        self.selected_year.set(current_year)

    # ================= QUARTER =================
    def get_current_quarter(self):
        m = datetime.now().month
        return "Q1" if m <= 3 else "Q2" if m <= 6 else "Q3" if m <= 9 else "Q4"

    def update_quarter_state(self, *args):
        if self.report_mode.get() == "Annual":
            self.quarter_dropdown.configure(state="disabled")
            # self.quarter_label.grid_remove()
        else:
            self.quarter_dropdown.configure(state="normal")
            # self.quarter_label.grid()
        self.refresh()

    # ================= GRADUATED TAX =================
    def calculate_graduated_tax(self, taxable_income):
        if taxable_income <= 250_000:
            return 0.0
        elif taxable_income <= 400_000:
            return (taxable_income - 250_000) * 0.20
        elif taxable_income <= 800_000:
            return 30_000 + (taxable_income - 400_000) * 0.25
        elif taxable_income <= 2_000_000:
            return 130_000 + (taxable_income - 800_000) * 0.30
        elif taxable_income <= 8_000_000:
            return 490_000 + (taxable_income - 2_000_000) * 0.32
        else:
            return 2_410_000 + (taxable_income - 8_000_000) * 0.35

    # ================= REFRESH =================
    def refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        earner_type = self.app_state.earner_type
        tax_type = self.app_state.tax_type
        deduction_type = self.app_state.deduction_type

        year = int(self.selected_year.get())
        mode = self.report_mode.get()
        quarter = self.selected_quarter.get()

        # ---------------- CUMULATIVE SUMMARY ----------------
        summary_annual = self.storage.get_annual_summary(year)
        gross_income_cumulative = summary_annual["gross_income"]
        income_cwt_cumulative = summary_annual["cwt"]
        gross_expense_cumulative = summary_annual["gross_expense"]
        expense_wt_cumulative = summary_annual["wt"]

        # ---------------- QUARTERLY INFO ----------------
        if mode == "Quarter":
            summary_quarter = self.storage.get_quarter_summary(year, quarter)
            prior_income_tax_paid = summary_quarter["prior_income_tax_paid"]
            prior_cwt_paid = summary_quarter["prior_cwt_paid"]
            cwt_current_qtr = summary_quarter["cwt_current_quarter"]
        else:
            prior_income_tax_paid = 0.0
            prior_cwt_paid = 0.0
            cwt_current_qtr = 0.0

        # ---------------- CALCULATE NET TAXABLE & TAX ----------------
        if tax_type == "8_percent":
            taxable = gross_income_cumulative if earner_type == "mixed" else max(0,
                                                                                 gross_income_cumulative - TAX_EXEMPTION)
            income_tax_due_ytd = taxable * 0.08
        else:
            deductible = gross_income_cumulative * 0.40 if deduction_type == "osd" else gross_expense_cumulative
            taxable = max(0, gross_income_cumulative - deductible)
            income_tax_due_ytd = self.calculate_graduated_tax(taxable)

        # Income Tax Payable (This Quarter)
        # Subtract prior income tax paid, prior CWT, and this quarter's CWT if in quarter mode
        if mode == "Quarter":
            income_tax_payable = max(0, income_tax_due_ytd - prior_income_tax_paid - prior_cwt_paid - cwt_current_qtr)
        else:
            income_tax_payable = max(0, income_tax_due_ytd - income_cwt_cumulative)

        # ---------------- UPDATE CARDS BASED ON DROPDOWN ----------------
        if mode == "Quarter":
            income_current = summary_quarter["gross_income"]
            expense_current = summary_quarter["gross_expense"]
            deductible_current = income_current * 0.40 if deduction_type == "osd" else expense_current
            taxable_current = max(0, income_current - deductible_current) if tax_type != "8_percent" else (
                income_current if earner_type == "mixed" else max(0, income_current - TAX_EXEMPTION)
            )
            tax_due_current = taxable_current * 0.08 if tax_type == "8_percent" else self.calculate_graduated_tax(
                taxable_current)
        else:  # Annual
            income_current = gross_income_cumulative
            expense_current = gross_expense_cumulative
            deductible_current = gross_income_cumulative * 0.40 if deduction_type == "osd" else gross_expense_cumulative
            taxable_current = max(0, gross_income_cumulative - deductible_current) if tax_type != "8_percent" else (
                gross_income_cumulative if earner_type == "mixed" else max(0, gross_income_cumulative - TAX_EXEMPTION)
            )
            tax_due_current = taxable_current * 0.08 if tax_type == "8_percent" else self.calculate_graduated_tax(
                taxable_current)

        self.card_values["Total Income"].configure(text=f"₱{income_current:,.2f}")
        self.card_values["Total Expenses"].configure(text=f"₱{expense_current:,.2f}")
        self.card_values["Net Taxable Income"].configure(text=f"₱{taxable_current:,.2f}")
        self.card_values["Estimated Tax Due"].configure(text=f"₱{tax_due_current:,.2f}")

        # ---------------- POPULATE TREE ----------------
        rows = []
        rows.append(("── INCOME TAX (1701Q / 1701) ──", ""))
        rows.append(("Income Earner Type", "Mixed Income Earner" if earner_type == "mixed" else "Sole Proprietor"))

        if tax_type == "8_percent":
            rows += [
                ("Tax Type", "8% Flat Income Tax"),
                ("Gross Income (YTD)", f"₱{gross_income_cumulative:,.2f}"),
                ("Net Taxable Income", f"₱{taxable:,.2f}"),
                ("Income Tax Due (YTD)", f"₱{income_tax_due_ytd:,.2f}"),
                ("Less: Creditable Withholding Tax (CWT)", f"₱{prior_cwt_paid + cwt_current_qtr:,.2f}"),
                ("Income Tax Payable", f"₱{income_tax_payable:,.2f}")
            ]
        else:
            rows += [
                ("Tax Type", "Graduated Income Tax"),
                ("Deduction Method", "OSD (40%)" if deduction_type == "osd" else "Itemized Deduction"),
                ("Gross Income (YTD)", f"₱{gross_income_cumulative:,.2f}"),
                ("Total Deductions", f"₱{deductible:,.2f}"),
                ("Net Taxable Income", f"₱{taxable:,.2f}"),
                ("Income Tax Due (YTD)", f"₱{income_tax_due_ytd:,.2f}"),
                ("Less: Creditable Withholding Tax (CWT)", f"₱{prior_cwt_paid + cwt_current_qtr:,.2f}"),
                ("Income Tax Payable", f"₱{income_tax_payable:,.2f}")
            ]

        # ---------------- PERCENTAGE TAX ----------------
        if tax_type != "8_percent":
            if mode == "Quarter":
                gross_current_qtr = summary_quarter["gross_income"]
                percentage_tax = gross_current_qtr * 0.03
            else:
                gross_current_qtr = gross_income_cumulative
                percentage_tax = gross_current_qtr * 0.03

            rows.append(("", ""))
            rows.append(("── PERCENTAGE TAX (2551Q) ──", ""))
            rows += [
                ("Gross Income (This Quarter)", f"₱{gross_current_qtr:,.2f}"),
                ("Percentage Tax Due (3%)", f"₱{percentage_tax:,.2f}")
            ]

        # ---------------- WITHHOLDING TAXES ----------------
        rows.append(("", ""))
        rows.append(("── WITHHOLDING TAXES ──", ""))
        rows += [
            ("Withholding Tax on Expenses (1601EQ / 1601FQ)", f"₱{expense_wt_cumulative:,.2f}")
        ]

        for field, value in rows:
            self.tree.insert("", "end", values=(field, value))
