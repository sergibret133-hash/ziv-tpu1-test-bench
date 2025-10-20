import threading
from logic import db_handler
import logic.robot_executor as robot_executor # Necesitará llamar al ejecutor
import json
from tkinter import filedialog, messagebox


class MonitoringController:
    def __init__(self, app_ref):
        self.app_ref = app_ref
        
    def _run_retrieve_chrono_log_thread(self):
        self.app_ref.run_button_state(is_running=True)
        threading.Thread(target=self._execute_retrieve_chrono_log, daemon=True).start()
    def _execute_retrieve_chrono_log(self):
        """Runs the test to get the full chronological register."""
        test_name="Retrieve Chronological Register"
        
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
            preferred_filename="Chronological_Register.robot",
            on_success=success_callback,
            on_pass_message="Registro cronológico consultado.",
            on_fail_message="Fallo al consultar el registro cronológico."
        )

    def _run_clear_chrono_log_thread(self):
        self.app_ref.run_button_state(is_running=True)
        threading.Thread(target=self._execute_clear_chrono_log, daemon=True).start()
    def _execute_clear_chrono_log(self):
        """Runs the test to clear the chronological register."""
        robot_executor._run_robot_test(
            self.app_ref,
            test_name="Delete Chronological Register",
            preferred_filename="Chronological_Register.robot",
            on_success=lambda listener: self.app_ref.gui_queue.put(('update_chrono_log_display', "Registro cronológico borrado.")),
            on_pass_message="Registro cronológico borrado con éxito.",
            on_fail_message="Fallo al borrar el registro cronológico."
        )

    def _run_capture_last_entries_thread(self):
        self.app_ref.run_button_state(is_running=True)
        threading.Thread(target=self._execute_capture_last_entries, daemon=True).start()

    def _execute_capture_last_entries(self):
        """Runs the test to capture the last N entries from the log."""
        test_name="Capture Last Chronological Log Entries"
        
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
            preferred_filename="Chronological_Register.robot",
            variables=variables,
            on_success=success_callback,
            on_pass_message=f"Capturadas las últimas {num_entries} entradas.",
            on_fail_message="Fallo al capturar las últimas entradas."
        )
        

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


        


            
    
