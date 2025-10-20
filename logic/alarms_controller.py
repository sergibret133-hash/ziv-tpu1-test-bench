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
        self.alarms_session_file = "alarms_session.json"
        

    def _start_alarms_browser(self):
        """Inicia un proceso de navegador separado para las alarmas."""
        if os.path.exists(self.alarms_session_file):
            os.remove(self.alarms_session_file)
            # Utilizamos start_browser.robot para iniciar una nueva sesión de navegador y guardar la info en alarms_session.json
        ip = self.app_ref.entry_ip.get()
        command = [
            sys.executable, '-m', 'robot',
            '--outputdir', 'test_results', '--log', 'None', '--report', 'None',
            '--variable', f'IP_ADDRESS:{ip}',
            '--variable', f'SESSION_FILE_PATH:{os.path.abspath(self.alarms_session_file)}', # Le pasamos a start_browser.robot la ruta absoluta del archivo de sesión nuevo con el que guardaremos una nueva sesión de navegador parar las alarmas
            'tests/start_browser.robot'
        ]
        self.alarms_browser_process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        # Esperamos a que el archivo de sesión sea creado (máx 30s)
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
            self.app_ref._update_status("La monitorización de alarmas ya está activa.", "orange")
            return

        self.stop_event.clear()
        self.monitoring_thread = threading.Thread(target=self._full_monitoring_cycle, daemon=True)
        self.monitoring_thread.start()
        # self.app_ref._update_status("Monitorización de alarmas iniciada.", "green")

    def stop_monitoring(self):
        """Detiene el bucle de monitorización."""
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.app_ref._update_status("Enviando señal de detención...", "orange")
            self.stop_event.set()
            # self.app_ref._update_status("Monitorización de alarmas detenida.", "orange")
            
            

    def _full_monitoring_cycle(self):
        """Gestiona el ciclo de vida completo: abre navegador, monitoriza, cierra navegador."""
        try:
            self.app_ref.gui_queue.put(('main_status', "Iniciando navegador de alarmas...", "orange"))
            if not self._start_alarms_browser(): # Aqui lanzamos start_browser.robot para iniciar una nueva sesión de navegador para las alarmas
                raise RuntimeError("No se pudo iniciar el navegador para las alarmas.") # Si falla, lanzamos excepción

            self.app_ref.gui_queue.put(('main_status', "Monitorización de alarmas iniciada.", "green"))
            self._monitoring_loop() # Una vez abierta la sesion de navegador, ejecutamos el bucle de monitorización, QUE SE ENCARGARÁ de acceder a la sesión existente y recoger las alarmas

        except Exception as e:
            error_msg = f"Error crítico en ciclo de alarmas: {e}"
            self.app_ref.gui_queue.put(('main_status', error_msg, "red"))
        finally: # Al finalizar (ya sea por error o por detención), cerramos el navegador de alarmas, pasandole el archivo de sesión del navegador de alarmas
            self.app_ref.gui_queue.put(('main_status', "Cerrando navegador de alarmas...", "orange"))
            if self.alarms_browser_process:
                robot.run(
                    os.path.join(TEST_DIRECTORY, 'close_all_browsers.robot'),
                    variable=[f'SESSION_FILE:{self.alarms_session_file}'],
                    output=None, log=None, report=None,
                    stdout=None, stderr=None
                )
                self.alarms_browser_process.terminate()
                self.alarms_browser_process = None


            if os.path.exists(self.alarms_session_file):
                os.remove(self.alarms_session_file)
            
            self.app_ref.gui_queue.put(('main_status', "Monitorización de alarmas detenida.", "white"))



    # def _monitoring_loop(self):
    #     """Bucle que se ejecuta en segundo plano para obtener las alarmas."""
        
    #     test_name = 'Scrape And Return Alarms'

    #     # 1. Preguntamos a app.py, qué necesitamos recoger del test que queremos ejecutar.
    #     gui_update_info = self.app_ref.test_gui_update_map.get(test_name)   # Nos devolvera el tipo de mensaje (update_alarms_display) y los atributos (alarms_data)
        
    #     message_type, attr_names = gui_update_info  # Guardamos esos campos que tendremos que rellenar una vez el test se ejecute
        
    #     # 2. La siguiente linea de codigo nos devuelve UNA FUNCIÓN callback, QUE AUN NO SE HA EJECUTADO. Se ejecutará y enviara los datos a traves de la cola-buzon al final.
    #     # PERO ANTES DE SER EJECUTADA Y ENVIAR LOS DATOS A LA GUI, NECESITAREMOS RELLENAR LOS DATOS.
    #     # PARA ELLO, PASAREMOS TODA LA FUNCION (SIN EJECUTARSE) A _run_robot_test. Alli, se obtendran los datos del listener Y SE COLOCARAN DENTRO DE LA FUNCION. 
    #     # Será la misma funcion _run_robot_test que rellena los campos, quien al final, si todo va bien, EJECUTARA LA FUNCION CALLBACK 
        
        
    #     success_callback = self.app_ref._create_gui_update_callback(message_type, attr_names)
    #     # Tiene esta pinta:
    #         #     def callback(listener):
    #         # # Recopila los valores de los atributos del listener
    #         # params = [getattr(listener, attr, None) for attr in attr_names]
    #         # # Envía el mensaje completo a la cola de la GUI
    #         # self.gui_queue.put(tuple([message_type] + params))
        
    #     while not self.stop_event.is_set():
    #         try:
    #             # 3. A traves del argumento on_success, le entregamos la funcion callback, que run_robot_test RELLENARÁ INTERNAMENTE 
    #             # Y al final, (si todo va bien), SE EJECUTARA LA FUNCION CALLBACK Y ENVIAREMOS LOS DATOS EN FORMATO DE TUPLA A TRAVES DEL BUZON HACIA LA GUI
    #             robot_executor._run_robot_test(
    #                 self.app_ref,
    #                 test_name=test_name,
    #                 preferred_filename='Get_Alarms.robot',
    #                 on_success=success_callback,    
    #                 suppress_gui_updates=True,
    #                 output_filename=None,
    #                 log_file=None,        
    #                 report_file=None      
    #             )
                
    #         except Exception as e:
    #             error_msg = f"Error en el bucle de monitorización de alarmas: {e}"
    #             self.app_ref.gui_queue.put(('main_status', error_msg, "red"))
    #             break 

    #         for _ in range(3):
    #             if self.stop_event.is_set():
    #                 break
    #             time.sleep(1)
    
    
    
    def _monitoring_loop(self):
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
                
                ip = self.app_ref.entry_ip.get()
                
                # Comando para ejecutar Robot desde la línea de comandos
                command = [
                    sys.executable, '-m', 'robot',
                    '--outputdir', 'test_results',
                    '--output', 'None',  # Deshabilitamos los archivos de salida
                    '--log', 'None',
                    '--report', 'None',
                    '--variable', f'IP_ADDRESS:{ip}',
                    # Pasamos la ruta del archivo de sesión del navegador de alarmas!
                    '--variable', f'SESSION_FILE:{os.path.abspath(self.alarms_session_file)}',
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
                                self.app_ref.gui_queue.put(('update_alarms_display', alarms_data))
                            except json.JSONDecodeError as e:
                                print(f"Error al decodificar JSON de alarmas: {e}")
                            break # Ya encontramos la línea, salimos del bucle
                
                # Si hubo un error en el subproceso, lo mostramos (opcional pero recomendado)
                elif result.returncode != 0:
                    print(f"Error en subproceso de alarmas: {result.stderr}")

            except Exception as e:
                error_msg = f"Error en el bucle de monitorización de alarmas: {e}"
                self.app_ref.gui_queue.put(('main_status', error_msg, "red"))
                break 

            # Espera antes de la siguiente comprobación
            for _ in range(6):
                if self.stop_event.is_set():
                    break
                time.sleep(1)