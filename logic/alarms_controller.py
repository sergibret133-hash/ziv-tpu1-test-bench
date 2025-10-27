import threading
import time
import robot
import os
import sys
import subprocess
import json
import logic.robot_executor as robot_executor

from logic.robot_executor import TEST_DIRECTORY

class AlarmsController:
    def __init__(self, app_ref):
        self.app_ref = app_ref
        self.monitoring_thread = None
        self.stop_event = threading.Event()
        
        self.alarms_browser_process = None
        self.alarms_session_file = None
        self.monitoring_context = None  # Guarda 'A' o 'B' para saber qué se está monitorizando

    def _start_alarms_browser(self, ip, session_file_path, session_alias):
        """Inicia un proceso de navegador separado para las alarmas."""
        if os.path.exists(self.alarms_session_file):
            os.remove(self.alarms_session_file)
            
            # Utilizamos start_browser.robot para iniciar una nueva sesión de navegador y guardar la info en alarms_session.json

        command = [
            sys.executable, '-m', 'robot',
            '--outputdir', 'test_results', '--log', 'None', '--report', 'None',
            '--variable', f'IP_ADDRESS:{ip}',
            # Usamos la ruta y alias dinámicos que nos pasan
            '--variable', f'SESSION_FILE_PATH:{session_file_path}', 
            '--variable', f'SESSION_ALIAS:{session_alias}', # Necesario para BrowserManager
            'tests/start_browser.robot'
        ]
        
        self.alarms_browser_process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)   # Ocultamos stdout/stderr para no ensuciar la consola
        
        # Esperamos a que el archivo de sesión sea creado (max 30s)
        timeout = 30
        start_time = time.time()
        while time.time() - start_time < timeout:
            if os.path.exists(self.alarms_session_file):
                return True
            time.sleep(0.5)
        return False

# Para iniciar y detener la monitorización de alarmas nos conectamos a una sesión de navegador existente (creado con start_browser.robot)

    def start_monitoring(self):
        """Inicia el bucle de monitorización de alarmas en un hilo."""
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.app_ref._update_status(f"Monitorización ya activa para {self.monitoring_context}.", "orange")
            return
        
        # Averiguar el contexto activo (A o B)
        active_session_id = self.app_ref.active_session_id
        session_info = self.app_ref.sessions.get(active_session_id)

        # Comprobamow si tenemos IP para ese contexto
        if not session_info or not session_info['ip']:
            error_msg = f"Error: No se puede monitorizar. Sesión {active_session_id} no está conectada o no tiene IP."
            self.app_ref.gui_queue.put(('main_status', error_msg, "red"))
            return
            
        ip = session_info['ip']
        
        # Guardamos el contexto que vamos a monitorizar
        self.monitoring_context = active_session_id     #'A' o 'B'  #Lo guardamos como varible global una vez hemos comprobado que hay sesion abierta y que la ip existe tambien
        # Utilizamos variables globales para definir nombre de archivo sesion alarmas y su alias.
        self.alarms_session_file = os.path.abspath(f"alarms_session_{active_session_id}.json")
        session_alias = f"Alarms_{active_session_id}" # Alias único para el navegador
        
        # Iniciamos el hilo
        self.stop_event.clear()
        self.monitoring_thread = threading.Thread(target=self._full_monitoring_cycle, args=(ip, self.alarms_session_file, session_alias, self.monitoring_context), daemon=True)
        self.monitoring_thread.start()
        # self.app_ref._update_status("Monitorización de alarmas iniciada.", "green")

    def stop_monitoring(self):
        """Detiene el bucle de monitorización."""
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.app_ref._update_status("Enviando señal de detención...", "orange")
            self.stop_event.set()
    
            
    def _full_monitoring_cycle(self, ip, session_file_path, session_alias, session_id_context):
        """Gestiona el ciclo de vida completo: abre navegador, monitoriza, cierra navegador."""
        
        try:
            self.app_ref.gui_queue.put('main_status', f"Iniciando navegador de alarmas para {session_id_context}...", "orange")
            
            
            # Pasamos todos los datos que son necesarios
            if not self._start_alarms_browser(ip, session_file_path, session_alias): # Aqui lanzamos start_browser.robot para iniciar una nueva sesión de navegador para las alarmas con los datos pasados
                raise RuntimeError(f"No se pudo iniciar el navegador para las alarmas de {session_id_context}.")

            self.app_ref.gui_queue.put(('main_status', f"Monitorización de alarmas ({session_id_context}) iniciada.", "green"))
            
            self._monitoring_loop(ip, session_file_path, session_id_context) # Una vez abierta la sesion de navegador, ejecutamos el bucle de monitorización, QUE SE ENCARGARÁ de acceder a la sesión existente y recoger las alarmas

        except Exception as e:
            error_msg = f"Error crítico en ciclo de alarmas ({session_id_context}): {e}"
            self.app_ref.gui_queue.put(('main_status', error_msg, "red"))
            
        finally: # Al finalizar (ya sea por error o por detención), cerramos el navegador de alarmas, pasandole el archivo de sesión del navegador de alarmas
            self.app_ref.gui_queue.put(('main_status', f"Cerrando navegador de alarmas ({session_id_context})...", "orange"))
            # Limpieza
            if self.alarms_browser_process:
                # robot.run(
                #     os.path.join(TEST_DIRECTORY, 'close_all_browsers.robot'),
                #     variable=[f'SESSION_FILE:{self.alarms_session_file}'],
                #     output=None, log=None, report=None,
                #     stdout=None, stderr=None
                # )
                self.alarms_browser_process.terminate()
                self.alarms_browser_process = None


            if os.path.exists(self.alarms_session_file):
                os.remove(self.alarms_session_file)
            
            self.app_ref.gui_queue.put(('main_status', f"Monitorización de alarmas ({session_id_context}) detenida.", "white"))

            self.monitoring_context = None


    
    def _monitoring_loop(self, ip, session_file_path, session_id_context):
        """Bucle que ejecuta el test de alarmas en un subproceso."""
        
        # Encontramos la ruta al archivo .robot que contiene el test
        robot_script_path = robot_executor._find_test_file(
            self.app_ref, 
            'Scrape And Return Alarms', 
            preferred_filename='Get_Alarms.robot'
        )
        if not robot_script_path:
            error_msg = "Error: No se encontró el script de robot para obtener alarmas."
            self.app_ref.gui_queue.put(('main_status', error_msg, "red"))
            return

        while not self.stop_event.is_set():
            try:
                if self.app_ref.is_main_task_running:
                    time.sleep(1) # Esperamos un segundo antes de volver a comprobar
                    continue      # Saltamos esta iteración del bucle
            
                
                # Comando para ejecutar Robot desde la línea de comandos
                command = [
                    sys.executable, '-m', 'robot',
                    '--outputdir', 'test_results',
                    '--output', 'None', 
                    '--log', 'None',
                    '--report', 'None',
                    '--variable', f'IP_ADDRESS:{ip}',
                    '--variable', f'SESSION_FILE:{session_file_path}', # Usamos la sesión fantasma
                    '--test', 'Scrape And Return Alarms',
                    robot_script_path
                ]
                # Ejecutamos el comando como un subproceso, capturando su salida
                result = subprocess.run(
                    command, 
                    capture_output=True, 
                    text=True, 
                    encoding='utf-8',
                    check=False # Evita que lance una excepción si el test falla
                )

                # Si el test fue exitoso, procesamos la salida de la consola
                if result.returncode == 0 and result.stdout:
                    for line in result.stdout.splitlines():
                        if line.startswith("GUI_ALARMS::"):
                            json_part = line.split("::", 1)[1]
                            try:
                                alarms_data = json.loads(json_part)
                                # Enviamos los datos a la GUI
                                self.app_ref.gui_queue.put(('update_alarms_display', session_id_context, alarms_data))
                            except json.JSONDecodeError as e:
                                print(f"Error al decodificar JSON de alarmas: {e}")
                            break # Ya encontramos la línea, salimos del bucle
                
                # Si hubo un error en el subproceso, lo mostramos
                elif result.returncode != 0:
                    print(f"Error en subproceso de alarmas ({session_id_context}): {result.stderr}")

            except Exception as e:
                error_msg = f"Error en el bucle de monitorización ({session_id_context}): {e}"
                self.app_ref.gui_queue.put(('main_status', error_msg, "red"))
                break 

            # Espera antes de la siguiente comprobación
            for _ in range(6):
                if self.stop_event.is_set():
                    break
                time.sleep(1)