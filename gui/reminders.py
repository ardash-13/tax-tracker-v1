from datetime import date, timedelta
from tkinter import messagebox

# ================== CONFIGURE DEADLINES ==================
# Deadlines are the last day of the filing period
def get_filing_deadlines(year: int):
    return {
        "Q1": date(year, 5, 15),
        "Q2": date(year, 8, 15),
        "Q3": date(year, 11, 15),
        "Annual": date(year + 1, 4, 15),
    }


# Advance notice in days
ADVANCE_DAYS = 7

def check_filing_reminders():
    today = date.today()
    deadlines = get_filing_deadlines(today.year)

    for period, deadline in deadlines.items():
        days_remaining = (deadline - today).days

        if 0 <= days_remaining <= ADVANCE_DAYS:
            messagebox.showwarning(
                f"{period} Filing Reminder",
                f"⚠ Reminder: {period} filing is due on {deadline:%B %d, %Y}.\n"
                f"You have {days_remaining} day(s) left to file.\n\n"
                "Please prepare your documents and consult your accountant if needed."
            )
