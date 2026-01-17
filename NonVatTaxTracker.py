import tkinter as tk
from core.app_state import AppState
from gui.setup_wizard import SetupWizard
from gui.main_window import MainWindow


def main():
    root = tk.Tk()
    root.withdraw()

    app_state = AppState()
    app_state.load()

    def launch_main():
        root.deiconify()
        MainWindow(root, app_state)

    if not app_state.is_configured:
        SetupWizard(
            root=root,
            parent=root,
            app_state=app_state,
            on_complete=launch_main
        )
    else:
        launch_main()

    root.mainloop()


if __name__ == "__main__":
    main()
