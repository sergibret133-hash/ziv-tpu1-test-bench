import sys
import os  # <-- Asegúrate de importar 'os'
from gui.app import ModernTestRunnerApp

# 1. Si este es el archivo que se está ejecutando...
if __name__ == "__main__":

    # 2. Preparamos el entorno (creamos carpetas si no existen)
    if not os.path.exists("test_results"):
        os.makedirs("test_results")
    if not os.path.exists("scheduler_profiles"):
        os.makedirs("scheduler_profiles")
    if not os.path.exists("trap_history"):
        os.makedirs("trap_history")

    # 3. Creamos una instancia de la aplicación y la arrancamos
    app = ModernTestRunnerApp()
    app.mainloop()