import threading
from logic import db_handler
import robot
import logic.robot_executor as robot_executor 
from logic.robot_executor import TestOutputListener 
import json
from tkinter import filedialog, messagebox
import time
import re

class MonitoringController:
    def __init__(self, app_ref):
        self.app_ref = app_ref
        
    def _run_retrieve_chrono_log_thread(self):
        self.app_ref.run_button_state(is_running=True)
        threading.Thread(target=self._execute_retrieve_chrono_log, daemon=True).start()
    def _execute_retrieve_chrono_log(self):
        """Runs the test to get the full chronological register."""
        test_name="Retrieve Chronological Register"
        active_id = self.app_ref.active_session_id
        self.app_ref.is_main_task_running = True
        
        
        try:
            # Buscamos la info de actualizacion de la GUI en nuestro mapa inicializado en init (el mismo que usa el planificador cuando ejecuta los tests)
            gui_update_info = self.app_ref.test_gui_update_map.get(test_name)
            success_callback = None
            
            if gui_update_info: #si se encuentra, CREAMOS EL CALLBACK DINAMICO (de esta forma evitamos repetir codigo y amortizamos el mapeo que hacemos con el diccionario de tests)
                message_type, attr_names = gui_update_info

            #*********************************************************************************************************
                # Utilizamos el método de creación de  callback dinamico
                success_callback = self.app_ref._create_gui_update_callback(message_type, attr_names)
            #*********************************************************************************************************
            
            robot_executor._run_robot_test(
                self.app_ref,
                test_name=test_name,
                session_id=active_id,
                preferred_filename="Chronological_Register.robot",
                on_success=success_callback,
                on_pass_message="Registro cronológico consultado.",
                on_fail_message="Fallo al consultar el registro cronológico."
            )
        except Exception as e:
            self.app_ref.gui_queue.put(('main_status', f"Error en la tarea: {e}", "red")) 
            
        finally:
            self.app_ref.is_main_task_running = False
            self.app_ref.gui_queue.put(('enable_buttons', None))
            
    def _run_clear_chrono_log_thread(self):
        self.app_ref.run_button_state(is_running=True)
        threading.Thread(target=self._execute_clear_chrono_log, daemon=True).start()
        
    def _execute_clear_chrono_log(self):
        """Runs the test to clear the chronological register."""
        active_id = self.app_ref.active_session_id
        try:
            robot_executor._run_robot_test(
                self.app_ref,
                test_name="Delete Chronological Register",
                session_id=active_id,
                preferred_filename="Chronological_Register.robot",
                on_success=lambda listener: self.app_ref.gui_queue.put(('update_chrono_log_display', "Registro cronológico borrado.")),
                on_pass_message="Registro cronológico borrado con éxito.",
                on_fail_message="Fallo al borrar el registro cronológico."
            )
        except Exception as e:
            self.app_ref.gui_queue.put(('main_status', f"Error en la tarea: {e}", "red")) 
            
        finally:
            self.app_ref.is_main_task_running = False
            self.app_ref.gui_queue.put(('enable_buttons', None))
            
    def _run_capture_last_entries_thread(self):
        self.app_ref.run_button_state(is_running=True)
        threading.Thread(target=self._execute_capture_last_entries, daemon=True).start()

    def _execute_capture_last_entries(self):
        """Runs the test to capture the last N entries from the log."""
        test_name="Capture Last Chronological Log Entries"
        active_id = self.app_ref.active_session_id
        self.app_ref.is_main_task_running = True
        
        try:
            num_entries = self.app_ref.num_entries_entry.get()
            event_filter = self.app_ref.event_filter_entry.get()
            order = self.app_ref.chrono_order_combobox.get()
            order_bool = "True" if order == "Ascendente" else "False"

            if not num_entries.isdigit() or int(num_entries) <= 0:
                self.app_ref.gui_queue.put(('main_status', "Error: 'Número de Entradas' debe ser un número positivo.", "red"))
                self.app_ref.run_button_state(is_running=False)
                return

            variables = [
                f"EXPECTED_NUM_ENTRIES:{num_entries}",
                f"EVENT_ALARM_FILTER:{event_filter}",
                f"CHRONO_ORDER:{order_bool}"
            ]

            # Buscamos la info de actualizacion de la GUI en nuestro mapa inicializado en init (el mismo que usa el planificador cuando ejecuta los tests)
            gui_update_info = self.app_ref.test_gui_update_map.get(test_name)
            success_callback = None
            
            if gui_update_info: #si se encuentra, CREAMOS EL CALLBACK DINAMICO (de esta forma evitamos repetir codigo y amortizamos el mapeo que hacemos con el diccionario de tests)
                message_type, attr_names = gui_update_info

            #*********************************************************************************************************
                # Utilizamos el método de creación de  callback dinamico
                success_callback = self.app_ref._create_gui_update_callback(message_type, attr_names)
            #*********************************************************************************************************


            robot_executor._run_robot_test(
                self.app_ref,
                test_name=test_name,
                session_id=active_id,
                preferred_filename="Chronological_Register.robot",
                variables=variables,
                on_success=success_callback,
                on_pass_message=f"Capturadas las últimas {num_entries} entradas.",
                on_fail_message="Fallo al capturar las últimas entradas."
            )
            
        except Exception as e:
            self.app_ref.gui_queue.put(('main_status', f"Error en la tarea: {e}", "red")) 
            
        finally:
            self.app_ref.is_main_task_running = False
            self.app_ref.gui_queue.put(('enable_buttons', None))
            
            
    def _load_traps_from_file(self):
        """Abre un diálogo para seleccionar un archivo .db y carga sus traps."""
        # Abre el explorador de archivos, empezando en la carpeta 'trap_history'
        filepath = filedialog.askopenfilename(
            title="Seleccionar archivo de historial de traps",
            initialdir="trap_history",
            filetypes=(("Database files", "*.db"), ("All files", "*.*"))
        )
        if not filepath:
            return  # El usuario canceló la selección
        
        trap_rows = db_handler.fetch_traps_from_db(filepath) # fetch_traps_from_db ya maneja sus propias conexiones y se encuentra en db_handler.py del proyecto.
        if trap_rows is not None:
            self.app_ref.update_trap_history_display(trap_rows, filepath)
        else:
            self.app_ref.update_status("Error al leer el archivo de la base de datos.", "red")


        

    # Funciones para la pestaña de análisis de correlacion entre los resultados obtenidos por el SNMP y los obtenidos por el Registro Cronológico
    def start_correlation_test(self):
            """Inicia la prueba de correlación en un hilo separado."""
            self.app_ref.correlation_button.configure(state="disabled", text="Ejecutando...")
            self._update_corr_display("Esperando evento...", "Esperando evento...", "PENDIENTE", "gray")
            
            # Asumimos que tienes este controlador y que puedes añadirle este método
            self.app_ref.trap_listener_controller._reset_traps() 
            
            threading.Thread(target=self._run_correlation_test, daemon=True).start()

    def _run_correlation_test(self):
        """Ejecuta la lógica de la prueba en un hilo."""
        active_id = self.app_ref.active_session_id
        self.app_ref.is_main_task_running = True # Ponemos el semáforo en ROJO
        
        # Escenario de Pruebas:
        activate_deactivate = 1
        inputs_a_probar = [1]
        duration = 10        
        wait_time = 12
        
        
        inputs_list_str = str(inputs_a_probar).replace(" ", "")
        try:
            # limpiamos traps antes!
            self.app_ref.trap_listener_controller._reset_traps()
            # --- 1. PROVOCAR EL EVENTO ---
            robot_executor._run_robot_test(
                self.app_ref,
                test_name="Input Activation",
                session_id=active_id,
                preferred_filename="InputActivation.robot",
                variables=[
                    f"ACTIVATE_DEACTIVATE:{activate_deactivate}",
                    f"DURATION:{duration}",
                    f"INPUTS_LIST:{inputs_list_str}"
                ],
                suppress_gui_updates=True,
                log_file=None, report_file=None, output_filename=None
            )
            
            time.sleep(wait_time) # Margen para que el equipo procese y envíe

            # --- 2. RECOGER DATOS DEL CRONOLÓGICO ---
            chrono_listener = TestOutputListener(self.app_ref)
            script_path = robot_executor._find_test_file(self.app_ref, "Capture Last Chronological Log Entries", "Chronological_Register.robot")
            
            robot.run(
                script_path,
                test="Capture Last Chronological Log Entries",
                variable=[f"IP_ADDRESS:{self.app_ref.sessions[active_id]['ip']}", f"SESSION_ALIAS:{active_id}", "EXPECTED_NUM_ENTRIES:2"],
                listener=chrono_listener,
                output=None, log=None, report=None, stdout=None, stderr=None
            )
            chrono_data = chrono_listener.chronological_log

            # --- 3. RECOGER DATOS DE TRAPS ---
            trap_data = self.app_ref.trap_listener_controller.get_raw_traps_for_correlation()

            # --- 4. COMPARAR Y MOSTRAR ---
            self._compare_and_update_gui(chrono_data, trap_data, inputs_a_probar) # Busca "Input 1"

        except Exception as e:
            self.app_ref.gui_queue.put(('main_status', f"Error en test de correlación: {e}", "red"))
            self._update_corr_display(f"Error: {e}", "Error", "ERROR", "red")
        
        finally:
            # Reactivamos el botón y ponemos el semáforo en VERDE
            self.app_ref.is_main_task_running = False 
            self.app_ref.correlation_button.configure(state="normal", text="▶️ Iniciar Test de Correlación (Activar Entrada 1)")

    def _parse_chrono_events(self, chrono_data, expected_inputs):
        """Parsea la salida del cronológico y la compara con los inputs esperados."""
        
        # Usamos sets para encontrar coincidencias sin importar el orden
        expected_set = set(map(str, expected_inputs))
        found_activations = set()
        found_deactivations = set()
        
        report_lines = []

        if not chrono_data:
            report_lines.append("[FALLO] No se recibieron datos del cronológico.")
            return False, False, report_lines

        # Expresión regular para capturar (ACTIVATION) o (DEACTIVATION) y el número (8)
        event_regex = re.compile(r"\((ACTIVATION|DEACTIVATION)\) OF INPUT \((\d+)\)")
        
        for entry in chrono_data:
            if not isinstance(entry, dict):
                report_lines.append(f"[AVISO] Ignorando entrada no válida en cronológico (no es dict): {type(entry)}")
                continue 
            
            # Como asumimos que es un diccionario lo que nos llega, obtenemos el TEXTO del evento
            event_text = entry.get('alarm_event', '')
            
            match = event_regex.search(event_text)  # Usamos el search para quedarnos con los dos grupos que habiamos especificado en event_regex
            
            if match:
                event_type, input_num_str = match.groups()  # Son los dos grupos que hemos creado arriba en la expresion regular de event_regex. El intervalo de cada grupo se define entre \( y \)
                if input_num_str in expected_set:   # Revisamos que dentro el input_num que ha encontrado en la linea que esta recorriendo del registro cronologico coincida con los inputs que hemos activado.
                    if event_type == "ACTIVATION":  # En caso de que el numero de input coincida, revisamos si es una activacion o una desactivacion para añadirlo al vector de activaciones o desactivaciones encontradas. 
                        # MAS ADELANTE COMPROBAREMOS TAMBIÉN SI EL HECHO DE SER UNA ACTIVACIÓN O DESACTIVACION TAMBIEN CONCUERDA CON LO QUE NOS PASAN POR EL ARGUMENTO DEL METODO.
                        found_activations.add(input_num_str)
                    elif event_type == "DEACTIVATION":
                        found_deactivations.add(input_num_str)
        
        # Comprobar EL NUMERO DE *** ACTIVACIONES ***. EXPECTED SET ERA EL VECTOR DE INPUTS ESPERADOS (TEORICOS). TIENE QUE HABER EL MISMO NUMERO DE FOUND_ACTIVATIONS QUE DE EXPECTED_SET
        if found_activations == expected_set:   # CUIDADO! COMPROBAMOS SI LAS ACTIVACIONES (CON SU NUM INPUT) COINCIDEN. NO EL NUMERO DE APARICIONES!
            report_lines.append(f"[ÉXITO] Cronológico: Se encontraron todas las {len(expected_set)} activaciones.")
            activations_ok = True
        else:
            report_lines.append(f"[FALLO] Cronológico: Faltaron activaciones. Esperadas: {expected_set}, Encontradas: {found_activations}")
            activations_ok = False

        # Comprobar *** DESACTIVACIONES ***
        if found_deactivations == expected_set:
            report_lines.append(f"[ÉXITO] Cronológico: Se encontraron todas las {len(expected_set)} desactivaciones.")
            deactivations_ok = True
        else:
            report_lines.append(f"[FALLO] Cronológico: Faltaron desactivaciones. Esperadas: {expected_set}, Encontradas: {found_deactivations}")
            deactivations_ok = False

        return activations_ok, deactivations_ok, report_lines



    def _parse_trap_events(self, trap_data, expected_inputs):
        """Parsea la salida de traps y la compara con los inputs esperados."""
        
        expected_set = set(map(str, expected_inputs)) # '1', '2', etc.
        report_lines = []
        
        if not trap_data or not isinstance(trap_data, list):    # Consideraremos que no hemos recibido traps si lo que nos llega no es en forma de lista.
            report_lines.append("[FALLO] No se recibieron traps SNMP.")
            return False, False, report_lines
            
        activation_traps = []
        deactivation_traps = []

        # Clasificar traps con el primer parametro del trap (indica si hay activacion o desactivacion, PERO NO INDICA QUE NUMERO DE INPUT SE HA ACTIVADO!)
        for trap in trap_data:
            if not isinstance(trap, dict):  # Lo normal es que nos llegue en formato de diccionario. ->
                report_lines.append(f"[AVISO] Ignorando entrada no válida en traps: {type(trap)}")  # -> Si no nos llega en este formato, no nos vale
                continue # Saltar este trap si es un string
            
            varbinds = trap.get('varbinds_dict', {})
            state = varbinds.get('DIMAT-TPU1C-MIB::tpu1cNotifyState')   # Cuidado. En este caso, solo nos basamos en tpu1cNotifyState, que nos da 1 o 0 en funcion de si es activacion o desactivacion
            
            if state == 1 or state == '1':
                activation_traps.append(trap)   # Se añade EL TRAP COMPLETO DE ESA ACTIVACION. Lo hacemos porque mas tarde analizaremos otra linea del trap donde nos aparecerá el num input activado.
            elif state == 0 or state == '0':
                deactivation_traps.append(trap) # Se añade EL TRAP COMPLETO DE ESA DESACTIVACION. Lo hacemos porque mas tarde analizaremos otra linea del trap donde tendremos que verificar QUE NO HAYA NINGUN NUM INPUT ACTIVO. 
        
        if not activation_traps:
            report_lines.append("[FALLO] SNMP: No se recibieron traps de ACTIVACIÓN (State: 1).")
        if not deactivation_traps:
            report_lines.append("[FALLO] SNMP: No se recibieron traps de DESACTIVACIÓN (State: 0).")
            
# *************************************************************************************************************************
        # Una vez hemos localizado y guardado los TRAPS de activaciones y desactivaciones,
        # de los traps guardados, nos quedaremos con la parte que nos interesa (inp1, inp2...)
        # Daremos un nuevo formato a los inputs esperados que tomamos como referencia (para que tengan la misma pinta que inp1, inp2,...)
        # Comparamos y decidimos si la activacion o desactivacion es correcta.
        # *************************************************************************************************************************

        # ***ACTIVACIONES*** Buscamos el trap que contenga el estado final de las ***ACTIVACIONES***:
        trap_activation_ok = False
        # Damos el formato que nos interesa a las ACTIVACIONES ESPERADAS que nos pasan como argumento.
        expected_trap_inputs = set([f"inp{i}" for i in expected_inputs])    # f"inp{i}": Para cada número i de la lista, CREA UNA NUEVA CADENA DE TEXTO (un f-string) añadiéndole el prefijo "inp".
        
        # Una vez tenemos bien guardado en expected_trap_inputs el formato estandar (inpx) de los inputs pasados como argumentos en expected_inputs, ->
        # -> tenempos que recorrer el vector crudo de traps de activaciones y quedarnos con el formato inpx que hay a continuacion de tpu1cNotifyInputCurrentState
        for trap in activation_traps:
            varbinds = trap.get('varbinds_dict', {})
            current_inputs_str = varbinds.get('DIMAT-TPU1C-MIB::tpu1cNotifyInputCurrentState', '').strip()  # Aqui nos quedamos con el numero de inputs activados! No solo con su estado. Separamos en forma de lista todos los numeros

            if current_inputs_str:  # Si hay numero de inputs que se hayan activado en el trap que estamos recorriendo..
                # Como lo que hay a la derecha del tpu1cNotifyInputCurrentState son TODOS LOS INPUTS ACTIVADOS ->
                found_trap_inputs = set(current_inputs_str.split(', '))     # -> tenemos que separarlos (ya que es una cadena str de momento) para poder comparar a posteriori
                if found_trap_inputs == expected_trap_inputs:   # Comprobamos que los numero de input que hemos separado coincidan con los esperados que habiamos pasado como argumento.
                    trap_activation_ok = True
                    break # Encontramos el trap con el estado final correcto

        if trap_activation_ok:
            report_lines.append(f"[ÉXITO] SNMP: Se encontró trap de activación con estado final: {expected_trap_inputs}")
        else:
            report_lines.append(f"[FALLO] SNMP: No se encontró trap de activación con el estado final esperado.")
            
# *************************************************************************************************************************
        # 3. Analizar traps de Desactivación
        # ***DESACTIVADO*** Buscamos un trap que muestre que todas las entradas se han ***DESACTIVADO*** (ya que recordemos que se van desactivando de en una en una. 
        # y la info que nos sigue proporcionando la linea que analizaos del trap SON SOLO LOS INPUT ACTIVOS. POR LO QUE la idea es ver cuando ya no quede NINGUNO ACTIVO)
        trap_deactivation_ok = False
        for trap in deactivation_traps: # Recordemos que en deactivation_traps estan todos los traps EN CRUDO (con el tpu1cNotifyInputCurrentState que no queremos)
            varbinds = trap.get('varbinds_dict', {})    # Es una forma segura de acceder a las claves que hay dentro del diccionario varbinds que hay dentro del diccionario del trap que estamos recorriendo. 
            current_inputs_str = varbinds.get('DIMAT-TPU1C-MIB::tpu1cNotifyInputCurrentState', 'valor_default').strip() # Nos guardamos los valores de la clave DIMAT-TPU1C-MIB::tpu1cNotifyInputCurrentState que hay dentro del diccionario varbinds_dict
             
            # Si la clave existe y su valor es un string vacío, está desactivado
            if not current_inputs_str:
                trap_deactivation_ok = True
                break # Encontramos el trap con el estado final vacío

        if trap_deactivation_ok:
            report_lines.append(f"[ÉXITO] SNMP: Se encontró trap de desactivación con estado final 'vacío'.")
        else:
            report_lines.append(f"[FALLO] SNMP: No se encontró trap de desactivación con estado final 'vacío'.")

        return trap_activation_ok, trap_deactivation_ok, report_lines
        
    
    def _compare_and_update_gui(self, chrono_data, trap_data, expected_inputs):
        """Compara los resultados y envía la actualización a la GUI."""
        
        # ***Análisis mediante las funciones que comprueban que las activaciones/desactivaciones coincidan con lo esperado***
        chrono_act_ok, chrono_deact_ok, chrono_report = self._parse_chrono_events(chrono_data, expected_inputs)
        trap_act_ok, trap_deact_ok, trap_report = self._parse_trap_events(trap_data, expected_inputs)

        # --- Formateo de Salida (para los visores) ---
        chrono_text_report = "--- REPORTE DEL REGISTRO CRONOLÓGICO ---\n"
        chrono_text_report += "\n".join(chrono_report)
        chrono_text_report += "\n\n--- DATOS EN BRUTO ---\n"
        
        if isinstance(chrono_data, list) and chrono_data:
            formatted_lines = []
            for entry in chrono_data:
                # Aseguramos que 'entry' sea un diccionario antes de usar .get()
                if isinstance(entry, dict):
                    ts = entry.get('timestamp', 'N/A')
                    event = entry.get('alarm_event', 'N/A')
                    formatted_lines.append(f"Timestamp: {ts} | Evento: {event}")
                elif isinstance(entry, str):
                    formatted_lines.append(entry) # Si ya era un string
                    
            chrono_text_report += "\n".join(formatted_lines)

        elif isinstance(chrono_data, str):
            chrono_text_report += chrono_data # Si ya era un string (ej. un error)
        else:
            chrono_text_report += "Sin datos."
        
        trap_text_report = "--- REPORTE DE TRAPS SNMP ---\n"
        trap_text_report += "\n".join(trap_report)
        trap_text_report += "\n\n--- DATOS EN BRUTO ---\n"

        # como lo que se espera es un str, tenemos que convertir el diccionario a cadena de str
        if isinstance(trap_data, list) and trap_data:   # Si hay datos y el tipo de dato de trap_data tiene formato de lista
                    formatted_text = ""
                    for i, trap in enumerate(trap_data):
                        formatted_text += f"--- Trap #{i+1} ---\n"  # Numeramos el trap que estamos recorriendo.
                        if isinstance(trap, dict): # Si el trap que recorremos es un diccionario
                            for key, value in trap.items(): # Recorremos cada una de sus claves
                                if key == 'varbinds_dict' and isinstance(value, dict):  # Si se trata de varbinds_dict, verificando que sea un diccionario  (es un diccionario dentro del diccionario principal del trap)
                                    formatted_text += f"  {key}:\n" # Por cada clave ->
                                    for vk, vv in value.items():
                                        formatted_text += f"    {vk}: {vv}\n"   # -> Vamos añadiendo cada uno de los elementos de esa clave.
                                else:
                                    formatted_text += f"  {key}: {value}\n"
                        elif isinstance(trap, str): # Si el trap que recorremos no es un diccionario
                            formatted_text += f"{trap}\n"   # Lo añadimos directamente
                        formatted_text += "\n"
                    trap_text_report += formatted_text
        elif isinstance(trap_data, str):    # Si TODOS los traps ya estan en formato string, no hace falta que hagamos nada. Podemos pasar el report hecho por el parser directamente.
            trap_text_report += trap_data
        else:
            trap_text_report += "Sin datos."


        
        # --- Veredicto Final ---
        if (chrono_act_ok and chrono_deact_ok and trap_act_ok and trap_deact_ok):
            result = "ÉXITO"
            color = "green"
        elif (chrono_act_ok or chrono_deact_ok or trap_act_ok or trap_deact_ok):
            result = "FALLO PARCIAL"
            color = "orange"
        else:
            result = "FALLO TOTAL"
            color = "red"
            
        self._update_corr_display(chrono_text_report, trap_text_report, result, color)
        
    def _update_corr_display(self, chrono_text, trap_text, result, color):
        """Envía los datos de la correlación a la cola de la GUI."""
        self.app_ref.gui_queue.put(
            ('update_correlation_display', chrono_text, trap_text, result, color)
        )