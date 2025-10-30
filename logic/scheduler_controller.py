
import json
import customtkinter as ctk
import os
from tkinter import filedialog
import threading
import  subprocess
from datetime import datetime, timezone

from logic import db_handler
import time
import sys
import csv
import logic.robot_executor as robot_executor



class SchedulerController:
    def __init__(self, app_ref):
        self.app_ref = app_ref  # Reference to the main application
        
        self.current_task_index = -1
        self.stop_sequence_flag = threading.Event()
        self.task_output_files = [] # Para guardar los output.xml
        self.verification_report_file = None
        self.current_db_path = None
        
        
    def _on_task_type_change(self, selected_type):
        """Muestra u oculta los widgets de creación de tareas según el tipo seleccionado."""
        # Lo hacemos para mostrar la info relevante en cada momento.
        # Por defecto, cuando el "formulario" se reinicia, se ocultan todos estos campos
        
        # Ocultar todos los widgets opcionales primero ("Test a ejecutar", "Duracion" y "Variables"). AL OCULTARLOS CON FORGET PASARAN A OCUPAR UN ESPACIO DE 0PX, POR LO QUE P.EJ. ELEMENTOS DE LA 6A FILA ("Si Falla") APARECERAN JUNTO A LA 1A Y 2A QUE SON PERMANENTES!
        # Test a ejecutar
        self.app_ref.task_test_label.grid_forget()
        self.app_ref.task_test_combo.grid_forget()
        # Duracion
        self.app_ref.task_param_label.grid_forget()
        self.app_ref.task_param_entry.grid_forget()
        # Variables entrada
        self.app_ref.task_vars_label.grid_forget()
        self.app_ref.task_vars_entry.grid_forget()
        
        # Ocultar widgets OID
        self.app_ref.task_oid_label.grid_forget()
        self.app_ref.task_oid_entry.grid_forget()
        
        # Advertencia SNMP
        self.app_ref.snmp_warning_label.grid_forget()

        # Variables esperadas
        # self.app_ref.task_args_display_label.grid_forget()    # Finalmente ocultaremos el frame intermedio completo, ya que hemos añadido el boton de copiar ->
        # ->
        if hasattr(self.app_ref, 'args_frame') and self.app_ref.args_frame is not None:
            self.app_ref.args_frame.grid_forget()
        
        # Selector de Sesión
        if hasattr(self.app_ref, 'task_session_selector') and self.app_ref.task_session_selector:
            self.app_ref.task_session_selector.grid_forget() # Ocultar selector de sesión
        
        # Mostrar los widgets necesarios para el tipo de tarea seleccionado. Solo para estos tipos de tareas los mostraremos.
        if selected_type == "Ejecutar Test":
            self.app_ref.task_test_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
            self.app_ref.task_test_combo.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

            self.app_ref.task_vars_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")
            self.app_ref.task_vars_entry.grid(row=3, column=1, padx=10, pady=5, sticky="ew")

            self.app_ref.args_frame.grid(row=4, column=1, padx=10, pady=(0,5), sticky="w")
            
            if hasattr(self.app_ref, 'task_session_selector') and self.app_ref.task_session_selector:
                self.app_ref.task_session_selector.grid(row=5, column=1, padx=10, pady=5, sticky="ew") # Mostrar selector de sesión
            
            self._on_test_selection_change(self.app_ref.task_test_combo.get()) # Llamada inicial al metodo que nos permite añadir la fila con los argumentos de ese testcase

        elif selected_type == "Pausa (segundos)":
            self.app_ref.task_param_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
            self.app_ref.task_param_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        elif selected_type == "Verificar Traps SNMP Nuevos":
            # Warning Monitoreo
            self.app_ref.snmp_warning_label.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="w")
            #  OID
            self.app_ref.task_oid_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")
            self.app_ref.task_oid_entry.grid(row=3, column=1, padx=10, pady=5, sticky="ew")
            # Selector de Sesión
            if hasattr(self.app_ref, 'task_session_selector') and self.app_ref.task_session_selector:
                self.app_ref.task_session_selector.grid(row=5, column=1, padx=10, pady=5, sticky="ew")

        elif selected_type == "Limpiar Buffer de Traps":
                if hasattr(self.app_ref, 'task_session_selector') and self.app_ref.task_session_selector:
                    self.app_ref.task_session_selector.grid(row=5, column=1, padx=10, pady=5, sticky="ew") # Mostrar selector de sesión


    def _select_task_in_sequence(self, index):
        """Gestiona la selección de una tarea en la lista."""
        self.app_ref.selected_task_index = index
        for i, frame in enumerate(self.app_ref.task_widgets):
            if i == index:
                frame.configure(fg_color=("gray80", "gray25")) # Color de resaltado
            else:
                frame.configure(fg_color="transparent")
                
    def _move_task(self, direction):
        """Mueve la tarea seleccionada hacia arriba (-1) o hacia abajo (1)."""
        if self.app_ref.selected_task_index == -1: return # Es para evitar mover nada u obtener error en caso de querer mover sin seleccionar nada.

        # Partimos de la lista de tareas que está en la memoria (self.app_ref.task_sequence)
        new_index = self.app_ref.selected_task_index + direction # Calculamos la nueva posición del objeto seleccionado que queremos mover.
        if 0 <= new_index < len(self.app_ref.task_sequence): # Nos aseguramos que la nueva pos se encuentre dentro de los indices posibles de la lista.
            # Intercambiar elementos en la lista de datos
            item = self.app_ref.task_sequence.pop(self.app_ref.selected_task_index) # Nos lo saca de la lista, guardandolo temporalmente
            self.app_ref.task_sequence.insert(new_index, item)
            
            # Redibujar y pre-seleccionar el elemento movido
            self.app_ref.update_task_sequence_display() # Una vez actualizada "task_sequence", podemos actualizar la lista en pantalla
            self.app_ref._select_task_in_sequence(new_index) # Hemos redibujado la lista de tareas actualizada, pero queremos conservar el elemento que habíamos movido como seleccionado.
            
    def _remove_selected_task(self):
        """Elimina la tarea seleccionada de la secuencia."""
        if self.app_ref.selected_task_index == -1: return # Es para evitar mover nada u obtener error en caso de querer mover sin seleccionar nada.
        
        self.app_ref.task_sequence.pop(self.app_ref.selected_task_index) # Lo sacamos de la lista SIN GUARDARLO
        self.app_ref.update_task_sequence_display()
        
        
    def _on_test_selection_change(self, selected_test):
        """Se activa al seleccionar un test y muestra sus argumentos requeridos."""

            # Si el usuario selecciona una cabecera (---), no hacemos nada.
        if not selected_test or selected_test.strip().startswith("---"):
            self.app_ref.task_args_display_label.configure(text="") # Limpiamos la etiqueta
            return

        actual_test_name = selected_test.strip()
        args = self.app_ref._get_test_case_arguments(actual_test_name)
        if args:
            self.app_ref.task_args_display_label.configure(text=f"Argumentos: {', '.join(args)}")
        else:
            self.app_ref.task_args_display_label.configure(text="Este test no requiere argumentos.")
            
    def _add_task_to_sequence(self):
        """Recopila la información de la tarea y la añade a la secuencia"""
        task_type = self.app_ref.task_type_combo.get()
        on_fail_action = self.app_ref.task_on_fail_combo.get()  # Puede ser "Detener secuencia", "Continuar"
        
        # Si la tarea es de verificación, forzamos que siempre continúe para que pueda continuar la secuencia con otras tareas. (sobretodo cuando se trata de seguir realizando más comprobaciones de traps)
        if task_type == "Verificar Traps SNMP Nuevos":
            on_fail_action = "Continuar"
        
        task_details = {    # Diccionario de valores que iremos rellenando. ESTE SERÁ EL ELEMENTO QUE AÑADIREMOS AL FINAL A LA LISTA DE SECUENCIA DE TAREAS!
            'type': task_type,
            'name': '', # Lo gaurdaremos mas abajo
            'on_fail': on_fail_action,
            'session_id': None, #Por defecto
            'file': '', #Por defecto
            'vars': '', #Por defecto
            'param': '' # Para Pausa o Traps
        }
        # **************** Lógica de Sesión (Solo para Tests ****************
        # *****************************************
        session_id = 'A'    # por defecto
        if task_type == "Ejecutar Test" or task_type == "Verificar Traps SNMP Nuevos" or task_type == "Limpiar Buffer de Traps":
            selected_session_str = self.app_ref.task_session_selector.get() # Para poder escoger la sesion en la que se ejecuta el test
            session_map = {"Sesión A": "A", "Sesión B": "B"}    # Con esto, definimos un mapeo para que cuando nos pasen p ej "Sesión A", nos quedemos con el valor "A" que es lo que nos interesa guardar después en 'session_id' del diccionario de la tarea
            session_id = session_map.get(selected_session_str, 'A') # Definimos 'A' como VALOR por defecto
            task_details['session_id'] = session_id # <-- Se guarda el ID de la sesión


        if task_type == "Ejecutar Test":
            test_full_name = self.app_ref.task_test_combo.get().strip()
            
            test_name = test_full_name.lstrip(" -")     # Limpiamos el nombre del test si viene con formato '  Test Name'

            robot_file_path = robot_executor._find_test_file(self.app_ref, test_name)      # Buscamos el archivo .robot correspondiente
            if not robot_file_path:
                self.app_ref.gui_queue.put(('scheduler_log', f" Error: No se pudo encontrar el archivo .robot para el test '{test_name}'.\n", "red"))
                return
        
            # Adquirimos las variables que se pasarán al test
            variables = self.app_ref.task_vars_entry.get()
            
            # Usamos el nombre limpio para la lógica, aunque usaremos el completo para mostrar
            display_name = test_full_name if test_full_name.startswith("---") else test_name
            
            task_details['name'] = f"{display_name} (Sesión: {session_id})" # <-- Nombre actualizado
            task_details['file'] = os.path.basename(robot_file_path) # Guardamos solo el nombre del archivo
            task_details['vars'] = variables
            

            self.app_ref.task_vars_entry.delete(0, 'end') # Limpiamos el campo de variables para la próxima tarea

        elif task_type == "Pausa (segundos)":
            duration_str = self.app_ref.task_param_entry.get()
            try:
                duration = int(duration_str)
                if duration <= 0:
                    raise ValueError
            except ValueError:
                self.app_ref.gui_queue.put(('scheduler_log', f"Error: La duración de la pausa debe ser un número positivo.\n", "red"))
                return
            task_details['name'] = f"PAUSA: {duration} segundos" 
            task_details['param'] = duration
            


        elif task_type == "Verificar Traps SNMP Nuevos":
            oid_to_verify = self.app_ref.task_oid_entry.get().strip()
            if not oid_to_verify:
                task_details['param'] = None
                task_details['name'] = f"Verificar Traps SNMP Nuevos(Sesión: {session_id})"
            else:
                # Si se especifica OID, la tarea es verificar el OID sin más!
                task_details['param'] = oid_to_verify
                task_details['name'] = f"Verificar Trap (OID: {oid_to_verify}) (Sesión: {session_id})"
                
        elif task_type == "Limpiar Buffer de Traps":
            # session_id ya está definido arriba
            task_details['name'] = f"Limpiar Buffer de Traps (Sesión: {session_id})"
            task_details['session_id'] = session_id    
            
            
        # Añadimos la tarea a la secuencia una vez rellenado sus detalles
        self.app_ref.task_sequence.append(task_details)
        self.app_ref.update_task_sequence_display()
        
        
        # Limpiamos los campos después de añadir
        self.app_ref.task_vars_entry.delete(0, 'end')
        self.app_ref.task_param_entry.delete(0, 'end')
        self.app_ref.task_oid_entry.delete(0, 'end')
        self.app_ref.task_test_combo.set("")
        self.app_ref.task_args_display_label.configure(text="")
        
        
    def _copy_suggested_args(self):
        """
        Copia los argumentos sugeridos de la etiqueta de ayuda al portapapeles.
        """
        # Obtener el texto completo de la etiqueta de ayuda
        full_text = self.app_ref.task_args_display_label.cget("text")
        
        # Limpiar el texto para quedarnos solo con las variables
        #    (eliminamos el prefijo "Argumentos: ")
        if "Argumentos: " in full_text:
            args_to_copy = full_text.replace("Argumentos: ", "")
            
            # Llamar a la función de copiado que ya tienes
            if args_to_copy:
                self.app_ref.copy_to_clipboard(args_to_copy)
            else:
                self.app_ref._update_status("No hay argumentos que copiar.", "orange")
        else:
            self.app_ref._update_status("No hay argumentos que copiar.", "orange")

    # ************ FUNCIONES DE CARGA Y GUARDADO DE PERFILES DE SECUENCIAS **********
            
    def _save_sequence_profile(self):
        """Guarda la secuencia de tareas actual en un archivo JSON."""
        # Comprobamos si hay algo que guardar
        if not self.app_ref.task_sequence:
            self.app_ref._update_status("No hay ninguna secuencia de tareas para guardar.", "orange")
            return

        # Creamos la carpeta de perfiles si no existe
        profiles_dir = "scheduler_profiles"
        os.makedirs(profiles_dir, exist_ok=True)

        # Abrimos el diálogo "Guardar como.."
        filepath = filedialog.asksaveasfilename(
            title="Guardar Perfil de la Secuencia",
            initialdir=profiles_dir,
            defaultextension=".json",
            filetypes=(("JSON files", "*.json"), ("All files", "*.*"))
        )

        # Si el usuario cancela, no hacemos nada
        if not filepath:
            return

        # Escribimos la secuencia en el archivo
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                # json.dumps convierte la lista de Python a un string en formato JSON
                # indent=4 hace que el archivo sea legible para los humanos
                json.dump(self.app_ref.task_sequence, f, indent=4)
            
            self.app_ref.gui_queue.put(('main_status', f"Perfil '{os.path.basename(filepath)}' guardado con éxito.", "green"))
        except Exception as e:
            self.app_ref.gui_queue.put(('main_status', f"Error al guardar el perfil: {e}", "red"))
            
    def _load_sequence_profile(self):
        """Carga una secuencia de tareas desde un archivo JSON."""
        
        profiles_dir = "scheduler_profiles" # Carpeta donde guardamos los perfiles
        os.makedirs(profiles_dir, exist_ok=True)

        # Abrimos el diálogo "Abrir..."
        filepath = filedialog.askopenfilename(
            title="Cargar Perfil de la Secuencia",
            initialdir=profiles_dir,
            filetypes=(("JSON files", "*.json"), ("All files", "*.*"))
        )

        # Si el usuario cancela, no hacemos nada
        if not filepath:
            return

        # Leemos y cargamos la secuencia desde el archivo
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                # json.load convierte el string JSON de nuevo a una lista de Python!
                loaded_sequence = json.load(f)
            
            # Actualizamos la secuencia actual y refrescamos la GUI
            self.app_ref.task_sequence = loaded_sequence
            self.app_ref.update_task_sequence_display()
            
            self.app_ref.gui_queue.put(('main_status', f"Perfil '{os.path.basename(filepath)}' cargado con éxito.", "green"))

        except json.JSONDecodeError:
            self.app_ref.gui_queue.put(('main_status', "Error: El archivo seleccionado no es un perfil JSON válido.", "red"))
        except Exception as e:
            self.app_ref.gui_queue.put(('main_status', f"Error al cargar el perfil: {e}", "red"))        





    def _run_task_sequence_thread(self):
        """Inicia la ejecución de la secuencia de tareas en un hilo separado."""
        if self.app_ref.is_main_task_running:
            self.app_ref.gui_queue.put(('scheduler_log', "Error: Ya hay una tarea principal en ejecución.\n", "red"))
            return
        if not self.app_ref.task_sequence:
            self.app_ref.gui_queue.put(('scheduler_log', "No hay tareas en la secuencia para ejecutar.\n", "gray"))
            return
        
        required_sessions = set(task['session_id'] for task in self.app_ref.task_sequence if task['type'] == 'Ejecutar Test')
        for session_id in required_sessions:
            if not self.app_ref.sessions[session_id]['process']:
                msg = f"Error: La Sesión {session_id} no está conectada.\n"
                self.app_ref.gui_queue.put(('scheduler_log', msg, "red"))
                return
            
        # Preparamos antes de la ejecución
        self.app_ref.is_main_task_running = True
        self.stop_sequence_flag.clear()
        self.task_output_files = [] # Limpiar lista de outputs.xml
        self.current_task_index = -1
        # Deshabilitamos botones para no interferir pasando el estado "is_running"
        # self.app_ref.run_button_state(is_running=True)    # Mejor pasarlo a la cola y no llamar a una función de app_ref desde un controlador.. ->
        # ->
        self.app_ref.gui_queue.put(('enable_buttons', None)) # Actualiza estado de botones
        self.app_ref.gui_queue.put(('scheduler_log', "▶️ Iniciando secuencia...\n", "cyan"))
        
        
        try:
            history_dir = "trap_history"
            os.makedirs(history_dir, exist_ok=True)
            
            history_name = self.app_ref.scheduler_history_name_entry.get()
            if not history_name:
                history_name = f"traps_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.current_db_path = os.path.join(history_dir, f"{history_name}.db")
            
            db_handler.initialize_database(self.current_db_path)
            self.app_ref.gui_queue.put(('scheduler_log', f"  Historial de traps (.db) inicializado en: {self.current_db_path}\n", "gray"))
        except Exception as e:
            self.app_ref.gui_queue.put(('scheduler_log', f"❌ Error al inicializar historial DB: {e}\n", "orange"))
            self.current_db_path = None

        try:
            self._initialize_verification_report()
            self.app_ref.gui_queue.put(('scheduler_log', f"  Informe de verificación (.csv) inicializado.\n", "gray"))
        except Exception as e:
            self.app_ref.gui_queue.put(('scheduler_log', f"❌ Error al inicializar informe CSV: {e}\n", "orange"))
            self.verification_report_file = None

        # Ejecutamos el hilo 
        threading.Thread(target=self._execute_next_task, daemon=True).start()
        
    def _stop_task_sequence(self):
        """Establece la señal para detener la ejecución de la secuencia."""
        if self.app_ref.is_main_task_running:
            self.stop_sequence_flag.set()
            self.app_ref.gui_queue.put(('scheduler_log', "Señal de detención enviada... Finalizando tarea actual.\n", "orange"))
            
            
    def _execute_next_task(self, sequence_failed=False):
        """
        Función recursiva/iterativa que se ejecuta en el hilo.
        Ejecuta una tarea y luego se llama a sí misma para la siguiente.
        """
        
        # *** CONDICIONES DE PARADA (depende de lo que se asignó y lo que pasó en el bucle anterior) ***
        # Si la secuencia falló y la tarea anterior tenia que detenerla
        if sequence_failed:
            self.app_ref.gui_queue.put(('scheduler_log', "Secuencia detenida debido a un error.\n", "red"))
            self._consolidate_reports(sequence_failed=True)
            return # Terminamos el hilo

        # Si se presionó el botón de Stop
        if self.stop_sequence_flag.is_set():
            self.app_ref.gui_queue.put(('scheduler_log', "⏹️ Secuencia detenida por el usuario.\n", "orange"))
            self._consolidate_reports(sequence_failed=True) # Consideramos 'fallida' si se detiene
            return # Termina el hilo

        # Si hemos completado todas las tareas :)
        self.current_task_index += 1    # Recordemos que el indice estaba inicializado a -1! 
        if self.current_task_index >= len(self.app_ref.task_sequence):
            self.app_ref.gui_queue.put(('scheduler_log', "✅ Secuencia completada.\n", "green"))
            self._consolidate_reports(sequence_failed=False)
            return # Salimos del bucle y el hilo termina. Ya no seguimos con el resto del bucle.

        # *** OBTENER Y EJECUTAR TAREA ACTUAL ***
        task = self.app_ref.task_sequence[self.current_task_index]
        task_num = self.current_task_index + 1
        total_tasks = len(self.app_ref.task_sequence)
        
        # Modificamos el nombre para el log, quitando el prefijo de guiones si existe
        log_name = task['name'].lstrip(" -")
        log_msg = f"--- (Tarea {task_num}/{total_tasks}) {log_name} ---\n"
        self.app_ref.gui_queue.put(('scheduler_log', log_msg, "white"))

        # *** LOGIC***
        oid_to_check = None 
        verification_result = "N/A"
        found_evidence = []
        # all_received = []   # Ya no lo usaremos aqui..
        # Inicializamos las variables antes de comenzar a ejecutar la tarea
        task_failed = False
        result_code = 0 # (PASS)        
        try:
            if task['type'] == "Ejecutar Test":
                # CUidado! Ya no usamos self.app_ref.active_session_id!
                session_to_run = task['session_id']
                # *******************************************
                
                if not session_to_run or not self.app_ref.sessions[session_to_run]['process']:  # SI la tarea no tiene asignada una sesión o la sesión que esta asignada a la tarea no está activa.
                    raise RuntimeError(f"Sesión {session_to_run} (requerida por la tarea) no está conectada.")

                output_file = f"output_task_{self.current_task_index}.xml"
                self.task_output_files.append(os.path.join("test_results", output_file))
                
                # Nombre limpio del test para buscar en el mapa
                clean_test_name = task['name'].split(" (Sesión:")[0].lstrip(" -")   # Solo queremos quedarnos con el nombre del test!

                # Creamos el callback para esta sesión específica. Esto lo hacemos para poder actualizar las secciones de la GUI correspondientes a la hora de ejecutar tests.
                on_success_callback = self.app_ref._create_gui_update_callback(
                    session_to_run,
                    *self.app_ref.test_gui_update_map.get(clean_test_name, (None, []))  # Buscamos el nombre del test de la tarea en el mapa. Si lo encuentra, nos devuelve una tupla! -> ('modules_display', ['modules']). 
                                                                                        # SI no lo encontrara en el mapa (porque sea un test que no actualiza la GUI), nos daría el valor por defecto de la tupla vacía: (None, [])                                         
                                                                                        #  Para separar la tupla, separamos en elemenetos con el *
                )

                result_code = robot_executor._run_robot_test(
                    app_ref=self.app_ref,
                    test_name=clean_test_name,
                    session_id=session_to_run, 
                    variables=task['vars'].split(),
                    on_success=on_success_callback,
                    preferred_filename=task['file'],
                    output_filename=output_file,
                    log_file=f"log_task_{self.current_task_index}.html",
                    report_file=f"report_task_{self.current_task_index}.html",
                    suppress_gui_updates=True, # No queremos status "PASS/FAIL" por cada test, ya que al final obtendremos el informe
                    block=True
                )
                if result_code != 0:
                    task_failed = True  # Despues de ejecutar el test (al final de este método/hilo), en caso de que haya fallado, se valorará en funcion de lo que esta tarea tenga asignado en task['on_fail'] si detener toda la secuencia


            elif task['type'] == "Pausa (segundos)":
                duration = task['param']
                self.app_ref.gui_queue.put(('scheduler_log', f" Iniciando pausa de {duration}s...\n", "gray"))
                # Hacemos la pausa en incrementos de 1s para poder cancelarla
                for _ in range(duration):
                    if self.stop_sequence_flag.is_set():
                        break # tenemos que permitir salir de la pausa en caso de que se quiera detener la secuencia
                    time.sleep(1)   # Para no sobrecargar la cpu
                
                if not self.stop_sequence_flag.is_set():
                    self.app_ref.gui_queue.put(('scheduler_log', f" Pausa finalizada.\n", "gray"))
            
            elif task['type'] == "Verificar Traps SNMP Nuevos":
                session_id = task.get('session_id', 'A') # Obtener sesión, por defecto 'A'
                
                if not self.app_ref.trap_listener_controller.is_listener_running(session_id):
                     raise RuntimeError(f"El Listener SNMP para la Sesión {session_id} no está iniciado.")
                
                # Aquí recuperamos el OID que guardamos.
                oid_to_check = task['param'] 
                
                if oid_to_check:
                    self.app_ref.gui_queue.put(('scheduler_log', f" Buscando (Sesión {session_id}) trap específico con OID: {oid_to_check}...\n", "gray"))
                else:
                    self.app_ref.gui_queue.put(('scheduler_log', f" Buscando (Sesión {session_id}) traps nuevos (genérico)...\n", "gray"))

                # Llamada a check_and_clear_new_traps. Nos devuelve en "success": '1' si le llegaron traps. '0' si no llegaron. En "found_traps" nos devolvera todos los traps encontrados en caso de no haber proporcionado un OID. 
                # En caso de proporcionar un OID nos devolverá el trap que coincide con el del OID.
                verification_success, found_evidence = self.app_ref.trap_listener_controller.check_traps_without_clearing(session_id, oid_to_check)
                
# *********************************************************************************************
            # YA NO HACEMOS USO DE ESTO PORQUE LOS DATOS DE LA DB LOS GUARDAREMOS SOLO CUANDO UTILICEMOS LA TAREA Limpiar Buffer de Traps
                # Si encontramos traps Y tenemos una DB abierta, los guardamos
                # if all_received and self.current_db_path:
                #     try:
                #         db_handler.save_traps_to_db(self.app_ref, all_received, self.current_db_path)
                #         self.app_ref.gui_queue.put(('scheduler_log', f"  {len(found_evidence)} traps guardados en {os.path.basename(self.current_db_path)}.\n", "gray"))
                #     except Exception as e:
                #         self.app_ref.gui_queue.put(('scheduler_log', f"  Error guardando traps en DB: {e}\n", "orange"))
# *********************************************************************************************

                if not verification_success:
                    msg = f"FALLÓ: No se recibieron traps"
                    if oid_to_check:    # Si no se encuentran traps, pero nos habían pasado un OID
                        msg += f" con OID {oid_to_check}.\n"
                    else: # Si no se encuentran traps y tampoco nos pasaban OID
                        msg += " nuevos.\n"
                    self.app_ref.gui_queue.put(('scheduler_log', f"❌ {msg}", "red"))
                    task_failed = True
                    verification_result = "FAILED"
                else:
                    msg = f"ÉXITO: Se recibieron traps"
                    if oid_to_check:
                        msg += f" (verificado OID {oid_to_check}).\n" # (Esto es una suposición)
                    else:
                        msg += " nuevos.\n"
                    self.app_ref.gui_queue.put(('scheduler_log', f"✔ {msg}", "green")) # Color cambiado a verde
                    verification_result = "VERIFIED"
                
            elif task['type'] == "Limpiar Buffer de Traps":
                session_id = task.get('session_id', 'A')
                self.app_ref.gui_queue.put(('scheduler_log', f" Limpiando buffer de traps (Sesión {session_id})...\n", "gray"))
                
                if not self.app_ref.trap_listener_controller.is_listener_running(session_id):
                     raise RuntimeError(f"El Listener SNMP para la Sesión {session_id} no está iniciado.")

                # Limpiamos datos y obtenemos traps
                traps_to_save = self.app_ref.trap_listener_controller.clear_traps_buffer(session_id)
                
                # Los guardamos en la DB
                if traps_to_save and self.current_db_path:
                    try:
                        db_handler.save_traps_to_db(self.app_ref, traps_to_save, self.current_db_path)
                        self.app_ref.gui_queue.put(('scheduler_log', f"  {len(traps_to_save)} traps guardados en {os.path.basename(self.current_db_path)}.\n", "gray"))
                    except Exception as e:
                        self.app_ref.gui_queue.put(('scheduler_log', f"  Error guardando traps en DB: {e}\n", "orange"))
                elif traps_to_save:
                     self.app_ref.gui_queue.put(('scheduler_log', "  No se configuró una DB, traps borrados sin guardar.\n", "orange"))
                else:
                    self.app_ref.gui_queue.put(('scheduler_log', "  Buffer ya estaba vacío.\n", "gray"))
                
                verification_result = "N/A"
        except Exception as e:
            self.app_ref.gui_queue.put(('scheduler_log', f"❌ Error fatal en la tarea: {e}\n", "red"))
            task_failed = True
            verification_result = "ERROR"
        
        
        if task['type'] == "Verificar Traps SNMP Nuevos":
            self._log_verification_result(task['name'], oid_to_check, verification_result, found_evidence)

        # *** Decidir si continuar ***
        should_stop = task_failed and (task['on_fail'] == "Detener secuencia")  # Solo pararemos la secuencia en el caso de que el test que haya fallado tenga asignado en el on_fail que así sea
        
        # Llamada recursiva para la siguiente tarea
        self._execute_next_task(sequence_failed=should_stop)           

    
    def _initialize_verification_report(self):
        """Crea o sobrescribe el CSV de verificación y escribe la cabecera."""
        report_dir = "test_results"
        self.verification_report_file = os.path.join(report_dir, "verification_report.csv")

        # Nos aseguramos de que el directorio existe
        os.makedirs(report_dir, exist_ok=True)
        
        with open(self.verification_report_file, 'w', newline='', encoding='utf-8') as f:   # usamos 'w' para sobrescribir el archivo en cada nueva ejecución
            writer = csv.writer(f)
            writer.writerow(["Timestamp", "TaskName", "ExpectedOID", "Result", "Evidence"]) # Inicalizamos el CSV con los siguientes campos



    def _log_verification_result(self, task_name, oid, result, evidence_list): 
        """Añade una fila al CSV de verificación único."""
        if not self.verification_report_file:
            self.app_ref.gui_queue.put(('scheduler_log', f"Error: no se pudo inicializar el informe CSV.\n", "red"))
            return # No hacemos nada si no hay archivo inicializado.
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        evidence_str = ""
        
        try:            
            # Convertir la lista de traps ("Evidence") a un string JSON para que sea mas facil de leer
            evidence_str = json.dumps(evidence_list)
        except Exception:
            evidence_str = str(evidence_list)
            
        try:
            with open(self.verification_report_file, 'a', newline='', encoding='utf-8') as f:   # Usamos 'a' para añadirla al final del archivo
                writer = csv.writer(f)
                writer.writerow([timestamp, task_name, str(oid) if oid else "N/A", result, evidence_str])
        except Exception as e:
            self.app_ref.gui_queue.put(('scheduler_log', f"❌ Error al escribir en el informe CSV: {e}\n", "red"))




    def _consolidate_reports(self, sequence_failed):
        """
        Se llama al final de la secuencia (éxito, fallo o stop).
        Genera un informe consolidado. Es el paso final en la ejecución de una secuencia (independientmente de que falle o se ejecute con exito)
        """
        try:
            if not self.task_output_files:
                self.app_ref.gui_queue.put(('scheduler_log', "No se generaron informes de tests para consolidar.\n", "gray"))   # Seria raro encontrarnos con este caso. Significaría que tendriamos que valorar alguna condicion mas de error en el bucle recurrente del metodo _execute_next_task
            else:
                self.app_ref.gui_queue.put(('scheduler_log', " Generando informe consolidado...\n", "cyan"))
                
                # Limpiamos informes antiguos
                if os.path.exists("test_results/report_consolidado.html"):
                    os.remove("test_results/report_consolidado.html")
                if os.path.exists("test_results/log_consolidado.html"):
                    os.remove("test_results/log_consolidado.html")

                # Construimos el comando para 'rebot'
                command = [
                    sys.executable, '-m', 'robot.rebot',
                    '--outputdir', 'test_results',
                    '--output', 'output_consolidado.xml',
                    '--log', 'log_consolidado.html',
                    '--report', 'report_consolidado.html',
                    '--name', 'Secuencia de Pruebas'
                ] + self.task_output_files # Añadimos todos los output.xml

                result = subprocess.run(
                    command, 
                    capture_output=True, 
                    text=True, 
                    timeout=30,
                    encoding='utf-8' # Asegurar encoding
                )

                if result.returncode == 0:
                    self.app_ref.gui_queue.put(('scheduler_log', "✔ Informe consolidado creado.\n", "green"))
                else:
                    error_output = result.stderr or result.stdout
                    self.app_ref.gui_queue.put(('scheduler_log', f"❌ Error al generar informe: {error_output}\n", "red"))

        except subprocess.TimeoutExpired:   # Debido al timeout del suboprocess de result
            self.app_ref.gui_queue.put(('scheduler_log', "❌ Error: La generación del informe tardó demasiado.\n", "red"))
        except Exception as e:  # Cualquier otro error que no sea de timeout
            self.app_ref.gui_queue.put(('scheduler_log', f"❌ Error inesperado al generar informe: {e}\n", "red"))

        # *** Restaurar GUI (SIEMPRE se ejecuta) ***
        final_message = "Secuencia completada con errores." if sequence_failed else "Secuencia completada con éxito."
        final_color = "red" if sequence_failed else "green"
        self.app_ref.gui_queue.put(('main_status', final_message, final_color))
        
        if self.verification_report_file and os.path.exists(self.verification_report_file):
            self.app_ref.gui_queue.put(('scheduler_log', f"✔ Informe de verificación guardado en: {self.verification_report_file}\n", "green"))
            
        self.app_ref.gui_queue.put(('enable_buttons', None)) # Rehabilitamos botones
        self.app_ref.is_main_task_running = False
        self.stop_sequence_flag.clear()
        self.current_task_index = -1    # Volvemos a inicializar la variable indice de las tareas
        self.task_output_files = []
        
        self.current_db_path = None