import threading
import time
import robot



class SessionController:
    def __init__(self, app_ref):
        self.app_ref = app_ref
        self.keep_alive_thread = None
        self.stop_event = threading.Event() # Manejaremos el thread mediante el estado de stop_event 

    def start_keep_alive(self):
        """Inicia el bucle 'keep-alive' en un hilo secundario."""
        if self.keep_alive_thread and self.keep_alive_thread.is_alive():
            return # Ya está en ejecución
        # Si se tiene que iniciar..
        self.stop_event.clear() # Borramos cualquier data restante del estado del hilo (que se haya podido ejecutar con anterioridad)
        self.keep_alive_thread = threading.Thread(target=self._keep_alive_loop, daemon=True)
        self.keep_alive_thread.start()
        print("INFO: Guardián de sesión iniciado.")
        
    
    def stop_keep_alive(self):
        """Detiene el bucle 'keep-alive'."""
        if self.keep_alive_thread and self.keep_alive_thread.is_alive():
            self.stop_event.set()
            print("INFO: Guardián de sesión detenido.")
            
    def _keep_alive_loop(self):
            """
            Bucle que se ejecuta en segundo plano. Cada 15 segundos, comprueba si
            la sesión ha expirado y la renueva si es necesario.
            """
            while not self.stop_event.is_set():
                time.sleep(55) # Espera 15 segundos

                # ¡Solo actúa si hay sesión y NINGÚN OTRO TEST está corriendo!
                if self.app_ref.browser_process and not self.app_ref.is_task_running:
                    try:
                        robot.run(
                            'tests/Keep_Alive.robot',
                            output=None, log=None, report=None,
                            stdout=None, stderr=None
                        )
                    except Exception as e:
                        print(f"ERROR en el guardián de sesión: {e}")