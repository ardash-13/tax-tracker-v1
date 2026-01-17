import json
import os
from core.paths import DATA_DIR

STATE_FILE = os.path.join(DATA_DIR, "app_state.json")


class AppState:
    def __init__(self):
        self.earner_type = None
        self.tax_type = None
        self.deduction_type = None
        self.is_configured = False

    def load(self):
        if not os.path.exists(STATE_FILE):
            return

        with open(STATE_FILE, "r") as f:
            data = json.load(f)

        self.earner_type = data.get("earner_type")
        self.tax_type = data.get("tax_type")
        self.deduction_type = data.get("deduction_type")
        self.is_configured = data.get("is_configured", False)

    def save(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(STATE_FILE, "w") as f:
            json.dump({
                "earner_type": self.earner_type,
                "tax_type": self.tax_type,
                "deduction_type": self.deduction_type,
                "is_configured": self.is_configured
            }, f, indent=4)

    def update_profile(self, earner_type, tax_type, deduction_type=None):
        self.earner_type = earner_type
        self.tax_type = tax_type
        self.deduction_type = deduction_type
        self.is_configured = True
        self.save()
