from datetime import date
from tkinter import messagebox


def notify_license_status(expiry_date):
    """
    Shows license reminders.
    Blocking logic is NOT handled here.
    expiry_date must be datetime.date
    """

    today = date.today()
    days_remaining = (expiry_date - today).days

    # 🔔 3 DAYS BEFORE EXPIRY
    if days_remaining == 3:
        messagebox.showwarning(
            "License Expiring Soon",
            f"Your license will expire in 3 days ({expiry_date}).\n\n"
            "Please renew your license to avoid interruption.\n\n"
            "You can request a new license to avoid interruption."
        )

    # ⛔ EXPIRED (TODAY OR PAST)
    elif days_remaining <= 0:
        messagebox.showerror(
            "License Expired",
            f"Your license expired on {expiry_date}.\n\n"
            "You must import a new license file to continue using the application.\n\n"
            "Contact support to request a new license."
        )
