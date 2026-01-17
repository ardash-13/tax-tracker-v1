import sys
import sqlite3
import os
from datetime import datetime

# ================== PATH HELPERS ==================
def get_app_root():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LICENSE_DIR = os.path.join(get_app_root(), "data", "license")
os.makedirs(LICENSE_DIR, exist_ok=True)


def get_data_dir():
    path = os.path.join(get_app_root(), "data")
    os.makedirs(path, exist_ok=True)
    return path

DB_FILE = os.path.join(get_data_dir(), "records.db")

# ================== STORAGE MANAGER ==================
class StorageManager:
    def __init__(self):
        self.conn = sqlite3.connect(DB_FILE)
        self.conn.row_factory = sqlite3.Row  # so we can get dict-like rows
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        # Income table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS income (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                gross_income REAL NOT NULL,
                description TEXT,
                cwt REAL DEFAULT 0,
                atc TEXT,
                income_received REAL NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        # Expense table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS expense (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                gross_expense REAL NOT NULL,
                description TEXT,
                wt REAL DEFAULT 0,
                atc TEXT,
                expense_paid REAL NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        self.conn.commit()

    # ================== INCOME ==================
    def add_income(self, data: dict):
        self.cursor.execute("""
            INSERT INTO income (
                date, gross_income, description, cwt, atc, income_received, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            data["date"],
            data["gross_income"],
            data.get("description"),
            data.get("cwt", 0),
            data.get("atc"),
            data["income_received"],
            datetime.now().isoformat()
        ))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_all_income(self):
        rows = self.cursor.execute("SELECT * FROM income ORDER BY date ASC").fetchall()
        return [dict(row) for row in rows]

    def update_income(self, record_id, data: dict):
        self.cursor.execute("""
            UPDATE income
            SET date = ?, gross_income = ?, description = ?, cwt = ?, atc = ?, income_received = ?
            WHERE id = ?
        """, (
            data["date"],
            data["gross_income"],
            data.get("description"),
            data.get("cwt", 0),
            data.get("atc"),
            data["income_received"],
            record_id
        ))
        self.conn.commit()

    def delete_income(self, record_id):
        self.cursor.execute("DELETE FROM income WHERE id = ?", (record_id,))
        self.conn.commit()

    def restore_income(self, data: dict):
        self.cursor.execute("""
            INSERT INTO income (
                id,
                date,
                description,
                gross_income,
                cwt,
                atc,
                income_received,
                created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data["id"],
            data["date"],
            data["description"],
            data["gross_income"],
            data["cwt"],
            data["atc"],
            data["income_received"],
            data["created_at"]
        ))
        self.conn.commit()

    def restore_expense(self, data: dict):
        self.cursor.execute("""
            INSERT INTO expense (
                id,
                date,
                description,
                gross_expense,
                wt,
                expense_paid,
                created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            data["id"],
            data["date"],
            data["description"],
            data["gross_expense"],
            data["wt"],
            data["expense_paid"],
            data["created_at"]
        ))
        self.conn.commit()

    def get_income_summary(self):
        row = self.cursor.execute("""
            SELECT
                IFNULL(SUM(gross_income), 0),
                IFNULL(SUM(cwt), 0),
                IFNULL(SUM(income_received), 0)
            FROM income
        """).fetchone()
        return {"gross_income": row[0], "cwt": row[1], "income_received": row[2]}

    def get_income_by_year(self, year: int):
        rows = self.cursor.execute("""
            SELECT *
            FROM income
            WHERE strftime('%Y', date) = ?
            ORDER BY date DESC
        """, (str(year),)).fetchall()
        return [dict(row) for row in rows]

    # ================== EXPENSE ==================
    def add_expense(self, data: dict):
        self.cursor.execute("""
            INSERT INTO expense (
                date, gross_expense, description, wt, atc, expense_paid, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            data["date"],
            data["gross_expense"],
            data.get("description"),
            data.get("wt", 0),
            data.get("atc"),
            data["expense_paid"],
            datetime.now().isoformat()
        ))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_all_expense(self):
        rows = self.cursor.execute("SELECT * FROM expense ORDER BY date ASC").fetchall()
        return [dict(row) for row in rows]

    def update_expense(self, record_id, data: dict):
        self.cursor.execute("""
            UPDATE expense
            SET date = ?, gross_expense = ?, description = ?, wt = ?, atc = ?, expense_paid = ?
            WHERE id = ?
        """, (
            data["date"],
            data["gross_expense"],
            data.get("description"),
            data.get("wt", 0),
            data.get("atc"),
            data["expense_paid"],
            record_id
        ))
        self.conn.commit()

    def delete_expense(self, record_id):
        self.cursor.execute("DELETE FROM expense WHERE id = ?", (record_id,))
        self.conn.commit()

    def get_expense_summary(self):
        row = self.cursor.execute("""
            SELECT
                IFNULL(SUM(gross_expense), 0),
                IFNULL(SUM(wt), 0),
                IFNULL(SUM(expense_paid), 0)
            FROM expense
        """).fetchone()
        return {"gross_expense": row[0], "wt": row[1], "expense_paid": row[2]}

    # ================== ANNUAL / QUARTER SUMMARY ==================
    def get_quarter_summary(self, year: int, quarter: str):
        quarter_months = {"Q1": (1, 3), "Q2": (4, 6), "Q3": (7, 9), "Q4": (10, 12)}
        start_month, end_month = quarter_months[quarter]

        # Gross income and CWT for this quarter
        income_row = self.cursor.execute("""
            SELECT IFNULL(SUM(gross_income),0), IFNULL(SUM(cwt),0)
            FROM income
            WHERE strftime('%Y', date)=? AND CAST(strftime('%m', date) AS INTEGER) BETWEEN ? AND ?
        """, (str(year), start_month, end_month)).fetchone()

        # Gross expense and WT for this quarter
        expense_row = self.cursor.execute("""
            SELECT IFNULL(SUM(gross_expense),0), IFNULL(SUM(wt),0)
            FROM expense
            WHERE strftime('%Y', date)=? AND CAST(strftime('%m', date) AS INTEGER) BETWEEN ? AND ?
        """, (str(year), start_month, end_month)).fetchone()

        # Since you don't track income tax paid yet, default to 0
        prior_income_tax_paid = 0.0

        # Prior CWT = sum of CWT from months before this quarter
        prior_cwt_paid = self.cursor.execute("""
            SELECT IFNULL(SUM(cwt),0)
            FROM income
            WHERE strftime('%Y', date) = ? AND CAST(strftime('%m', date) AS INTEGER) < ?
        """, (str(year), start_month)).fetchone()[0]

        cwt_current_quarter = income_row[1]

        return {
            "gross_income": income_row[0],
            "cwt": income_row[1],
            "gross_expense": expense_row[0],
            "wt": expense_row[1],
            "prior_income_tax_paid": prior_income_tax_paid,
            "prior_cwt_paid": prior_cwt_paid,
            "cwt_current_quarter": cwt_current_quarter
        }

    def get_annual_summary(self, year: int):
        income_row = self.cursor.execute("""
            SELECT IFNULL(SUM(gross_income),0), IFNULL(SUM(cwt),0)
            FROM income
            WHERE strftime('%Y', date)=?
        """, (str(year),)).fetchone()

        expense_row = self.cursor.execute("""
            SELECT IFNULL(SUM(gross_expense),0), IFNULL(SUM(wt),0)
            FROM expense
            WHERE strftime('%Y', date)=?
        """, (str(year),)).fetchone()

        return {
            "gross_income": income_row[0],
            "cwt": income_row[1],
            "gross_expense": expense_row[0],
            "wt": expense_row[1]
        }

    # FOR VAT-THRESHOLD NOTIF
    def get_year_gross_income(self, year: int) -> float:
        row = self.cursor.execute("""
            SELECT IFNULL(SUM(gross_income), 0)
            FROM income
            WHERE strftime('%Y', date) = ?
        """, (str(year),)).fetchone()

        return float(row[0])
