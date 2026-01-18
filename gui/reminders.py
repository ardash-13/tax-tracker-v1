from datetime import date, timedelta
from tkinter import messagebox

# ================== CONFIGURE DEADLINES ==================
# Deadlines are the last day of the filing period
def get_filing_deadlines(year: int):
    return {
        # INCOME TAX
        "Income Tax Q1 (1701Q)": date(year, 5, 15),
        "Income Tax Q2 (1701Q)": date(year, 8, 15),
        "Income Tax Q3 (1701Q)": date(year, 11, 15),
        "Annual Income Tax (1701/1701A)": date(year + 1, 4, 15),

        # PERCENTAGE TAX (NON-VAT)
        "Percentage Tax Q1 (2551Q)": date(year, 4, 25),
        "Percentage Tax Q2 (2551Q)": date(year, 7, 25),
        "Percentage Tax Q3 (2551Q)": date(year, 10, 25),
        "Percentage Tax Q4 (2551Q)": date(year + 1, 1, 25),
    }



# Advance notice in days
ADVANCE_DAYS = 7

def check_filing_reminders():
    today = date.today()
    deadlines = get_filing_deadlines(today.year)

    for filing_name, deadline in deadlines.items():
        days_remaining = (deadline - today).days

        if 0 <= days_remaining <= ADVANCE_DAYS:
            messagebox.showwarning(
                "Tax Filing Reminder",
                f"⚠ TAX FILING REMINDER\n\n"
                f"Filing: {filing_name}\n"
                f"Due Date: {deadline:%B %d, %Y}\n"
                f"Days Remaining: {days_remaining} day(s)\n\n"
                "Please ensure that your records are complete and "
                "file on or before the due date to avoid penalties, "
                "surcharges, and interest.\n\n"
                "If you are unsure, consult your accountant or tax professional."
            )
