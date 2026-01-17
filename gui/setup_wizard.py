import tkinter as tk
from tkinter import ttk, messagebox


class SetupWizard(tk.Toplevel):
    def __init__(self, root, parent, app_state, on_complete, edit_mode=False):
        super().__init__(parent)

        self.root = root
        self.parent = parent
        self.app_state = app_state
        self.on_complete = on_complete
        self.edit_mode = edit_mode

        self.title("Edit Profile" if edit_mode else "Initial Setup")
        self.geometry("480x320")
        self.resizable(False, False)
        self.update_idletasks()
        self.center_window(parent)

        self.lift()
        self.focus_force()
        self.attributes("-topmost", True)

        # Main container
        self.container = ttk.Frame(self)
        self.container.pack(expand=True, fill="both", padx=24, pady=24)

        self.step = 1
        self.show_step()

    def clear(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    # ================== SHARED UI HELPERS ==================
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

        # Center over parent
        x = parent_x + (parent_w // 2) - (w // 2)
        y = parent_y + (parent_h // 2) - (h // 2)

        self.geometry(f"{w}x{h}+{x}+{y}")

    def header(self, title, subtitle=None):
        ttk.Label(
            self.container,
            text=title,
            font=("Segoe UI", 14, "bold")
        ).pack(anchor="w", pady=(0, 6))

        if subtitle:
            ttk.Label(
                self.container,
                text=subtitle,
                wraplength=440,
                foreground="#555555",
                font=("Segoe UI", 10)
            ).pack(anchor="w", pady=(0, 16))

    def option_group(self):
        frame = ttk.Frame(self.container)
        frame.pack(anchor="w", fill="x", pady=(0, 16))
        return frame

    def footer_button(self, text, command):
        ttk.Separator(self.container).pack(fill="x", pady=(12, 12))
        ttk.Button(
            self.container,
            text=text,
            command=command,
            style="Accent.TButton"
        ).pack(anchor="e", pady=(4, 0))

    # ================== STEP CONTROL ==================
    def show_step(self):
        self.clear()
        if self.step == 1:
            self.step_earner_type()
        elif self.step == 2:
            self.step_tax_type()
        elif self.step == 3:
            self.step_deduction_type()
        elif self.step == 4:
            self.finish_setup()

    # ================== STEP 1 ==================
    def step_earner_type(self):
        self.header(
            "Income Earner Type",
            "Select the category that best describes your income source."
        )

        self.earner_var = tk.StringVar(
            value=self.app_state.earner_type if self.edit_mode else ""
        )

        group = self.option_group()

        ttk.Radiobutton(
            group,
            text="Purely Self-Employed / Sole Proprietor",
            variable=self.earner_var,
            value="sole",
            command=self.toggle_mixed_note
        ).pack(anchor="w", pady=4)

        ttk.Radiobutton(
            group,
            text="Mixed-Income Earner",
            variable=self.earner_var,
            value="mixed",
            command=self.toggle_mixed_note
        ).pack(anchor="w", pady=4)

        self.mixed_note = ttk.Label(
            self.container,
            text=(
                "Note for Mixed-Income Earners:\n"
                "This system tracks business income only. "
                "Salary income is taxed separately by the employer."
            ),
            wraplength=440,
            foreground="#555555",
            font=("Segoe UI", 9)
        )
        self.mixed_note.pack_forget()
        self.toggle_mixed_note()

        self.footer_button("Next", self.next_from_earner)

    def toggle_mixed_note(self):
        if self.earner_var.get() == "mixed":
            self.mixed_note.pack(anchor="w", pady=(6, 0))
        else:
            self.mixed_note.pack_forget()

    def next_from_earner(self):
        if not self.earner_var.get():
            messagebox.showerror("Required", "Please select an option.", parent=self)
            return
        self.app_state.earner_type = self.earner_var.get()
        self.step = 2
        self.show_step()

    # ================== STEP 2 ==================
    def step_tax_type(self):
        self.header(
            "Tax Type",
            "Choose how your income tax will be computed."
        )

        self.tax_var = tk.StringVar()

        group = self.option_group()

        ttk.Radiobutton(
            group,
            text="8% Flat Income Tax",
            variable=self.tax_var,
            value="8_percent"
        ).pack(anchor="w", pady=4)

        ttk.Radiobutton(
            group,
            text="Graduated Income Tax",
            variable=self.tax_var,
            value="graduated"
        ).pack(anchor="w", pady=4)

        self.footer_button("Next", self.next_from_tax)

    def next_from_tax(self):
        if not self.tax_var.get():
            messagebox.showerror("Required", "Please select a tax type.", parent=self)
            return
        self.app_state.tax_type = self.tax_var.get()
        self.step = 3 if self.tax_var.get() == "graduated" else 4
        if self.step == 4:
            self.app_state.deduction_type = None
        self.show_step()

    # ================== STEP 3 ==================
    def step_deduction_type(self):
        self.header(
            "Deduction Method",
            "Select how expenses will be deducted from taxable income."
        )

        self.deduction_var = tk.StringVar()

        group = self.option_group()

        ttk.Radiobutton(
            group,
            text="Optional Standard Deduction (OSD)",
            variable=self.deduction_var,
            value="osd"
        ).pack(anchor="w", pady=4)

        ttk.Radiobutton(
            group,
            text="Itemized Deduction",
            variable=self.deduction_var,
            value="itemized"
        ).pack(anchor="w", pady=4)

        self.footer_button("Finish", self.finish_from_deduction)

    def finish_from_deduction(self):
        if not self.deduction_var.get():
            messagebox.showerror("Required", "Please select a deduction type.", parent=self)
            return
        self.app_state.deduction_type = self.deduction_var.get()
        self.step = 4
        self.show_step()

    # ================== STEP 4 ==================
    def finish_setup(self):
        self.app_state.is_configured = True
        self.app_state.save()
        try:
            self.grab_release()
        except tk.TclError:
            pass
        self.destroy()
        if self.on_complete:
            self.on_complete()
