import sys
import os 
from gui.app import ModernTestRunnerApp

if __name__ == "__main__":

    # *** Preparamos el entorno ***
    if not os.path.exists("test_results"):
        os.makedirs("test_results")
    if not os.path.exists("scheduler_profiles"):
        os.makedirs("scheduler_profiles")
    if not os.path.exists("trap_history"):
        os.makedirs("trap_history")

    app = ModernTestRunnerApp()
    app.mainloop()