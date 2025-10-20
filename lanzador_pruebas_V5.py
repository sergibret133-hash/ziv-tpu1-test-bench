import os
from gui.app import ModernTestRunnerApp



# v5_CAMBIOS:
# -> Refactorizacion de todo el proyecto en modulos y paquetes
# -> Solucionado aparición de ventanas fantasma en el momento de ejecutar tests con Selenium. 
# -> Solucionado error al cerrar sesión principal del navegador (ahora se cierra correctamente la ventana del navegador)
# -> Soluciondo bug que no permitía visualizar correctamente los argumentos sugeridos en la pestaña Scheduler cuando eran muy largos
# - Añadir sección de alarmas. Monitorización .
# -> Monitorización de alarmas en segundo plano con Robot Framework y actualización de la GUI con la info obtenida
#       -> Gestión avanzada de sesiones de navegador para la monitorización de alarmas.
# -> Comprobación de los popups de sesion expirada al inicio de cada testcase. Relleno automático del requerimiento de contraseña.

if __name__ == "__main__":
    # Asegurarse de que las carpetas de resultados existen
    if not os.path.exists("test_results"):
        os.makedirs("test_results")
    if not os.path.exists("scheduler_profiles"):
        os.makedirs("scheduler_profiles")
    if not os.path.exists("trap_history"):
        os.makedirs("trap_history")

    # Crear y ejecutar la aplicación
    app = ModernTestRunnerApp()
    app.mainloop()