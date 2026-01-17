import csv
import os
from datetime import datetime
from core.paths import BACKUP_DIR


def ensure_backup_dir():
    os.makedirs(BACKUP_DIR, exist_ok=True)


def backup_income(storage):
    ensure_backup_dir()

    incomes = storage.get_all_income()
    grouped = {}

    for inc in incomes:
        year = inc["date"][:4]
        grouped.setdefault(year, []).append(inc)

    # Make sure all years in backups are updated
    existing_files = [f for f in os.listdir(BACKUP_DIR) if f.endswith("_income.csv")]
    years_in_files = [f.split("_")[0] for f in existing_files]

    all_years = set(list(grouped.keys()) + years_in_files)

    for year in all_years:
        rows = grouped.get(year, [])  # will be empty if no records
        path = os.path.join(BACKUP_DIR, f"{year}_income.csv")

        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "ID", "Date", "Gross Income", "Description",
                "CWT", "ATC", "Income Received"
            ])
            for r in rows:
                writer.writerow([
                    r["id"],
                    r["date"],
                    r["gross_income"],
                    r.get("description", ""),
                    r["cwt"],
                    r.get("atc", ""),
                    r["income_received"]
                ])


def backup_expense(storage):
    ensure_backup_dir()

    expenses = storage.get_all_expense()
    grouped = {}

    for exp in expenses:
        year = exp["date"][:4]
        grouped.setdefault(year, []).append(exp)

    # Make sure all years in backups are updated
    existing_files = [f for f in os.listdir(BACKUP_DIR) if f.endswith("_expense.csv")]
    years_in_files = [f.split("_")[0] for f in existing_files]

    all_years = set(list(grouped.keys()) + years_in_files)

    for year in all_years:
        rows = grouped.get(year, [])  # empty if no records for that year
        path = os.path.join(BACKUP_DIR, f"{year}_expense.csv")

        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "ID", "Date", "Gross Expense", "Description",
                "WT", "ATC", "Expense Paid"
            ])
            for r in rows:
                writer.writerow([
                    r["id"],
                    r["date"],
                    r["gross_expense"],
                    r.get("description", ""),
                    r["wt"],
                    r.get("atc", ""),
                    r["expense_paid"]
                ])


TAX_EXEMPTION = 250_000


def backup_summary(storage, app_state, year: int):
    ensure_backup_dir()

    summary = storage.get_annual_summary(year)

    gross_income = summary["gross_income"]
    income_cwt = summary["cwt"]
    gross_expense = summary["gross_expense"]
    expense_wt = summary["wt"]

    tax_type = app_state.tax_type
    deduction_type = app_state.deduction_type

    # ================= TAX COMPUTATION =================
    earner_type = app_state.earner_type

    if tax_type == "8_percent":
        if earner_type == "mixed":
            taxable_income = gross_income
        else:
            taxable_income = max(0, gross_income - TAX_EXEMPTION)

        income_tax_due = taxable_income * 0.08
        percentage_tax = "N/A"
    else:
        if deduction_type == "osd":
            deductible = gross_income * 0.40
        else:
            deductible = gross_expense

        taxable_income = max(0, gross_income - deductible)

        # Graduated tax table
        if taxable_income <= 250_000:
            income_tax_due = 0
        elif taxable_income <= 400_000:
            income_tax_due = (taxable_income - 250_000) * 0.15
        elif taxable_income <= 800_000:
            income_tax_due = 22_500 + (taxable_income - 400_000) * 0.20
        elif taxable_income <= 2_000_000:
            income_tax_due = 102_500 + (taxable_income - 800_000) * 0.25
        elif taxable_income <= 8_000_000:
            income_tax_due = 402_500 + (taxable_income - 2_000_000) * 0.30
        else:
            income_tax_due = 2_202_500 + (taxable_income - 8_000_000) * 0.35

        percentage_tax = gross_income * 0.03

    filepath = os.path.join(BACKUP_DIR, f"{year}_summary.csv")

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Field", "Value"])
        writer.writerow(["Year", year])
        writer.writerow(["Tax Type", tax_type])
        writer.writerow(["Deduction Type", deduction_type or "N/A"])
        writer.writerow(["Gross Income", f"{gross_income:.2f}"])
        writer.writerow(["Total Expense", f"{gross_expense:.2f}"])
        writer.writerow(["Net Taxable Income", f"{taxable_income:.2f}"])
        writer.writerow(["Income Tax Due", f"{income_tax_due:.2f}"])
        writer.writerow([
            "Percentage Tax",
            percentage_tax if percentage_tax == "N/A" else f"{percentage_tax:.2f}"
        ])
        writer.writerow(["Income CWT", f"{income_cwt:.2f}"])
        writer.writerow(["Expense WT", f"{expense_wt:.2f}"])
